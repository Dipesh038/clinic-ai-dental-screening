from fastapi import APIRouter, Depends, HTTPException, Response, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from app.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from app.config import settings
from app.db import get_database
from app.security import verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    username: str
    role: str


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    response: Response,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> LoginResponse:
    user = await db.users.find_one({"username": credentials.username})
    if user is None or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_access_token(username=user["username"], role=user["role"])
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return LoginResponse(username=user["username"], role=user["role"])
