from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class PatientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    dob: date
    gender: Gender
    contact: str = Field(min_length=1, max_length=100)
    notes: str = ""


class PatientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    dob: date | None = None
    gender: Gender | None = None
    contact: str | None = Field(default=None, min_length=1, max_length=100)
    notes: str | None = None


class PatientOut(BaseModel):
    id: str
    name: str
    dob: date
    gender: Gender
    contact: str
    notes: str
