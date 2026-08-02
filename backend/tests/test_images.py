from bson import ObjectId
import pytest
from httpx import ASGITransport, AsyncClient

from app.db import get_database
from app.dependencies import CurrentUser, get_current_user
from app.main import app
from app.models.prediction import BoundingBox, DetectionOut
from app.models.user import Role
import app.routers.images as images_module
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


def _insert_image(fake_db: FakeDB) -> str:
    image_id = ObjectId()
    fake_db.images.docs.append(
        {
            "_id": image_id,
            "visitId": "visit-1",
            "imageUrl": "https://cloudinary.example/tooth.jpg",
        }
    )
    return str(image_id)


async def test_predict_image_saves_expected_json_shape(fake_db, monkeypatch):
    class FakePredictor:
        def predict(self, image_url: str) -> list[DetectionOut]:
            assert image_url == "https://cloudinary.example/tooth.jpg"
            return [
                DetectionOut(
                    class_id=0,
                    disease_name="cavity",
                    confidence=0.87,
                    box=BoundingBox(x1=10, y1=20, x2=80, y2=120),
                )
            ]

    image_id = _insert_image(fake_db)
    monkeypatch.setattr(images_module, "get_predictor", lambda: FakePredictor())

    async with await _client() as client:
        response = await client.post(f"/api/images/{image_id}/predict")

    assert response.status_code == 200
    body = response.json()
    assert body["image_id"] == image_id
    assert body["detections"] == [
        {
            "class_id": 0,
            "disease_name": "cavity",
            "confidence": 0.87,
            "box": {"x1": 10.0, "y1": 20.0, "x2": 80.0, "y2": 120.0},
        }
    ]
    assert isinstance(body["latency_ms"], int)
    assert len(fake_db.predictions.docs) == 1


async def test_predict_image_returns_503_when_model_unavailable(fake_db, monkeypatch):
    image_id = _insert_image(fake_db)
    monkeypatch.setattr(images_module, "get_predictor", lambda: None)

    async with await _client() as client:
        response = await client.post(f"/api/images/{image_id}/predict")

    assert response.status_code == 503
    assert response.json()["detail"] == "AI model is not available"


async def test_predict_image_for_unknown_image_returns_404(monkeypatch):
    monkeypatch.setattr(images_module, "get_predictor", lambda: None)

    async with await _client() as client:
        response = await client.post("/api/images/000000000000000000000000/predict")

    assert response.status_code == 404


async def test_get_latest_prediction_returns_most_recent(fake_db):
    image_id = _insert_image(fake_db)
    older_id = ObjectId()
    newer_id = ObjectId()
    fake_db.predictions.docs.extend(
        [
            {
                "_id": older_id,
                "imageId": image_id,
                "detections": [],
                "latencyMs": 20,
                "createdAt": "2026-01-01T00:00:00Z",
            },
            {
                "_id": newer_id,
                "imageId": image_id,
                "detections": [],
                "latencyMs": 10,
                "createdAt": "2026-01-02T00:00:00Z",
            },
        ]
    )

    async with await _client() as client:
        response = await client.get(f"/api/images/{image_id}/predictions/latest")

    assert response.status_code == 200
    assert response.json()["id"] == str(newer_id)


async def test_save_corrections_and_get_latest(fake_db):
    image_id = _insert_image(fake_db)
    payload = {
        "corrections": [
            {
                "class_id": 1,
                "disease_name": "periodontitis",
                "box": {"x1": 10.0, "y1": 20.0, "x2": 80.0, "y2": 120.0},
            }
        ]
    }

    async with await _client() as client:
        # Save corrections
        post_response = await client.post(f"/api/images/{image_id}/corrections", json=payload)
        assert post_response.status_code == 200
        post_body = post_response.json()
        assert post_body["image_id"] == image_id
        assert len(post_body["corrections"]) == 1
        assert post_body["corrections"][0]["disease_name"] == "periodontitis"

        # Get latest
        get_response = await client.get(f"/api/images/{image_id}/corrections/latest")
        assert get_response.status_code == 200
        assert get_response.json()["id"] == post_body["id"]


async def test_mark_image_reviewed(fake_db):
    image_id = _insert_image(fake_db)

    async with await _client() as client:
        response = await client.post(f"/api/images/{image_id}/mark-reviewed")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == image_id
    assert "reviewed_at" in body
    assert body["reviewed_at"] is not None

    # Verify db update
    doc = fake_db.images.docs[0]
    assert "reviewedAt" in doc
    assert doc["reviewedAt"] is not None
