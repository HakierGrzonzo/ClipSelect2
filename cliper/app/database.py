from typing import AsyncGenerator
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Float,
)
from sqlalchemy.ext.declarative import DeclarativeMeta

from os import environ

from sqlalchemy.sql.schema import Column

DATABASE_URL = environ.get("DATABASE", "sqlite+aiosqlite:///./test.db")

engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base: DeclarativeMeta = declarative_base()


class Series(Base):
    __tablename__ = "Series"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(128), nullable=False, index=True)
    subseries = relationship(
        "SubSeries",
        lazy="raise",
        back_populates="series",
        passive_deletes=True,
    )

    __mapper_args__ = {"eager_defaults": True}


class SubSeries(Base):
    __tablename__ = "SubSeries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    series_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Series.id", use_alter=True, ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    order = Column(Integer())

    name = Column(String(128), nullable=False, index=True)

    series = relationship("Series", lazy="joined", back_populates="subseries")
    episodes = relationship(
        "Episode",
        lazy="raise",
        back_populates="subseries",
        passive_deletes=True,
    )

    __mapper_args__ = {"eager_defaults": True}


class Episode(Base):
    __tablename__ = "Episode"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    subseries_id = Column(
        UUID(as_uuid=True),
        ForeignKey("SubSeries.id", use_alter=True, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    order = Column(Integer())
    name = Column(String(128), nullable=False, index=True)
    path = Column(String(256), nullable=False)

    subseries = relationship(
        "SubSeries", lazy="joined", back_populates="episodes"
    )
    captions = relationship(
        "Caption",
        lazy="raise",
        back_populates="episode",
        passive_deletes=True,
    )

    subtitle_track_index = Column(Integer(), nullable=False)

    __mapper_args__ = {"eager_defaults": True}


class Caption(Base):
    __tablename__ = "Caption"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    episode_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Episode.id", use_alter=True, ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    episode = relationship("Episode", lazy="joined", back_populates="captions")

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
