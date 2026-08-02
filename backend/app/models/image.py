from __future__ import annotations

from pydantic import BaseModel


class ImageOut(BaseModel):
    id: str
    visit_id: str
    image_url: str
    top_prediction: str | None = None
