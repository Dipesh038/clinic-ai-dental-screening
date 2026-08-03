from datetime import datetime
import logging

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Response,
    UploadFile,
    status,
)
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

router = APIRouter(tags=["visits"])
logger = logging.getLogger("app.visits")

# Front-desk actions (scheduling/records): dentist + receptionist.
_frontdesk = Depends(require_role(Role.DENTIST, Role.RECEPTIONIST))
# Read-only for everyone, including admin oversight.
_view = Depends(require_role(Role.DENTIST, Role.RECEPTIONIST, Role.ADMIN))
# Clinical work (uploading/reviewing images): dentist only.
_clinical = Depends(require_role(Role.DENTIST))
# Clinical read (image list exposes AI predictions): dentist + admin, not receptionist.
_clinical_view = Depends(require_role(Role.DENTIST, Role.ADMIN))

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


@router.get(
    "/api/patients/{patient_id}/visits", response_model=list[VisitOut], dependencies=[_view]
)
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
    dependencies=[_frontdesk],
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


@router.get("/api/visits/{visit_id}", response_model=VisitOut, dependencies=[_view])
async def get_visit(visit_id: str, db: AsyncIOMotorDatabase = Depends(get_database)) -> VisitOut:
    doc = await db.visits.find_one({"_id": _to_object_id(visit_id)})
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found")
    return _doc_to_out(doc)


@router.put("/api/visits/{visit_id}", response_model=VisitOut, dependencies=[_frontdesk])
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


async def _run_prediction_in_background(
    image_id: str, doc: dict, file_bytes: bytes, db: AsyncIOMotorDatabase
) -> None:
    # Runs after the upload response has already been sent. AI inference on the
    # free-tier backend's CPU can take 20-30+ seconds; blocking the upload
    # request on it made every upload feel that slow. Takes the same `db`
    # handle the request was injected with (Motor's client is a shared,
    # long-lived connection pool, so reusing it post-response is safe) rather
    # than re-resolving get_database(), which would bypass FastAPI's
    # dependency-override mechanism and silently skip the test DB in tests.
    try:
        await create_prediction_for_image(image_id, doc, db, image_bytes=file_bytes)
    except Exception:
        logger.exception("Automatic AI prediction failed for image_id=%s", image_id)


@router.post(
    "/api/visits/{visit_id}/images",
    response_model=ImageOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[_clinical],
)
async def upload_visit_image(
    visit_id: str,
    background_tasks: BackgroundTasks,
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
    image_id = str(result.inserted_id)

    background_tasks.add_task(_run_prediction_in_background, image_id, doc, file_bytes, db)

    return ImageOut(
        id=image_id,
        visit_id=visit_id,
        image_url=image_url,
        top_prediction=None,
    )


@router.get(
    "/api/visits/{visit_id}/images", response_model=list[ImageOut], dependencies=[_clinical_view]
)
async def list_visit_images(
    visit_id: str, db: AsyncIOMotorDatabase = Depends(get_database)
) -> list[ImageOut]:
    object_id = _to_object_id(visit_id)
    visit = await db.visits.find_one({"_id": object_id})
    if visit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found")

    from app.routers.images import _image_doc_to_out

    visit_images = [image async for image in db.images.find({"visitId": visit_id}).sort("_id", -1)]
    image_ids = [str(image["_id"]) for image in visit_images]

    # One query for every image's latest prediction instead of one query per
    # image -- was N+1 round-trips for N images, now 2 total.
    latest_prediction_by_image: dict[str, dict] = {}
    async for prediction in db.predictions.find({"imageId": {"$in": image_ids}}).sort(
        "createdAt", -1
    ):
        latest_prediction_by_image.setdefault(prediction["imageId"], prediction)

    images = []
    for image in visit_images:
        try:
            image_out = _image_doc_to_out(image)
        except Exception as e:
            import logging
            logging.error(f"Error mapping image_doc_to_out for image {image.get('_id')}: {e}")
            continue

        prediction = latest_prediction_by_image.get(str(image["_id"]))
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


@router.get("/api/visits/{visit_id}/report", response_class=Response, dependencies=[_view])
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

    visit_images = [image async for image in db.images.find({"visitId": visit_id})]
    image_ids = [str(image["_id"]) for image in visit_images]

    # One query per collection for the whole visit instead of two per image --
    # was 2N+1 round-trips for N images, now 3 total. Sorted newest-first, so
    # the first entry seen per imageId while building the map below is the
    # latest one (matches the per-image find_one(..., sort=[("createdAt", -1)])
    # this replaces).
    latest_correction_by_image: dict[str, dict] = {}
    async for correction in db.corrections.find({"imageId": {"$in": image_ids}}).sort(
        "createdAt", -1
    ):
        latest_correction_by_image.setdefault(correction["imageId"], correction)

    latest_prediction_by_image: dict[str, dict] = {}
    async for prediction in db.predictions.find({"imageId": {"$in": image_ids}}).sort(
        "createdAt", -1
    ):
        latest_prediction_by_image.setdefault(prediction["imageId"], prediction)

    images = []
    for image in visit_images:
        image_id = str(image["_id"])
        correction = latest_correction_by_image.get(image_id)
        prediction = latest_prediction_by_image.get(image_id)
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
