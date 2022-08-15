from typing import final
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tempfile import NamedTemporaryFile
import ffmpeg

from .cache import cache, cache_streaming

from .database import Caption, get_async_db
from .utils import (
    filter_gif_caption,
    filter_webm_caption,
    run_ffmpeg_async,
    run_ffmpeg_generator,
)

router = APIRouter()


@router.get("/simple")
@cache_streaming()
async def get_simple_caption(
    clip_uuid: str,
    format: str = "webm",
    session: AsyncSession = Depends(get_async_db),
):
    caption = (
        (await session.execute(select(Caption).filter(Caption.id == clip_uuid)))
        .scalars()
        .one()
    )
    timing = {"ss": f"{caption.start}", "t": f"{caption.stop - caption.start}"}
    temp = NamedTemporaryFile("wb+", suffix=".ass")
    subs, _ = await run_ffmpeg_async(
        ffmpeg.input(caption.episode.path, **timing)[
            str(caption.episode.subtitle_track_index)
        ].output(
            "pipe:",
            f="ass",
        ),
    )
    temp.write(subs)
    temp.flush()
    filters = {
        "webm": filter_webm_caption,
        "gif": filter_gif_caption,
    }

    async def content_generator():
        async for data in run_ffmpeg_generator(
            filters[format](
                ffmpeg.input(
                    caption.episode.path,
                    **timing,
                ),
                temp.name,
                t=timing["t"],
            )
        ):
            yield data
        temp.close()

    mime = {
        "webm": "video/webm",
        "gif": "image/gif",
    }
    return {"Content-type": mime[format]}, content_generator()


@router.get("/multi")
@cache_streaming()
async def get_multi_caption(
    from_clip: str,
    to_clip: str,
    session: AsyncSession = Depends(get_async_db),
):
    captions = (
        (
            await session.execute(
                select(Caption)
                .filter(Caption.id.in_([from_clip, to_clip]))
                .order_by(Caption.order)
            )
        )
        .scalars()
        .all()
    )
    if len(captions) != 2:
        return HTTPException(status_code=400, detail="Caption not found!")
    first_caption, final_caption = captions
    if first_caption.episode.id != final_caption.episode.id:
        return HTTPException(status_code=400)
    timing = {
        "ss": f"{first_caption.start}",
        "t": f"{final_caption.stop - first_caption.start}",
    }
    temp = NamedTemporaryFile("wb+", suffix=".ass")
    subs, _ = await run_ffmpeg_async(
        ffmpeg.input(first_caption.episode.path, **timing)[
            str(first_caption.episode.subtitle_track_index)
        ].output(
            "pipe:",
            f="ass",
        ),
    )
    temp.write(subs)
    temp.flush()

    async def content_generator():
        async for data in run_ffmpeg_generator(
            filter_webm_caption(
                ffmpeg.input(
                    first_caption.episode.path,
                    **timing,
                ),
                temp.name,
                t=timing["t"],
            )
        ):
            yield data
        temp.close()
    return {"Content-type": "video/webm"}, content_generator()
