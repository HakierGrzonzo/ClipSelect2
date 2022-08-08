from uuid import uuid4
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

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
