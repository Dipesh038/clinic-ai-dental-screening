"""Seed a user (default role: admin) into the Users collection.

Usage:
    python scripts/create_admin.py --username admin
    python scripts/create_admin.py --username admin --role admin --password "..."

Run from the backend/ directory with the venv active. If --password is
omitted you'll be prompted securely (input is not echoed to the terminal).
"""

import argparse
import asyncio
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import close_client, get_database  # noqa: E402
from app.models.user import Role  # noqa: E402
from app.security import hash_password  # noqa: E402


async def create_user(username: str, password: str, role: Role) -> None:
    db = get_database()
    existing = await db.users.find_one({"username": username})
    if existing is not None:
        print(f"User '{username}' already exists — skipping.")
        return
    await db.users.insert_one(
        {"username": username, "password_hash": hash_password(password), "role": role.value}
    )
    print(f"Created {role.value} user '{username}'.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed a user into the Users collection.")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", default=None, help="Omit to be prompted securely.")
    parser.add_argument("--role", default="admin", choices=[r.value for r in Role])
    args = parser.parse_args()

    password = args.password or getpass.getpass("Password: ")
    try:
        asyncio.run(create_user(args.username, password, Role(args.role)))
    finally:
        close_client()


if __name__ == "__main__":
    main()
