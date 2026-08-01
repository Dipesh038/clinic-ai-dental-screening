from fastapi import Cookie, Depends, HTTPException, status
from jose import JWTError
from pydantic import BaseModel

from app.auth import decode_access_token
from app.models.user import Role


class CurrentUser(BaseModel):
    username: str
    role: Role


async def get_current_user(access_token: str | None = Cookie(default=None)) -> CurrentUser:
    if access_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_access_token(access_token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )
    return CurrentUser(username=payload["sub"], role=payload["role"])


def require_role(*allowed_roles: Role):
    async def checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return current_user

    return checker
