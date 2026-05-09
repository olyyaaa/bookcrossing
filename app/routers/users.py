from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate
from app.auth import get_current_user

router = APIRouter(prefix="/api/v1/users", tags=["Користувачі"])

@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserOut)
def update_my_profile(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if data.name is not None:
        current_user.name = data.name
    if data.city is not None:
        current_user.city = data.city
    if data.latitude is not None:
        current_user.latitude = data.latitude
    if data.longitude is not None:
        current_user.longitude = data.longitude
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    return user