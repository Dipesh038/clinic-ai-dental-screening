from __future__ import annotations

from bson import ObjectId


def _matches(doc: dict, query: dict) -> bool:
    for key, value in query.items():
        if isinstance(value, dict) and "$exists" in value:
            if (key in doc) != value["$exists"]:
                return False
        elif doc.get(key) != value:
            return False
    return True


class FakeCursor:
    def __init__(self, docs: list[dict]):
        self._docs = docs

    def sort(self, key: str, direction: int = 1) -> "FakeCursor":
        self._docs = sorted(self._docs, key=lambda d: d.get(key), reverse=direction < 0)
        return self

    def __aiter__(self):
        return self._generator()

    async def _generator(self):
        for doc in self._docs:
            yield doc


class _Result:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class FakeCollection:
    def __init__(self):
        self.docs: list[dict] = []

    def find(self, query: dict | None = None) -> FakeCursor:
        query = query or {}
        return FakeCursor([d for d in self.docs if _matches(d, query)])

    async def find_one(self, query: dict, sort: list[tuple[str, int]] | None = None) -> dict | None:
        matches = [d for d in self.docs if _matches(d, query)]
        if sort:
            key, direction = sort[0]
            matches.sort(key=lambda d: d.get(key), reverse=direction < 0)
        return matches[0] if matches else None

    async def count_documents(self, query: dict | None = None) -> int:
        return len([d for d in self.docs if _matches(d, query or {})])

    async def insert_one(self, doc: dict) -> _Result:
        doc.setdefault("_id", ObjectId())
        self.docs.append(doc)
        return _Result(inserted_id=doc["_id"])

    async def update_one(self, query: dict, update: dict) -> _Result:
        for doc in self.docs:
            if _matches(doc, query):
                doc.update(update.get("$set", {}))
                return _Result(matched_count=1)
        return _Result(matched_count=0)

    async def delete_one(self, query: dict) -> _Result:
        for i, doc in enumerate(self.docs):
            if _matches(doc, query):
                del self.docs[i]
                return _Result(deleted_count=1)
        return _Result(deleted_count=0)

    async def delete_many(self, query: dict) -> _Result:
        before = len(self.docs)
        self.docs = [d for d in self.docs if not _matches(d, query)]
        return _Result(deleted_count=before - len(self.docs))


class FakeDB:
    def __init__(self):
        self.users = FakeCollection()
        self.patients = FakeCollection()
        self.visits = FakeCollection()
        self.images = FakeCollection()
        self.predictions = FakeCollection()
        self.corrections = FakeCollection()
