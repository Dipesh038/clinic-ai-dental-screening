import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import close_client, get_client

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = get_client()
    await client.admin.command("ping")
    logger.info("MongoDB Atlas connection established")
    yield
    close_client()


app = FastAPI(title="Clinic-Specific AI Dental Screening API", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
