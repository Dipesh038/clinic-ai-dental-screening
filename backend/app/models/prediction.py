from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class DetectionOut(BaseModel):
    class_id: int
    disease_name: str
    confidence: float = Field(ge=0, le=1)
    box: BoundingBox


class PredictionOut(BaseModel):
    id: str
    image_id: str
    detections: list[DetectionOut]
    latency_ms: int
    created_at: datetime
