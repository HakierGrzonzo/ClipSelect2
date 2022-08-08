from fastapi import FastAPI
from .series import router as series_router
from .episodes import router as episode_router
from .importer import router as import_router

from .database import (
    engine,
    Base,
)

app = FastAPI(
    title="A cliper microservice for ClipSelect2",
    openapi_prefix="http://localhost:8000/",
)


@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(series_router, prefix="/series", tags=["series", "data"])
app.include_router(episode_router, prefix="/episode", tags=["episode", "data"])
app.include_router(import_router, prefix="/import", tags=["internal"])
