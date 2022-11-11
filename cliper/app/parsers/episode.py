from typing import Dict, Tuple
import xml.etree.ElementTree as ET

from app.subparser import parse_srt_string

from ..utils import run_ffmpeg_async
from .utils import get_unique_id
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
        lambda d: 10 if "full" in d["tags"].get("title", "").lower() else 0,
    ]
    return sum([c(stream) for c in criteria])


def rate_audio(stream: Dict) -> int:
    criteria = [
        lambda d: 2 if d["tags"].get("language", "").lower() == "jpn" else 0,
        lambda d: 1 if d["tags"].get("language", "").lower() == "eng" else 0,
        lambda d: -1 if d["tags"].get("language") is None else 0,
    ]
    return sum(
        [c(stream) for c in criteria if print(c(stream), stream) is None]
    )


def parse_episode_from_nfo(content: str):
    xml = ET.fromstring(content)
    try:
        return {
            "name": xml.find("title").text,
            "order": int(xml.find("episode").text),
            "id": get_unique_id(xml),
        }
    except Exception:
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
    audio = list(
        stream
        for stream in probed["streams"]
        if stream["codec_type"] == "audio"
    )
    if len(audio) < 1:
        raise Exception(f"No audio found! {episode_data['path']}")
    if len(subtitles) < 1:
        raise Exception(f"No subtitles found! {episode_data['path']}")
    best_subs = sorted(subtitles, key=lambda v: -rate_stream(v))[0]
    raw_subs, _ = await run_ffmpeg_async(
        ffmpeg.input(episode_data["path"])[f'{best_subs["index"]}'].output(
            "pipe:", f="srt"
        )
    )
    parsed_subtitels = parse_srt_string(raw_subs.decode())
    print(f"Parsed subtitles for {episode_data['name']}")
    return Episode(
        **episode_data,
        subtitle_track_index=best_subs["index"],
        audio_track_index=sorted(audio, key=lambda a: -rate_audio(a))[0][
            "index"
        ],
        captions=list(
            Caption(order=i, **subtitle.dict())
            for i, subtitle in enumerate(parsed_subtitels)
        ),
    )
