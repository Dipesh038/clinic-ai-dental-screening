from __future__ import annotations

import logging
from datetime import datetime, timezone
from time import perf_counter

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, Response, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from io import BytesIO
from urllib.request import urlopen
from PIL import Image

from app.ai import get_predictor
from app.db import get_database
from app.dependencies import require_role
from app.models.image import ImageOut
from app.models.prediction import DetectionOut, PredictionOut
from app.models.correction import CorrectionIn, CorrectionOut, CorrectionItem
from app.models.user import Role
from app.grad_cam import generate_heatmap_for_crop

router = APIRouter(
    tags=["images"], dependencies=[Depends(require_role(Role.DENTIST, Role.RECEPTIONIST, Role.ADMIN))]
)
logger = logging.getLogger("app.images")


def _to_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")


def _doc_to_out(doc: dict) -> PredictionOut:
    return PredictionOut(
        id=str(doc["_id"]),
        image_id=str(doc["imageId"]),
        detections=[DetectionOut(**detection) for detection in doc["detections"]],
        latency_ms=doc["latencyMs"],
        created_at=doc["createdAt"],
    )


def _image_doc_to_out(doc: dict) -> ImageOut:
    return ImageOut(
        id=str(doc["_id"]),
        visit_id=str(doc["visitId"]),
        image_url=doc["imageUrl"],
        reviewed_at=doc.get("reviewedAt"),
    )


async def create_prediction_for_image(
    image_id: str, image: dict, db: AsyncIOMotorDatabase, image_bytes: bytes | None = None
) -> PredictionOut | None:
    predictor = get_predictor()
    if predictor is None:
        return None

    started_at = perf_counter()
    detections = predictor.predict(image_url=image["imageUrl"], image_bytes=image_bytes)
    latency_ms = round((perf_counter() - started_at) * 1000)

    doc = {
        "imageId": image_id,
        "detections": [detection.model_dump() for detection in detections],
        "latencyMs": latency_ms,
        "createdAt": datetime.now(timezone.utc),
    }
    result = await db.predictions.insert_one(doc)
    doc["_id"] = result.inserted_id

    logger.info(
        "AI prediction completed image_id=%s latency_ms=%s detections=%s",
        image_id,
        latency_ms,
        len(detections),
    )
    return _doc_to_out(doc)


@router.get("/api/images/{image_id}", response_model=ImageOut)
async def get_image(image_id: str, db: AsyncIOMotorDatabase = Depends(get_database)) -> ImageOut:
    image = await db.images.find_one({"_id": _to_object_id(image_id)})
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    return _image_doc_to_out(image)


@router.delete("/api/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(image_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    object_id = _to_object_id(image_id)
    image = await db.images.find_one({"_id": object_id})
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    await db.images.delete_one({"_id": object_id})
    await db.predictions.delete_many({"imageId": image_id})
    await db.corrections.delete_many({"imageId": image_id})
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/api/images/{image_id}/predictions/latest", response_model=PredictionOut)
async def get_latest_prediction(
    image_id: str, db: AsyncIOMotorDatabase = Depends(get_database)
) -> PredictionOut:
    image = await db.images.find_one({"_id": _to_object_id(image_id)})
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    cursor = db.predictions.find({"imageId": image_id}).sort("createdAt", -1)
    async for prediction in cursor:
        return _doc_to_out(prediction)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found")


@router.post("/api/images/{image_id}/predict", response_model=PredictionOut)
async def predict_image(
    image_id: str, db: AsyncIOMotorDatabase = Depends(get_database)
) -> PredictionOut:
    image = await db.images.find_one({"_id": _to_object_id(image_id)})
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    prediction = await create_prediction_for_image(image_id, image, db)
    if prediction is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI model is not available",
        )
    return prediction


@router.post("/api/images/{image_id}/corrections", response_model=CorrectionOut)
async def save_corrections(
    image_id: str, correction_in: CorrectionIn, db: AsyncIOMotorDatabase = Depends(get_database)
) -> CorrectionOut:
    image = await db.images.find_one({"_id": _to_object_id(image_id)})
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    doc = {
        "imageId": image_id,
        "corrections": [item.model_dump() for item in correction_in.corrections],
        "createdAt": datetime.now(timezone.utc),
    }
    result = await db.corrections.insert_one(doc)
    doc["_id"] = result.inserted_id

    return CorrectionOut(
        id=str(doc["_id"]),
        image_id=doc["imageId"],
        corrections=[CorrectionItem(**c) for c in doc["corrections"]],
        created_at=doc["createdAt"],
    )


@router.get("/api/images/{image_id}/corrections/latest", response_model=CorrectionOut)
async def get_latest_correction(
    image_id: str, db: AsyncIOMotorDatabase = Depends(get_database)
) -> CorrectionOut:
    image = await db.images.find_one({"_id": _to_object_id(image_id)})
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    cursor = db.corrections.find({"imageId": image_id}).sort("createdAt", -1)
    async for doc in cursor:
        return CorrectionOut(
            id=str(doc["_id"]),
            image_id=doc["imageId"],
            corrections=[CorrectionItem(**c) for c in doc["corrections"]],
            created_at=doc["createdAt"],
        )

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Corrections not found")


@router.post("/api/images/{image_id}/mark-reviewed", response_model=ImageOut)
async def mark_image_reviewed(
    image_id: str, db: AsyncIOMotorDatabase = Depends(get_database)
) -> ImageOut:
    object_id = _to_object_id(image_id)
    image = await db.images.find_one({"_id": object_id})
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    reviewed_at = datetime.now(timezone.utc)
    await db.images.update_one({"_id": object_id}, {"$set": {"reviewedAt": reviewed_at}})
    image["reviewedAt"] = reviewed_at
    return _image_doc_to_out(image)


@router.get("/api/images/{image_id}/heatmap/{detection_index}", response_class=Response)
async def get_image_heatmap(
    image_id: str, detection_index: int, db: AsyncIOMotorDatabase = Depends(get_database)
) -> Response:
    image = await db.images.find_one({"_id": _to_object_id(image_id)})
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    cursor = db.predictions.find({"imageId": image_id}).sort("createdAt", -1)
    prediction = None
    async for p in cursor:
        prediction = p
        break

    if prediction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found")

    detections = prediction.get("detections", [])
    if detection_index < 0 or detection_index >= len(detections):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Detection not found")

    box = detections[detection_index]["box"]

    # Load original image
    try:
        with urlopen(image["imageUrl"]) as response:
            original_image = Image.open(BytesIO(response.read()))
            original_image.load()
    except Exception as e:
        logger.error(f"Failed to fetch image for heatmap: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to load image"
        )

    # Crop to bounding box
    crop = original_image.crop((box["x1"], box["y1"], box["x2"], box["y2"]))

    # Generate heatmap
    try:
        heatmap_bytes = generate_heatmap_for_crop(crop)
    except Exception as e:
        logger.error(f"Failed to generate heatmap: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate heatmap"
        )

    return Response(content=heatmap_bytes, media_type="image/jpeg")
