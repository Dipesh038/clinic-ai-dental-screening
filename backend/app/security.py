from typing import Optional, Tuple

from passlib.context import CryptContext

# bcrypt's default cost factor (12 rounds) takes ~2s to verify on the Render
# free tier's slow shared CPU, which dominates login latency end-to-end.
# 10 rounds is still well above OWASP's minimum recommendation and cuts that
# to a few hundred ms.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=10)


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def verify_and_rehash(plain_password: str, password_hash: str) -> Tuple[bool, Optional[str]]:
    """Verify a password, returning a re-hash at the current cost factor if the
    stored hash used an outdated one (e.g. an older, slower rounds setting)."""
    valid, new_hash = pwd_context.verify_and_update(plain_password, password_hash)
    return valid, new_hash
