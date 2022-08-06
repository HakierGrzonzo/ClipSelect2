from typing import List
from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from . import models
from .database import Series, SubSeries, SessionLocal, engine, Base


app = FastAPI(title="A cliper microservice for ClipSelect2")


@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_series_from_db(session: AsyncSession):
    return (await session.execute(select(Series))).unique().scalars()


@app.get("/series/", response_model=List[models.Series])
async def get_series(session: AsyncSession = Depends(get_async_db)):
    series = (await get_series_from_db(session)).all()
    return series


@app.post("/series/add_mock")
async def add_mock_series(session: AsyncSession = Depends(get_async_db)):
    series = (await get_series_from_db(session)).all()
    session.add(Series(name=f"A new exciting series no. {len(series)}"))
    await session.commit()


@app.post("/subseries/add_mock")
async def add_mock_subseries(session: AsyncSession = Depends(get_async_db)):
    series = (await get_series_from_db(session)).one()
    session.add(
        SubSeries(series_id=series.id, name=f"Season {len(series.subseries)}")
    )
    await session.commit()
