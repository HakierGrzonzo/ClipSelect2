from uuid import uuid4
from fastapi import APIRouter, Depends, Response
import ffmpeg
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.utils import run_ffmpeg_async

from .database import Caption, Episode, get_async_db, AsyncSession

from . import models

router = APIRouter()


@router.get("/", response_model=models.Episode)
async def get_episode_by_uuid(
    episode_uuid: str,
    search_term: str,
    session: AsyncSession = Depends(get_async_db),
):
    return (
        (
            await session.execute(
                select(Episode)
                .filter(Episode.id == episode_uuid)
                .options(selectinload(Episode.captions))
            )
        )
        .scalars()
        .one()
    )


@router.get("/{episode_uuid}")
async def get_thumbnail_for_episode(
    episode_uuid: str,
    session: AsyncSession = Depends(get_async_db),
) -> Response:
    episode = (
        (
            await session.execute(
                select(Episode)
                .filter(Episode.id == episode_uuid)
                .options(selectinload(Episode.captions))
            )
        )
        .scalars()
        .one()
    )
    a_random_caption = episode.captions[len(episode.captions) // 2]
    a_random_time = (a_random_caption.start + a_random_caption.stop) / 4
    thumb, _ = await run_ffmpeg_async(
        ffmpeg.input(episode.path, ss=f"{a_random_time}")
        .filter("scale", 240, -1)
        .output("pipe:", f="image2", vframes=1, **{"c:v": "webp"})
    )
    return Response(content=thumb, media_type="image/webp")
