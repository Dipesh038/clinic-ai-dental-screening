from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_uri)
    return _client


def get_database() -> AsyncIOMotorDatabase:
    return get_client().get_default_database(default="clinic_ai")


async def ensure_indexes() -> None:
    # Every non-_id query in this app was a full collection scan (no indexes
    # existed anywhere). Fine at today's data volume, but each of these
    # matches an actual find()/count_documents() filter or sort in the
    # routers, so it's the difference between O(n) and O(log n) as data
    # grows. create_index is a no-op if the index already exists, so this is
    # safe to run on every startup.
    db = get_database()
    await db.users.create_index("username", unique=True)
    await db.patients.create_index("isDeleted")
    await db.visits.create_index([("patientId", 1), ("date", -1)])
    await db.images.create_index("visitId")
    await db.images.create_index("reviewedAt")
    await db.predictions.create_index([("imageId", 1), ("createdAt", -1)])
    await db.corrections.create_index([("imageId", 1), ("createdAt", -1)])


def close_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
