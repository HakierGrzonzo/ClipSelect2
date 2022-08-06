from typing import List
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


class Episode(_protoModel):
    pass


class SubSeries(_protoModel):
    episodes: List[Episode] = []


class Series(_protoModel):
    subseries: List[SubSeries] = []
