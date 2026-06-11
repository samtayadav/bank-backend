import hashlib
import hmac
import secrets
from datetime import datetime, timezone

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from database import sessions_collection, users_collection

bearer_scheme = HTTPBearer(auto_error=False)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _hash_password(password: str, salt: str | None = None) -> str:
    password_salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        password_salt.encode("utf-8"),
        120000,
    ).hex()
    return f"{password_salt}:{digest}"


def _verify_password(password: str, password_hash: str) -> bool:
    try:
        salt, expected_digest = password_hash.split(":", 1)
    except ValueError:
        return False

    actual_digest = _hash_password(password, salt).split(":", 1)[1]
    return hmac.compare_digest(actual_digest, expected_digest)


async def create_user(username: str, password: str) -> dict:
    normalized_username = username.strip().lower()
    if not normalized_username:
        raise ValueError("Username is required")

    existing_user = await users_collection.find_one({"username": normalized_username})
    if existing_user:
        raise ValueError("Username already exists")

    result = await users_collection.insert_one(
        {
            "username": normalized_username,
            "password_hash": _hash_password(password),
            "created_at": _now(),
        }
    )
    return {"_id": str(result.inserted_id), "username": normalized_username}


async def authenticate_user(username: str, password: str) -> dict | None:
    normalized_username = username.strip().lower()
    user = await users_collection.find_one({"username": normalized_username})
    if not user or not _verify_password(password, user.get("password_hash", "")):
        return None

    return {"_id": str(user["_id"]), "username": user["username"]}


async def create_session(user: dict) -> str:
    token = secrets.token_urlsafe(32)
    await sessions_collection.insert_one(
        {
            "token": token,
            "user_id": user["_id"],
            "username": user["username"],
            "created_at": _now(),
        }
    )
    return token


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Login required")

    session = await sessions_collection.find_one({"token": credentials.credentials})
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired login")

    return {"_id": session["user_id"], "username": session["username"]}
