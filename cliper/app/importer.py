from elasticsearch import AsyncElasticsearch
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.elasticsearch import enroll_series_in_elastic, get_elastic
from .database import (
    Series,
    get_async_db,
)
from fastapi import APIRouter, Depends

from app.parsers.walker import walk_series

router = APIRouter()


@router.get("/register")
async def add_new_series(
    path: str,
    session: AsyncSession = Depends(get_async_db),
    es: AsyncElasticsearch = Depends(get_elastic),
):
    try:
        series = await walk_series(path)
        session.add(series)
        await session.flush()
        series = await session.get(Series, series.id)
        await enroll_series_in_elastic(series, es)
        return f'Added series "{series.id}"'
    finally:
        await session.commit()


@router.delete("/all")
async def drop_all_series(session: AsyncSession = Depends(get_async_db)):
    try:
        await session.execute(delete(Series))
        return f"Droped all series!"
    finally:
        await session.commit()
