from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, Depends, Response
import ffmpeg
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .elasticsearch import get_elastic

from app.utils import run_ffmpeg_async

from .database import Episode, get_async_db, AsyncSession

from . import models

router = APIRouter()

@router.get("/get/{episode_uuid}", response_model=models.Episode)
async def get_episode_by_uuid(
    episode_uuid: str,
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

@router.get("/search/{episode_uuid}", response_model=models.Episode)
async def search_episode_by_uuid(
    episode_uuid: str,
    search_term: str,
    session: AsyncSession = Depends(get_async_db),
    es: AsyncElasticsearch = Depends(get_elastic),
):
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
    results = await es.search(
        index=episode.subseries.series.id,
        query={
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": episode.id,
                            "fields": ["episode"],
                        },
                    },
                    {
                        "multi_match": {
                            "query": search_term,
                            "fields": ["text"],
                        },
                    },
                ]
            },
        },
    )
    result_ids = list(
        result["_source"]["id"] for result in results["hits"]["hits"]
    )
    return models.Episode(
        id=episode.id,
        name=episode.name,
        order=episode.order,
        captions=list(
            models.Caption(
                id=caption.id,
                text=caption.text,
                order=caption.order,
                start=caption.start,
                stop=caption.stop,
            )
            for caption in episode.captions
            if caption.id.__str__() in result_ids
        ),
    )


@router.get("/thumb/{episode_uuid}")
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
    a_random_caption = episode.captions[len(episode.captions) // 6]
    a_random_time = (a_random_caption.start + a_random_caption.stop) / 2
    thumb, _ = await run_ffmpeg_async(
        ffmpeg.input(episode.path, ss=f"{a_random_time}")
        .filter("scale", 240, -1)
        .output("pipe:", vframes=1, f="image2", **{"c:v": "mjpeg"})
    )
    return Response(content=thumb, media_type="image/jpeg")
