from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.db import get_database
from app.dependencies import CurrentUser, get_current_user
from app.main import app
from app.models.user import Role
from tests.conftest import FakeDB


@pytest.fixture
def fake_db():
    return FakeDB()


@pytest.fixture(autouse=True)
def override_dependencies(fake_db):
    app.dependency_overrides[get_database] = lambda: fake_db
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        username="dr.smith", role=Role.DENTIST
    )
    yield
    app.dependency_overrides.clear()


async def _client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="https://test")


async def test_dashboard_stats_returns_counts(fake_db):
    fake_db.patients.docs.extend(
        [
            {"name": "Jane Doe", "isDeleted": False},
            {"name": "John Roe", "isDeleted": False},
            {"name": "Deleted Pat", "isDeleted": True},
        ]
    )
    fake_db.visits.docs.extend([{"complaint": "Tooth pain"}])
    fake_db.images.docs.extend(
        [
            {"imageUrl": "https://cloudinary/a.jpg"},
            {"imageUrl": "https://cloudinary/b.jpg", "reviewedAt": "2026-01-01T00:00:00Z"},
        ]
    )

    async with await _client() as client:
        response = await client.get("/api/dashboard/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["total_patients"] == 2
    assert body["total_visits"] == 1
    assert body["pending_reviews"] == 1
