from typing import List, Optional
from pydantic import UUID4, BaseModel


class _protoModel(BaseModel):
    id: UUID4
    name: str

    class Config:
        orm_mode = True


class Caption(BaseModel):
    id: UUID4
    text: str
    order: int
    start: float
    stop: float

    class Config:
        orm_mode = True


class ProtoEpisode(_protoModel):
    order: int


class Episode(ProtoEpisode):
    captions: List[Caption]


class ProtoSubSeries(_protoModel):
    order: int


class SubSeries(ProtoSubSeries):
    episodes: List[ProtoEpisode]


class Series(_protoModel):
    subseries: List[ProtoSubSeries]


class FullSeries(_protoModel):
    subseries: List[SubSeries]
