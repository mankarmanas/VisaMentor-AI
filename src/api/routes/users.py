from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from pydantic import BaseModel
from datetime import date
from src.db.database import get_db
from src.db.crud import UserCRUD

router = APIRouter()


class UserProfileRequest(BaseModel):
    email: str
    name: str
    photo_url: str
    university: str
    program: str
    program_end_date: str
    stem_eligible: bool


class UserProfileUpdateRequest(BaseModel):
    university: str
    program: str
    program_start_date: str
    program_end_date: str
    stem_eligible: bool


@router.post("/users/register")
async def register_user(request: UserProfileRequest, x_user_uid: Optional[str] = Header(None)):
    """Called on first login — saves name, email, photo to DB."""
    if not x_user_uid:
        raise HTTPException(status_code=401, detail="Not authorized")

    db = next(get_db())
    try:
        user = UserCRUD.get_by_uid(db, x_user_uid)
        if not user:
            user = UserCRUD.create(
                db=db,
                uid=x_user_uid,
                email=request.email,
                name=request.name,
                photo_url=request.photo_url,
            )
        return {"message": "User registered", "has_profile": UserCRUD.has_profile(db, x_user_uid)}
    finally:
        db.close()


@router.post("/users/profile")
async def save_profile(request: UserProfileUpdateRequest, x_user_uid: Optional[str] = Header(None)):
    """Save or update profile — university, program, dates."""
    if not x_user_uid:
        raise HTTPException(status_code=401, detail="Not authorized")

    db = next(get_db())
    try:
        user = UserCRUD.update_profile(
            db=db,
            uid=x_user_uid,
            university=request.university,
            program=request.program,
            program_start_date=date.fromisoformat(request.program_start_date),
            program_end_date=date.fromisoformat(request.program_end_date),
            stem_eligible=request.stem_eligible,
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "Profile saved"}
    finally:
        db.close()


@router.get("/users/profile")
async def get_profile(x_user_uid: Optional[str] = Header(None)):
    """Get current profile — used to pre-fill settings form."""
    if not x_user_uid:
        raise HTTPException(status_code=401, detail="Not authorized")

    db = next(get_db())
    try:
        user = UserCRUD.get_by_uid(db, x_user_uid)
        if not user:
            return {"has_profile": False}
        return {
            "has_profile": UserCRUD.has_profile(db, x_user_uid),
            "name": user.name,
            "email": user.email,
            "photo_url": user.photo_url,
            "university": user.university,
            "program": user.program,
            "program_start_date": user.program_start_date.isoformat() if user.program_start_date else None,
            "program_end_date": user.program_end_date.isoformat() if user.program_end_date else None,
            "stem_eligible": user.stem_eligible,
        }
    finally:
        db.close()