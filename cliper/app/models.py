from typing import List
from pydantic import BaseModel


class _protoModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class Caption(BaseModel):
    id: int
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


class FullSubSeries(_protoModel):
    episodes: List[Episode]


class Series(_protoModel):
    subseries: List[ProtoSubSeries]


class FullSeries(_protoModel):
    subseries: List[SubSeries]


class CaptionSeries(_protoModel):
    subseries: List[FullSubSeries]
