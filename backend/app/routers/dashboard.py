from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from app.db import get_database
from app.dependencies import require_role
from app.models.user import Role


class DashboardStats(BaseModel):
    total_patients: int
    total_visits: int
    pending_reviews: int


router = APIRouter(
    tags=["dashboard"],
    dependencies=[Depends(require_role(Role.DENTIST, Role.RECEPTIONIST, Role.ADMIN))],
)


@router.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncIOMotorDatabase = Depends(get_database)) -> DashboardStats:
    total_patients = await db.patients.count_documents({"isDeleted": False})
    total_visits = await db.visits.count_documents({})

    # Images that don't have reviewedAt field, or reviewedAt is null
    pending_reviews = await db.images.count_documents({"reviewedAt": {"$exists": False}})

    return DashboardStats(
        total_patients=total_patients,
        total_visits=total_visits,
        pending_reviews=pending_reviews,
    )
