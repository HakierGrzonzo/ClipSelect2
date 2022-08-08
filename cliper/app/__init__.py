from fastapi import FastAPI
from .series import router as series_router
from .importer import router as import_router

from .database import (
    engine,
    Base,
)

app = FastAPI(title="A cliper microservice for ClipSelect2")


@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(series_router, prefix="/series", tags=["series", "data"])
app.include_router(import_router, prefix="/import", tags=["internal", "data"])
