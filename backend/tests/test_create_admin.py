import scripts.create_admin as create_admin_module
from app.models.user import Role
from app.security import verify_password
from scripts.create_admin import create_user


class FakeUsersCollection:
    def __init__(self):
        self.docs = []

    async def find_one(self, query):
        return next((d for d in self.docs if d["username"] == query["username"]), None)

    async def insert_one(self, doc):
        self.docs.append(doc)


class FakeDB:
    def __init__(self):
        self.users = FakeUsersCollection()


async def test_create_user_inserts_hashed_password(monkeypatch):
    fake_db = FakeDB()
    monkeypatch.setattr(create_admin_module, "get_database", lambda: fake_db)

    await create_user("admin", "s3cret-pw", Role.ADMIN)

    assert len(fake_db.users.docs) == 1
    stored = fake_db.users.docs[0]
    assert stored["username"] == "admin"
    assert stored["password_hash"] != "s3cret-pw"
    assert verify_password("s3cret-pw", stored["password_hash"])
    assert stored["role"] == "admin"


async def test_create_user_skips_existing_username(monkeypatch):
    fake_db = FakeDB()
    fake_db.users.docs.append({"username": "admin", "password_hash": "x", "role": "admin"})
    monkeypatch.setattr(create_admin_module, "get_database", lambda: fake_db)

    await create_user("admin", "new-pw", Role.ADMIN)

    assert len(fake_db.users.docs) == 1
    assert fake_db.users.docs[0]["password_hash"] == "x"
