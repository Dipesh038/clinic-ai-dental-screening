from datetime import datetime
import logging

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.cloudinary_client import upload_image
from app.db import get_database
from app.dependencies import require_role
from app.image_processing import strip_exif_metadata
from app.models.image import ImageOut
from app.models.user import Role
from app.models.visit import VisitCreate, VisitOut, VisitUpdate
from app.routers.images import create_prediction_for_image
from app.report import generate_pdf_report

router = APIRouter(
    tags=["visits"], dependencies=[Depends(require_role(Role.DENTIST, Role.RECEPTIONIST, Role.ADMIN))]
)
logger = logging.getLogger("app.visits")

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024


def _to_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")


def _doc_to_out(doc: dict) -> VisitOut:
    return VisitOut(
        id=str(doc["_id"]),
        patient_id=str(doc["patientId"]),
        date=doc["date"].date() if hasattr(doc["date"], "date") else doc["date"],
        complaint=doc["complaint"],
        notes=doc.get("notes", ""),
    )


async def _get_active_patient(db: AsyncIOMotorDatabase, patient_id: str) -> dict:
    patient = await db.patients.find_one({"_id": _to_object_id(patient_id), "isDeleted": False})
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return patient


@router.get("/api/patients/{patient_id}/visits", response_model=list[VisitOut])
async def list_visits_for_patient(
    patient_id: str, db: AsyncIOMotorDatabase = Depends(get_database)
) -> list[VisitOut]:
    await _get_active_patient(db, patient_id)
    cursor = db.visits.find({"patientId": patient_id}).sort("date", -1)
    return [_doc_to_out(doc) async for doc in cursor]


@router.post(
    "/api/patients/{patient_id}/visits",
    response_model=VisitOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_visit(
    patient_id: str, visit: VisitCreate, db: AsyncIOMotorDatabase = Depends(get_database)
) -> VisitOut:
    await _get_active_patient(db, patient_id)
    doc = {
        "patientId": patient_id,
        "date": datetime.combine(visit.date, datetime.min.time()),
        "complaint": visit.complaint,
        "notes": visit.notes,
    }
    result = await db.visits.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _doc_to_out(doc)


@router.get("/api/visits/{visit_id}", response_model=VisitOut)
async def get_visit(visit_id: str, db: AsyncIOMotorDatabase = Depends(get_database)) -> VisitOut:
    doc = await db.visits.find_one({"_id": _to_object_id(visit_id)})
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found")
    return _doc_to_out(doc)


@router.put("/api/visits/{visit_id}", response_model=VisitOut)
async def update_visit(
    visit_id: str, visit: VisitUpdate, db: AsyncIOMotorDatabase = Depends(get_database)
) -> VisitOut:
    updates = visit.model_dump(exclude_unset=True)
    if "date" in updates:
        updates["date"] = datetime.combine(updates["date"], datetime.min.time())

    object_id = _to_object_id(visit_id)
    if updates:
        result = await db.visits.update_one({"_id": object_id}, {"$set": updates})
        if result.matched_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found")

    doc = await db.visits.find_one({"_id": object_id})
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found")
    return _doc_to_out(doc)


@router.post(
    "/api/visits/{visit_id}/images",
    response_model=ImageOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_visit_image(
    visit_id: str,
    file: UploadFile = File(...),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ImageOut:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG and PNG images are supported",
        )

    object_id = _to_object_id(visit_id)
    visit = await db.visits.find_one({"_id": object_id})
    if visit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image must be smaller than 5 MB",
        )

    file_bytes = strip_exif_metadata(file_bytes, file.content_type or "")
    image_url = upload_image(file_bytes, folder=f"visits/{visit_id}")

    doc = {"visitId": visit_id, "imageUrl": image_url}
    result = await db.images.insert_one(doc)
    doc["_id"] = result.inserted_id

    prediction = None
    try:
        prediction = await create_prediction_for_image(str(result.inserted_id), doc, db, image_bytes=file_bytes)
    except Exception:
        logger.exception("Automatic AI prediction failed for image_id=%s", result.inserted_id)

    top_detection = None
    try:
        if prediction and prediction.detections:
            top_detection = max(prediction.detections, key=lambda detection: detection.confidence)
    except Exception as e:
        logger.error(f"Error calculating top detection: {e}")

    return ImageOut(
        id=str(result.inserted_id),
        visit_id=visit_id,
        image_url=image_url,
        top_prediction=top_detection.disease_name if top_detection else None,
    )


@router.get("/api/visits/{visit_id}/images", response_model=list[ImageOut])
async def list_visit_images(
    visit_id: str, db: AsyncIOMotorDatabase = Depends(get_database)
) -> list[ImageOut]:
    object_id = _to_object_id(visit_id)
    visit = await db.visits.find_one({"_id": object_id})
    if visit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found")

    cursor = db.images.find({"visitId": visit_id}).sort("_id", -1)

    images = []
    async for image in cursor:
        from app.routers.images import _image_doc_to_out

        try:
            # We need to fetch the top prediction for each image
            image_out = _image_doc_to_out(image)
        except Exception as e:
            import logging
            logging.error(f"Error mapping image_doc_to_out for image {image.get('_id')}: {e}")
            continue
        prediction = await db.predictions.find_one(
            {"imageId": str(image["_id"])}, sort=[("createdAt", -1)]
        )

        top_prediction = None
        try:
            if prediction and prediction.get("detections"):
                top_detection = max(prediction["detections"], key=lambda d: d.get("confidence", 0))
                top_prediction = top_detection.get("disease_name")
        except Exception as e:
            import logging
            logging.error(f"Error extracting top prediction for image {image['_id']}: {e}")

        image_out.top_prediction = top_prediction
        images.append(image_out)

    return images


@router.get("/api/visits/{visit_id}/report", response_class=Response)
async def download_visit_report(
    visit_id: str, db: AsyncIOMotorDatabase = Depends(get_database)
) -> Response:
    object_id = _to_object_id(visit_id)
    visit = await db.visits.find_one({"_id": object_id})
    if visit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found")

    patient = await db.patients.find_one({"_id": _to_object_id(visit["patientId"])})
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    images = []
    cursor = db.images.find({"visitId": visit_id})
    async for image in cursor:
        image_id = str(image["_id"])

        # Get latest correction
        correction = await db.corrections.find_one({"imageId": image_id}, sort=[("createdAt", -1)])

        # Get latest prediction
        prediction = await db.predictions.find_one({"imageId": image_id}, sort=[("createdAt", -1)])

        images.append(
            {
                "image": image,
                "corrections": correction["corrections"] if correction else None,
                "predictions": prediction["detections"] if prediction else None,
            }
        )

    pdf_bytes = generate_pdf_report(patient, visit, images)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="report_{visit_id}.pdf"'},
    )
