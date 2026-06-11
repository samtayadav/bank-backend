import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.accounts import router as accounts_router
from routers.auth import router as auth_router
from routers.transfers import router as transfers_router

app = FastAPI()

allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts_router)
app.include_router(auth_router)
app.include_router(transfers_router)

@app.get("/")
async def root():
    return {"message": "Bank API Working!"}
