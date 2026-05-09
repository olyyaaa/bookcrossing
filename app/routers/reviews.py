from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewOut
from app.auth import get_current_user

router = APIRouter(prefix="/api/v1/reviews", tags=["Відгуки"])

@router.post("/", response_model=ReviewOut, status_code=201)
def create_review(
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(Review).filter(
        Review.book_id == data.book_id,
        Review.user_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ви вже залишили відгук для цієї книги")

    review = Review(
        book_id=data.book_id,
        user_id=current_user.id,
        rating=data.rating,
        text=data.text
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

@router.get("/book/{book_id}", response_model=List[ReviewOut])
def get_book_reviews(book_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.book_id == book_id).all()