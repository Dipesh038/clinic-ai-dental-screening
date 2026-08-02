import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import close_client, get_database
from app.models.user import Role
from app.security import hash_password


async def seed():
    db = get_database()
    users = [
        ("admin", "admin123", Role.ADMIN),
        ("dentist", "dentist123", Role.DENTIST),
        ("receptionist", "receptionist123", Role.RECEPTIONIST),
    ]
    for username, password, role in users:
        existing = await db.users.find_one({"username": username})
        if existing is None:
            await db.users.insert_one(
                {"username": username, "password_hash": hash_password(password), "role": role.value}
            )
            print(f"Created {role.value} user: '{username}'")
        else:
            await db.users.update_one(
                {"username": username},
                {"$set": {"password_hash": hash_password(password), "role": role.value}},
            )
            print(f"Updated {role.value} user: '{username}'")

if __name__ == "__main__":
    try:
        asyncio.run(seed())
    finally:
        close_client()
