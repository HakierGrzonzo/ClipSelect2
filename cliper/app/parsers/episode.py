from typing import Dict, Tuple
import xml.etree.ElementTree as ET

from app.subparser import parse_srt_string

from ..utils import run_ffmpeg_async
from ..database import Caption, Episode
import ffmpeg


def unformat_timestamp(subtitle_timestamp: Tuple[int, int, int, int]) -> float:
    hours, minutes, seconds, miliseconds = subtitle_timestamp
    return 60 * ((60 * hours) + minutes) + seconds + (miliseconds / 1000)


def rate_stream(stream: Dict) -> int:
    criteria = [
        lambda d: -1 if d["disposition"]["hearing_impaired"] else 0,
        lambda d: -2 if d["disposition"]["visual_impaired"] else 0,
        lambda d: -80 if "songs" in d["tags"].get("title", "").lower() else 0,
        lambda d: -80 if "sign" in d["tags"].get("title", "").lower() else 0,
    ]
    return sum([c(stream) for c in criteria])


def parse_episode_from_nfo(content: str):
    xml = ET.fromstring(content)
    try:
        return {
            "name": xml.find("title").text,
            "order": int(xml.find("episode").text),
        }
    except:
        raise Exception(content)


async def parse_episode_into_clips(episode_data: Dict) -> Episode:
    probed = ffmpeg.probe(episode_data["path"])
    subtitles = list(
        stream
        for stream in probed["streams"]
        if stream["codec_type"] == "subtitle"
        and stream["tags"].get("language") == "eng"
        and stream["codec_name"] != "hdmv_pgs_subtitle"
    )
    print("parsing subs")
    if len(subtitles) < 1:
        raise Exception(f"No subtitles found! {episode_data['path']}")
    best_subs = sorted(subtitles, key=lambda v: rate_stream(v))[0]
    raw_subs, _ = await run_ffmpeg_async(
        ffmpeg.input(episode_data["path"])[f'{best_subs["index"]}'].output(
            "pipe:", f="srt"
        )
    )
    parsed_subtitels = parse_srt_string(raw_subs.decode())
    print(f"Parsed subtitles for {episode_data['name']}")
    return Episode(
        name=episode_data["name"],
        order=episode_data["order"],
        path=episode_data["path"],
        subtitle_track_index=best_subs["index"],
        captions=list(
            Caption(order=i, **subtitle.dict())
            for i, subtitle in enumerate(parsed_subtitels)
        ),
    )
