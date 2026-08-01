from enum import Enum

from pydantic import BaseModel, Field


class Role(str, Enum):
    DENTIST = "dentist"
    RECEPTIONIST = "receptionist"
    ADMIN = "admin"


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    role: Role


class UserInDB(BaseModel):
    username: str
    password_hash: str
    role: Role


class UserOut(BaseModel):
    username: str
    role: Role
