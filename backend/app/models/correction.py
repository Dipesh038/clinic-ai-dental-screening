from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.prediction import BoundingBox


class CorrectionItem(BaseModel):
    class_id: int
    disease_name: str
    box: BoundingBox


class CorrectionIn(BaseModel):
    corrections: list[CorrectionItem]


class CorrectionOut(BaseModel):
    id: str
    image_id: str
    corrections: list[CorrectionItem]
    created_at: datetime
