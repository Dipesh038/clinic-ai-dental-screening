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


async def test_upload_visit_image_returns_url(monkeypatch):
    import app.routers.visits as visits_module

    monkeypatch.setattr(
        visits_module, "upload_image", lambda file_bytes, folder: "https://cloudinary/test.jpg"
    )
    async with await _client() as client:
        patient_id = await _create_patient(client)
        create_resp = await client.post(f"/api/patients/{patient_id}/visits", json=VISIT_PAYLOAD)
        visit_id = create_resp.json()["id"]
        response = await client.post(
            f"/api/visits/{visit_id}/images",
            files={"file": ("tooth.jpg", b"fake-image-bytes", "image/jpeg")},
        )

    assert response.status_code == 201
    body = response.json()
    assert body["image_url"] == "https://cloudinary/test.jpg"
    assert body["visit_id"] == visit_id


async def test_upload_visit_image_triggers_prediction(monkeypatch):
    import app.routers.visits as visits_module
    from app.models.prediction import BoundingBox, DetectionOut, PredictionOut
    from datetime import datetime, timezone

    monkeypatch.setattr(
        visits_module, "upload_image", lambda file_bytes, folder: "https://cloudinary/test.jpg"
    )

    async def fake_create_prediction_for_image(image_id, image, db):
        return PredictionOut(
            id="prediction-1",
            image_id=image_id,
            detections=[
                DetectionOut(
                    class_id=1,
                    disease_name="plaque",
                    confidence=0.91,
                    box=BoundingBox(x1=1, y1=2, x2=3, y2=4),
                )
            ],
            latency_ms=12,
            created_at=datetime.now(timezone.utc),
        )

    monkeypatch.setattr(
        visits_module, "create_prediction_for_image", fake_create_prediction_for_image
    )

    async with await _client() as client:
        patient_id = await _create_patient(client)
        create_resp = await client.post(f"/api/patients/{patient_id}/visits", json=VISIT_PAYLOAD)
        visit_id = create_resp.json()["id"]
        response = await client.post(
            f"/api/visits/{visit_id}/images",
            files={"file": ("tooth.jpg", b"fake-image-bytes", "image/jpeg")},
        )

    assert response.status_code == 201
    assert response.json()["top_prediction"] == "plaque"


async def test_upload_image_for_unknown_visit_returns_404():
    async with await _client() as client:
        response = await client.post(
            "/api/visits/000000000000000000000000/images",
            files={"file": ("tooth.jpg", b"fake-image-bytes", "image/jpeg")},
        )
    assert response.status_code == 404


async def test_upload_visit_image_rejects_unsupported_type():
    async with await _client() as client:
        patient_id = await _create_patient(client)
        create_resp = await client.post(f"/api/patients/{patient_id}/visits", json=VISIT_PAYLOAD)
        visit_id = create_resp.json()["id"]
        response = await client.post(
            f"/api/visits/{visit_id}/images",
            files={"file": ("tooth.gif", b"fake-image-bytes", "image/gif")},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only JPEG and PNG images are supported"


async def test_upload_visit_image_rejects_files_over_5mb():
    async with await _client() as client:
        patient_id = await _create_patient(client)
        create_resp = await client.post(f"/api/patients/{patient_id}/visits", json=VISIT_PAYLOAD)
        visit_id = create_resp.json()["id"]
        response = await client.post(
            f"/api/visits/{visit_id}/images",
            files={"file": ("large.png", b"x" * (5 * 1024 * 1024 + 1), "image/png")},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Image must be smaller than 5 MB"


async def test_download_visit_report_returns_pdf(monkeypatch):
    import app.routers.visits as visits_module

    monkeypatch.setattr(
        visits_module, "upload_image", lambda file_bytes, folder: "https://cloudinary/test.jpg"
    )

    async with await _client() as client:
        patient_id = await _create_patient(client)
        create_resp = await client.post(f"/api/patients/{patient_id}/visits", json=VISIT_PAYLOAD)
        visit_id = create_resp.json()["id"]
        await client.post(
            f"/api/visits/{visit_id}/images",
            files={"file": ("tooth.jpg", b"fake-image-bytes", "image/jpeg")},
        )
        response = await client.get(f"/api/visits/{visit_id}/report")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


async def test_download_visit_report_for_unknown_visit_returns_404():
    async with await _client() as client:
        response = await client.get("/api/visits/000000000000000000000000/report")
    assert response.status_code == 404


async def test_upload_visit_image_strips_jpeg_exif(monkeypatch):
    import app.routers.visits as visits_module

    uploaded_bytes = {}

    def fake_upload_image(file_bytes, folder):
        uploaded_bytes["value"] = file_bytes
        return "https://cloudinary/test.jpg"

    jpeg_with_exif = (
        b"\xff\xd8" + b"\xff\xe1" + (8).to_bytes(2, "big") + b"Exif\x00\x00" + b"\xff\xd9"
    )

    monkeypatch.setattr(visits_module, "upload_image", fake_upload_image)
    async with await _client() as client:
        patient_id = await _create_patient(client)
        create_resp = await client.post(f"/api/patients/{patient_id}/visits", json=VISIT_PAYLOAD)
        visit_id = create_resp.json()["id"]
        response = await client.post(
            f"/api/visits/{visit_id}/images",
            files={"file": ("tooth.jpg", jpeg_with_exif, "image/jpeg")},
        )

    assert response.status_code == 201
    assert uploaded_bytes["value"] == b"\xff\xd8\xff\xd9"
