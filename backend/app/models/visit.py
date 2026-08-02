from __future__ import annotations

from datetime import date as date_

from pydantic import BaseModel, Field


class VisitCreate(BaseModel):
    date: date_
    complaint: str = Field(min_length=1, max_length=500)
    notes: str = ""


class VisitUpdate(BaseModel):
    date: date_ | None = None
    complaint: str | None = Field(default=None, min_length=1, max_length=500)
    notes: str | None = None


class VisitOut(BaseModel):
    id: str
    patient_id: str
    date: date_
    complaint: str
    notes: str
