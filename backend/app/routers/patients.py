from datetime import date, datetime

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db import get_database
from app.dependencies import require_role
from app.models.patient import PatientCreate, PatientOut, PatientUpdate
from app.models.user import Role

router = APIRouter(
    prefix="/api/patients",
    tags=["patients"],
    dependencies=[Depends(require_role(Role.DENTIST, Role.RECEPTIONIST))],
)


def _to_object_id(patient_id: str) -> ObjectId:
    try:
        return ObjectId(patient_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")


def _doc_to_out(doc: dict) -> PatientOut:
    dob = doc["dob"]
    if isinstance(dob, datetime):
        dob = dob.date()
    return PatientOut(
        id=str(doc["_id"]),
        name=doc["name"],
        dob=dob,
        gender=doc["gender"],
        contact=doc["contact"],
        notes=doc.get("notes", ""),
    )


def _dob_to_datetime(dob: date) -> datetime:
    return datetime.combine(dob, datetime.min.time())


@router.get("", response_model=list[PatientOut])
async def list_patients(db: AsyncIOMotorDatabase = Depends(get_database)) -> list[PatientOut]:
    cursor = db.patients.find({"isDeleted": False})
    return [_doc_to_out(doc) async for doc in cursor]


@router.post("", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient: PatientCreate, db: AsyncIOMotorDatabase = Depends(get_database)
) -> PatientOut:
    doc = {
        "name": patient.name,
        "dob": _dob_to_datetime(patient.dob),
        "gender": patient.gender.value,
        "contact": patient.contact,
        "notes": patient.notes,
        "isDeleted": False,
    }
    result = await db.patients.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _doc_to_out(doc)


@router.get("/{patient_id}", response_model=PatientOut)
async def get_patient(
    patient_id: str, db: AsyncIOMotorDatabase = Depends(get_database)
) -> PatientOut:
    doc = await db.patients.find_one({"_id": _to_object_id(patient_id), "isDeleted": False})
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return _doc_to_out(doc)


@router.put("/{patient_id}", response_model=PatientOut)
async def update_patient(
    patient_id: str,
    patient: PatientUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> PatientOut:
    updates = patient.model_dump(exclude_unset=True)
    if "dob" in updates:
        updates["dob"] = _dob_to_datetime(updates["dob"])
    if "gender" in updates:
        updates["gender"] = updates["gender"].value

    object_id = _to_object_id(patient_id)
    if updates:
        result = await db.patients.update_one(
            {"_id": object_id, "isDeleted": False}, {"$set": updates}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    doc = await db.patients.find_one({"_id": object_id, "isDeleted": False})
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return _doc_to_out(doc)


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: str, db: AsyncIOMotorDatabase = Depends(get_database)
) -> None:
    result = await db.patients.update_one(
        {"_id": _to_object_id(patient_id), "isDeleted": False},
        {"$set": {"isDeleted": True}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
