import pytest
from httpx import ASGITransport, AsyncClient

from app.db import get_database
from app.main import app
from app.security import hash_password


class FakeUsersCollection:
    def __init__(self, users):
        self._users = users

    async def find_one(self, query):
        return next((u for u in self._users if u["username"] == query["username"]), None)


class FakeDB:
    def __init__(self, users):
        self.users = FakeUsersCollection(users)


@pytest.fixture(autouse=True)
def override_db():
    fake_db = FakeDB(
        [{"username": "dr.smith", "password_hash": hash_password("s3cret-pw"), "role": "dentist"}]
    )
    app.dependency_overrides[get_database] = lambda: fake_db
    yield
    app.dependency_overrides.clear()


async def test_login_with_valid_credentials_sets_cookie():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="https://test") as client:
        response = await client.post(
            "/api/auth/login", json={"username": "dr.smith", "password": "s3cret-pw"}
        )
    assert response.status_code == 200
    assert response.json() == {"username": "dr.smith", "role": "dentist"}
    assert "access_token" in response.cookies


async def test_login_with_wrong_password_returns_401():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="https://test") as client:
        response = await client.post(
            "/api/auth/login", json={"username": "dr.smith", "password": "wrong-pw"}
        )
    assert response.status_code == 401
    assert "access_token" not in response.cookies


async def test_login_with_unknown_username_returns_401():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="https://test") as client:
        response = await client.post(
            "/api/auth/login", json={"username": "nobody", "password": "whatever"}
        )
    assert response.status_code == 401


async def test_me_with_valid_cookie_returns_current_user():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="https://test") as client:
        await client.post("/api/auth/login", json={"username": "dr.smith", "password": "s3cret-pw"})
        response = await client.get("/api/auth/me")
    assert response.status_code == 200
    assert response.json() == {"username": "dr.smith", "role": "dentist"}


async def test_me_without_cookie_returns_401():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="https://test") as client:
        response = await client.get("/api/auth/me")
    assert response.status_code == 401


async def test_logout_clears_cookie_and_deauthenticates():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="https://test") as client:
        await client.post("/api/auth/login", json={"username": "dr.smith", "password": "s3cret-pw"})
        logout_response = await client.post("/api/auth/logout")
        me_response = await client.get("/api/auth/me")

    assert logout_response.status_code == 204
    assert me_response.status_code == 401
