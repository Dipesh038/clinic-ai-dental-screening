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


async def _create_patient(client) -> str:
    response = await client.post(
        "/api/patients",
        json={
            "name": "Jane Doe",
            "dob": "1990-05-15",
            "gender": "female",
            "contact": "555-1234",
            "notes": "",
        },
    )
    return response.json()["id"]


VISIT_PAYLOAD = {"date": "2026-01-10", "complaint": "Tooth pain", "notes": "Upper right molar"}


async def test_create_visit_returns_201():
    async with await _client() as client:
        patient_id = await _create_patient(client)
        response = await client.post(f"/api/patients/{patient_id}/visits", json=VISIT_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert body["complaint"] == "Tooth pain"
    assert body["patient_id"] == patient_id


async def test_create_visit_for_unknown_patient_returns_404():
    async with await _client() as client:
        response = await client.post(
            "/api/patients/000000000000000000000000/visits", json=VISIT_PAYLOAD
        )
    assert response.status_code == 404


async def test_list_visits_for_patient():
    async with await _client() as client:
        patient_id = await _create_patient(client)
        await client.post(f"/api/patients/{patient_id}/visits", json=VISIT_PAYLOAD)
        response = await client.get(f"/api/patients/{patient_id}/visits")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["complaint"] == "Tooth pain"


async def test_get_visit_by_id():
    async with await _client() as client:
        patient_id = await _create_patient(client)
        create_resp = await client.post(f"/api/patients/{patient_id}/visits", json=VISIT_PAYLOAD)
        visit_id = create_resp.json()["id"]
        response = await client.get(f"/api/visits/{visit_id}")

    assert response.status_code == 200
    assert response.json()["id"] == visit_id


async def test_get_visit_not_found_returns_404():
    async with await _client() as client:
        response = await client.get("/api/visits/000000000000000000000000")
    assert response.status_code == 404


async def test_update_visit_persists_changes():
    async with await _client() as client:
        patient_id = await _create_patient(client)
        create_resp = await client.post(f"/api/patients/{patient_id}/visits", json=VISIT_PAYLOAD)
        visit_id = create_resp.json()["id"]
        response = await client.put(
            f"/api/visits/{visit_id}", json={"notes": "Resolved with filling"}
        )

    assert response.status_code == 200
    assert response.json()["notes"] == "Resolved with filling"
    assert response.json()["complaint"] == "Tooth pain"


async def test_visits_require_authentication():
    app.dependency_overrides.pop(get_current_user, None)
    async with await _client() as client:
        response = await client.get("/api/patients/000000000000000000000000/visits")
    assert response.status_code == 401


async def test_admin_role_forbidden_from_visits():
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        username="admin1", role=Role.ADMIN
    )
    async with await _client() as client:
        response = await client.get("/api/patients/000000000000000000000000/visits")
    assert response.status_code == 403
