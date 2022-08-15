from typing import List
from uuid import UUID
from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.elasticsearch import get_elastic
from app.utils import reduce_captions
from . import models
from .database import (
    Caption,
    Episode,
    Series,
    SubSeries,
    get_async_db,
)

router = APIRouter()


async def get_series_from_db(session: AsyncSession):
    return (
        (
            await session.execute(
                select(Series).options(selectinload(Series.subseries))
            )
        )
        .unique()
        .scalars()
    )


@router.get("/", response_model=List[models.Series])
async def get_series(session: AsyncSession = Depends(get_async_db)):
    series = (await get_series_from_db(session)).all()
    return series


@router.get("/by_title/{title}", response_model=models.FullSeries)
async def get_series_by_title(
    title: str, session: AsyncSession = Depends(get_async_db)
):
    try:
        series = (
            (
                await session.execute(
                    select(Series)
                    .filter(Series.name == title)
                    .options(
                        selectinload(Series.subseries).joinedload(
                            SubSeries.episodes
                        )
                    )
                )
            )
            .scalars()
            .one()
        )
        return series
    except:
        raise HTTPException(status_code=404, detail="Series not found")


@router.get("/search/{title}", response_model=models.CaptionSeries)
async def search_series(
    title: str,
    search_term: str,
    session: AsyncSession = Depends(get_async_db),
    es: AsyncElasticsearch = Depends(get_elastic),
):
    if search_term == "":
        raise HTTPException(status_code=400, detail="No search term")
    try:
        series = (
            (await session.execute(select(Series).filter(Series.name == title)))
            .scalars()
            .one()
        )
        results = await es.search(
            index=series.id,
            size=100,
            query={
                "simple_query_string": {
                    "query": search_term,
                    "analyzer": "english",
                    "default_operator": "and",
                    "fields": ["text^10", "next", "previous"],
                },
            },
        )
        result_ids = list(
            UUID(result["_source"]["id"]) for result in results["hits"]["hits"]
        )
        captions = (
            (
                await session.execute(
                    select(Caption).filter(Caption.id.in_(result_ids))
                )
            )
            .scalars()
            .all()
        )

        return models.CaptionSeries(
            id=series.id, name=series.name, subseries=reduce_captions(captions)
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="Series not found")
