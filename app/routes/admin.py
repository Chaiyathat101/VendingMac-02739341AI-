from fastapi import APIRouter, HTTPException

from app.config import ADMIN_PASSWORD, ADMIN_USERNAME
from app.models import AdminLoginRequest

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/login")
def login(payload: AdminLoginRequest):
    if payload.username == ADMIN_USERNAME and payload.password == ADMIN_PASSWORD:
        return {"message": "Login successful", "role": "admin"}
    raise HTTPException(status_code=401, detail="Invalid credentials")
