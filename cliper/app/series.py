from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from . import models
from .database import (
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


@router.get("/by_title", response_model=models.FullSeries)
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
