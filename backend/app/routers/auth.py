# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, Response, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from app.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from app.config import settings
from app.db import get_database
from app.dependencies import CurrentUser, get_current_user
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
    # bcrypt is deliberately CPU-expensive; on the free tier's slow shared CPU
    # it dominates login time. Run it off the event loop so one login doesn't
    # stall every other in-flight request.
    password_ok = user is not None and await run_in_threadpool(
        verify_password, credentials.password, user["password_hash"]
    )
    if not password_ok:
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
        samesite="none" if settings.cookie_secure else "lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return LoginResponse(username=user["username"], role=user["role"])


@router.get("/me", response_model=LoginResponse)
async def me(current_user: CurrentUser = Depends(get_current_user)) -> LoginResponse:
    return LoginResponse(username=current_user.username, role=current_user.role)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    response.delete_cookie(
        key="access_token",
        samesite="none" if settings.cookie_secure else "lax",
        secure=settings.cookie_secure,
    )
