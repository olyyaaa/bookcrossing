from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.exchange import ExchangeRequest, RequestStatus
from app.models.book import Book, BookStatus
from app.models.notification import Notification
from app.models.user import User
from app.schemas.exchange import ExchangeCreate, ExchangeOut
from app.auth import get_current_user

router = APIRouter(prefix="/api/v1/exchanges", tags=["Обміни"])

@router.post("/", response_model=ExchangeOut, status_code=201)
def create_exchange(
    data: ExchangeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    book = db.query(Book).filter(Book.id == data.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книгу не знайдено")
    if book.status != BookStatus.available:
        raise HTTPException(status_code=400, detail="Книга недоступна для обміну")
    if book.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="Не можна запитати власну книгу")

    request = ExchangeRequest(
        book_id=book.id,
        sender_id=current_user.id,
        owner_id=book.owner_id,
        comment=data.comment
    )
    db.add(request)

    book.status = BookStatus.reserved

    notification = Notification(
        user_id=book.owner_id,
        message=f"Користувач {current_user.name} хоче отримати вашу книгу «{book.title}»"
    )
    db.add(notification)
    db.commit()
    db.refresh(request)
    return request

@router.get("/my", response_model=List[ExchangeOut])
def get_my_exchanges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(ExchangeRequest).filter(
        (ExchangeRequest.sender_id == current_user.id) |
        (ExchangeRequest.owner_id == current_user.id)
    ).all()

@router.patch("/{request_id}/approve", response_model=ExchangeOut)
def approve_exchange(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    req = db.query(ExchangeRequest).filter(ExchangeRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Запит не знайдено")
    if req.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Немає прав")
    if req.status != RequestStatus.pending:
        raise HTTPException(status_code=400, detail="Запит вже оброблено")

    req.status = RequestStatus.approved

    notification = Notification(
        user_id=req.sender_id,
        message=f"Ваш запит на книгу схвалено! Зв'яжіться з власником для передачі."
    )
    db.add(notification)
    db.commit()
    db.refresh(req)
    return req

@router.patch("/{request_id}/reject", response_model=ExchangeOut)
def reject_exchange(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    req = db.query(ExchangeRequest).filter(ExchangeRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Запит не знайдено")
    if req.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Немає прав")
    if req.status != RequestStatus.pending:
        raise HTTPException(status_code=400, detail="Запит вже оброблено")

    req.status = RequestStatus.rejected

    book = db.query(Book).filter(Book.id == req.book_id).first()
    if book:
        book.status = BookStatus.available

    notification = Notification(
        user_id=req.sender_id,
        message=f"На жаль, ваш запит на книгу відхилено."
    )
    db.add(notification)
    db.commit()
    db.refresh(req)
    return req

@router.patch("/{request_id}/complete", response_model=ExchangeOut)
def complete_exchange(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    req = db.query(ExchangeRequest).filter(ExchangeRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Запит не знайдено")
    if req.sender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Немає прав")
    if req.status != RequestStatus.approved:
        raise HTTPException(status_code=400, detail="Запит не схвалено")

    req.status = RequestStatus.completed

    book = db.query(Book).filter(Book.id == req.book_id).first()
    if book:
        book.status = BookStatus.exchanged

    notification = Notification(
        user_id=req.owner_id,
        message=f"Передачу книги підтверджено. Обмін завершено!"
    )
    db.add(notification)
    db.commit()
    db.refresh(req)
    return req