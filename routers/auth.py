from fastapi import APIRouter, HTTPException

from models import LoginRequest, RegisterRequest
from security import authenticate_user, create_session, create_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(payload: RegisterRequest):
    try:
        user = await create_user(payload.username, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    token = await create_session(user)
    return {"token": token, "user": user}


@router.post("/login")
async def login(payload: LoginRequest):
    user = await authenticate_user(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = await create_session(user)
    return {"token": token, "user": user}
