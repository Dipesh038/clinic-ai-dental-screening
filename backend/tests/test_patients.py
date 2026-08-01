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


PATIENT_PAYLOAD = {
    "name": "Jane Doe",
    "dob": "1990-05-15",
    "gender": "female",
    "contact": "555-1234",
    "notes": "Prefers morning appointments",
}


async def test_create_patient_returns_201():
    async with await _client() as client:
        response = await client.post("/api/patients", json=PATIENT_PAYLOAD)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Jane Doe"
    assert body["dob"] == "1990-05-15"
    assert "id" in body


async def test_list_patients_excludes_soft_deleted():
    async with await _client() as client:
        create_resp = await client.post("/api/patients", json=PATIENT_PAYLOAD)
        patient_id = create_resp.json()["id"]
        await client.delete(f"/api/patients/{patient_id}")
        list_resp = await client.get("/api/patients")

    assert list_resp.status_code == 200
    assert list_resp.json() == []


async def test_get_patient_by_id():
    async with await _client() as client:
        create_resp = await client.post("/api/patients", json=PATIENT_PAYLOAD)
        patient_id = create_resp.json()["id"]
        get_resp = await client.get(f"/api/patients/{patient_id}")

    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Jane Doe"


async def test_get_patient_not_found_returns_404():
    async with await _client() as client:
        response = await client.get("/api/patients/000000000000000000000000")
    assert response.status_code == 404


async def test_update_patient_persists_changes():
    async with await _client() as client:
        create_resp = await client.post("/api/patients", json=PATIENT_PAYLOAD)
        patient_id = create_resp.json()["id"]
        update_resp = await client.put(
            f"/api/patients/{patient_id}", json={"contact": "555-9999"}
        )

    assert update_resp.status_code == 200
    assert update_resp.json()["contact"] == "555-9999"
    assert update_resp.json()["name"] == "Jane Doe"


async def test_delete_patient_soft_deletes():
    async with await _client() as client:
        create_resp = await client.post("/api/patients", json=PATIENT_PAYLOAD)
        patient_id = create_resp.json()["id"]
        delete_resp = await client.delete(f"/api/patients/{patient_id}")
        get_resp = await client.get(f"/api/patients/{patient_id}")

    assert delete_resp.status_code == 204
    assert get_resp.status_code == 404


async def test_patients_require_authentication():
    app.dependency_overrides.pop(get_current_user, None)
    async with await _client() as client:
        response = await client.get("/api/patients")
    assert response.status_code == 401


async def test_admin_role_forbidden_from_patients():
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        username="admin1", role=Role.ADMIN
    )
    async with await _client() as client:
        response = await client.get("/api/patients")
    assert response.status_code == 403


async def test_receptionist_role_allowed_on_patients():
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        username="reception1", role=Role.RECEPTIONIST
    )
    async with await _client() as client:
        response = await client.get("/api/patients")
    assert response.status_code == 200
