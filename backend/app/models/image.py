from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ImageOut(BaseModel):
    id: str
    visit_id: str
    image_url: str
    top_prediction: str | None = None
    reviewed_at: datetime | None = None
