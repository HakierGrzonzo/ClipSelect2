from typing import AsyncGenerator
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    DateTime,
    Float,
    create_engine,
)
from sqlalchemy.ext.declarative import DeclarativeMeta

from os import environ

from sqlalchemy.sql.schema import Column

DATABASE_URL = environ.get("DATABASE", "sqlite+aiosqlite:///./test.db")

engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    autocommit=False, class_=AsyncSession, autoflush=False, bind=engine
)

Base: DeclarativeMeta = declarative_base()


class Series(Base):
    __tablename__ = "Series"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(128), nullable=False, index=True)
    subseries = relationship(
        "SubSeries", back_populates="series", lazy="joined"
    )


class SubSeries(Base):
    __tablename__ = "SubSeries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    series_id = Column(
        UUID(as_uuid=True), ForeignKey("Series.id", use_alter=True), index=True
    )
    series = relationship("Series", back_populates="subseries", lazy="joined")

    name = Column(String(128), nullable=False, index=True)

    episodes = relationship(
        "Episode", back_populates="subseries", lazy="joined"
    )


class Episode(Base):
    __tablename__ = "Episode"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    subseries_id = Column(
        UUID(as_uuid=True),
        ForeignKey("SubSeries.id", use_alter=True),
        index=True,
    )
    subseries = relationship(
        "SubSeries", back_populates="episodes", lazy="joined"
    )

    name = Column(String(128), nullable=False, index=True)

    captions = relationship("Caption", back_populates="episode", lazy="joined")


class Caption(Base):
    __tablename__ = "Caption"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    episode_id = Column(
        UUID(as_uuid=True), ForeignKey("Episode.id", use_alter=True), index=True
    )
    episode = relationship("Episode", back_populates="captions", lazy="joined")

    # The content of the subtitles for the caption
    text = Column(String(256), nullable=False)

    # The order the caption apprears in
    order = Column(Integer())

    # start/end of caption in seconds
    start = Column(Float())
    stop = Column(Float())


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
