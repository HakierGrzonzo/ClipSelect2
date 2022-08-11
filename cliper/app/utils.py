from typing import Dict
from asyncio import create_subprocess_exec, subprocess
from tempfile import NamedTemporaryFile
from typing import Tuple
import ffmpeg

from .database import Caption


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
    "webm": {"f": "webm", "c:v": "vp9", "b:v": "750k", "c:a": "libvorbis"},
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