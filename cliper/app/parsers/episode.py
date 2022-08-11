from typing import Dict, Tuple
import xml.etree.ElementTree as ET

from ..utils import run_ffmpeg_async
from ..database import Caption, Episode
from subtitle_parser import SrtParser
from tempfile import NamedTemporaryFile
import ffmpeg


def unformat_timestamp(subtitle_timestamp: Tuple[int, int, int, int]) -> float:
    hours, minutes, seconds, miliseconds = subtitle_timestamp
    return 60 * ((60 * hours) + minutes) + seconds + (miliseconds / 1000)


def rate_disposition(disposition: Dict) -> int:
    criteria = [
        lambda d: -1 if d["hearing_impaired"] else 0,
        lambda d: -2 if d["visual_impaired"] else 0,
    ]
    return sum([c(disposition) for c in criteria])


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
    )
    if len(subtitles) < 1:
        raise Exception("No subtitles found!")
    best_subs = sorted(
        subtitles, key=lambda v: rate_disposition(v["disposition"])
    )[0]
    with NamedTemporaryFile("w+", suffix=".srt") as temp:
        raw_subs, _ = await run_ffmpeg_async(
            ffmpeg.input(episode_data["path"])[f'{best_subs["index"]}'].output(
                "pipe:", f="srt"
            )
        )
        temp.write(raw_subs.decode())
        temp.seek(0)
        parser = SrtParser(temp.file)
        parser.parse()
    parser.print_warnings()
    return Episode(
        name=episode_data["name"],
        order=episode_data["order"],
        path=episode_data["path"],
        subtitle_track_index=best_subs["index"],
        captions=list(
            Caption(
                order=i,
                text=subtitle.text.strip(),
                start=unformat_timestamp(subtitle.start),
                stop=unformat_timestamp(subtitle.end),
            )
            for i, subtitle in enumerate(parser.subtitles)
        ),
    )
