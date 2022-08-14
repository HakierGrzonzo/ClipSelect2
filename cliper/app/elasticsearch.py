from typing import AsyncGenerator
from app.utils import prev_current_next
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_streaming_bulk

from .database import Series


async def get_elastic() -> AsyncGenerator[AsyncElasticsearch, None]:
    connection = AsyncElasticsearch(hosts=["http://localhost:9200"])
    yield connection
    await connection.close()


async def enroll_series_in_elastic(series: Series, es: AsyncElasticsearch):
    # if index exists, remove it
    if await es.indices.exists(index=series.id):
        await es.indices.delete(index=series.id)

    await es.indices.create(index=series.id)
    async for _ in async_streaming_bulk(
        client=es,
        index=series.id,
        actions=[
            {
                "text": caption.text,
                "previous": previous.text if previous else None,
                "next": next.text if next else None,
                "id": caption.id,
                "episode": episode.id,
                "subseries": subseries.id,
                "series": series.id,
            }
            for subseries in series.subseries
            for episode in subseries.episodes
            for previous, caption, next in prev_current_next(episode.captions)
        ],
    ):
        pass
