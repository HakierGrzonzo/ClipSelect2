import asyncio
from collections import defaultdict
from typing import Generator, List, TypeVar, AsyncGenerator
from asyncio import create_subprocess_exec, subprocess
from tempfile import NamedTemporaryFile
from typing import Tuple
import ffmpeg

from . import models

from .database import Caption, Episode, Series, SubSeries


async def run_ffmpeg_async(
    ffmpeg_stream, input: None | bytes = None
) -> Tuple[bytes, bytes]:
    """
    Runs ffmpeg expresions from `ffmpeg-python` with asyncio

    ARGS:
        ffmpeg_stream - stream from `ffmpeg-python`
    """
    cmd_line = ffmpeg_stream.compile()
    proc = await create_subprocess_exec(
        cmd_line[0],
        *cmd_line[1:],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
    )
    out, error = await proc.communicate(input)
    if await proc.wait() != 0:
        raise Exception(
            f"Failed to run ffmpeg: {cmd_line}\n\n {error.decode()}"
        )
    return out, error


async def run_ffmpeg_generator(ffmpeg_stream) -> AsyncGenerator[bytes, None]:
    """
    Runs ffmpeg expresions from `ffmpeg-python` with asyncio

    ARGS:
        ffmpeg_stream - stream from `ffmpeg-python`
    """
    cmd_line = ffmpeg_stream.compile()
    proc = await create_subprocess_exec(
        cmd_line[0],
        *cmd_line[1:],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
    )
    while proc.stdout:
        data = await proc.stdout.read(1024)
        if len(data) == 0:
            break
        yield data
    await proc.wait()


async def generate_pallette(caption: Caption):
    temp = NamedTemporaryFile("r+b", suffix=".png")
    _, _ = await run_ffmpeg_async(
        ffmpeg.input(caption.episode.path, ss=f"{caption.start}")
        .video.filter("palettegen")
        .output(
            temp.name,
            t=f"{caption.stop - caption.start}",
        ),
    )
    return temp


FORMATS = {
    "webm": {
        "f": "webm",
        "deadline": 'realtime',
        "row-mt": 1,
        "c:v": "vp8",
        "crf": 20,
        "b:v": "3M",
        "cpu-used": 1, 
        "c:a": "libvorbis",
    },
    "gif": {"r": 10, "f": "gif", "loop": 0, "final_delay": 50},
}


def add_subtitle_filter(stream, subtitle_filename: str):
    return stream.filter(
        "subtitles", filename=subtitle_filename, force_style="Fontsize=24"
    )


def filter_gif_caption(stream, subtitle_filename: str, **output_params):
    pallette_stream = stream.filter("palettegen")
    return ffmpeg.filter(
        [
            add_subtitle_filter(
                stream.filter("scale", -1, 320), subtitle_filename
            ),
            pallette_stream,
        ],
        "paletteuse",
    ).output("pipe:", **output_params, **FORMATS["gif"])


def filter_webm_caption(stream, subtitle_filename: str, **output_params):
    return ffmpeg.output(
        add_subtitle_filter(
            stream.video.filter("scale", -1, 480), subtitle_filename
        ),
        stream.audio,
        "pipe:",
        **output_params,
        **FORMATS["webm"],
    )


def reduce_captions(captions: List[Caption]) -> List[models.FullSubSeries]:
    episodes = defaultdict(lambda: list())
    for caption in captions:
        episodes[caption.episode].append(models.Caption(**caption.__dict__))
    subseries = defaultdict(lambda: list())
    for episode, captions in episodes.items():
        subseries[episode.subseries].append(
            models.Episode(**episode.__dict__, captions=captions)
        )
    return list(
        models.FullSubSeries(**subseries.__dict__, episodes=episodes)
        for subseries, episodes in subseries.items()
    )


T = TypeVar("T")


def prev_current_next(
    iterable: List[T],
) -> Generator[Tuple[T | None, T, T | None], None, None]:
    padded = [None, *iterable, None]
    for i in range(1, len(iterable) + 1):
        yield padded[i - 1], padded[i], padded[i + 1]
