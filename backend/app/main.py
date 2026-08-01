import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import close_client, get_client
from app.routers.auth import router as auth_router

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = get_client()
    await client.admin.command("ping")
    logger.info("MongoDB Atlas connection established")
    yield
    close_client()


app = FastAPI(title="Clinic-Specific AI Dental Screening API", lifespan=lifespan)
app.include_router(auth_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
