from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.ai import load_predictor
from app.db import close_client, ensure_indexes, get_client
from app.routers.auth import router as auth_router
from app.routers.images import router as images_router
from app.routers.patients import router as patients_router
from app.routers.visits import router as visits_router
from app.routers.dashboard import router as dashboard_router

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = get_client()
    await client.admin.command("ping")
    logger.info("MongoDB Atlas connection established")
    await ensure_indexes()
    load_predictor()
    yield
    close_client()


app = FastAPI(title="Clinic-Specific AI Dental Screening API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:3000"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(patients_router)
app.include_router(visits_router)
app.include_router(images_router)
app.include_router(dashboard_router)


@app.get("/health")
def health() -> dict[str, object]:
    return {"status": "ok", "grad_cam_enabled": settings.enable_grad_cam}
