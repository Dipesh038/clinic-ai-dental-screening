from __future__ import annotations

import logging
from datetime import datetime, timezone
from time import perf_counter

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.ai import get_predictor
from app.db import get_database
from app.dependencies import require_role
from app.models.image import ImageOut
from app.models.prediction import DetectionOut, PredictionOut
from app.models.user import Role

router = APIRouter(
    tags=["images"], dependencies=[Depends(require_role(Role.DENTIST, Role.RECEPTIONIST))]
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
    )


async def create_prediction_for_image(
    image_id: str, image: dict, db: AsyncIOMotorDatabase
) -> PredictionOut | None:
    predictor = get_predictor()
    if predictor is None:
        return None

    started_at = perf_counter()
    detections = predictor.predict(image["imageUrl"])
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
