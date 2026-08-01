import pytest
from fastapi import HTTPException

from app.dependencies import CurrentUser, require_role
from app.models.user import Role


async def test_require_role_allows_matching_role():
    checker = require_role(Role.DENTIST, Role.ADMIN)
    user = CurrentUser(username="dr.smith", role=Role.DENTIST)

    result = await checker(current_user=user)

    assert result is user


async def test_require_role_rejects_wrong_role():
    checker = require_role(Role.ADMIN)
    user = CurrentUser(username="reception1", role=Role.RECEPTIONIST)

    with pytest.raises(HTTPException) as exc_info:
        await checker(current_user=user)

    assert exc_info.value.status_code == 403
