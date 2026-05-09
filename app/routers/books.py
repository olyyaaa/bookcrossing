from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import math, os, shutil, uuid
from app.database import get_db
from app.models.book import Book, BookLocation, BookStatus
from app.models.user import User
from app.schemas.book import BookCreate, BookUpdate, BookOut
from app.auth import get_current_user

router = APIRouter(prefix="/api/v1/books", tags=["Книги"])

UPLOAD_DIR = "static/img/books"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

@router.get("/", response_model=List[BookOut])
def get_books(
    search: Optional[str] = Query(None),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    radius: Optional[float] = Query(10.0),
    db: Session = Depends(get_db)
):
    query = db.query(Book).filter(Book.status == BookStatus.available)

    if search:
        query = query.filter(
            (Book.title.ilike(f"%{search}%")) |
            (Book.author.ilike(f"%{search}%")) |
            (Book.genre.ilike(f"%{search}%"))
        )

    books = query.all()

    if lat is not None and lon is not None:
        books = [
            b for b in books
            if b.location and haversine(lat, lon, b.location.latitude, b.location.longitude) <= radius
        ]

    return books

@router.get("/{book_id}", response_model=BookOut)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книгу не знайдено")
    return book

@router.post("/", response_model=BookOut, status_code=201)
def create_book(
    data: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    book = Book(
        owner_id=current_user.id,
        title=data.title,
        author=data.author,
        genre=data.genre,
        description=data.description
    )
    db.add(book)
    db.flush()

    location = BookLocation(
        book_id=book.id,
        latitude=data.latitude,
        longitude=data.longitude,
        address=data.address
    )
    db.add(location)
    db.commit()
    db.refresh(book)
    return book

@router.put("/{book_id}", response_model=BookOut)
def update_book(
    book_id: int,
    data: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книгу не знайдено")
    if book.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Немає прав для редагування")

    if data.title is not None:
        book.title = data.title
    if data.author is not None:
        book.author = data.author
    if data.genre is not None:
        book.genre = data.genre
    if data.description is not None:
        book.description = data.description

    db.commit()
    db.refresh(book)
    return book

@router.delete("/{book_id}", status_code=204)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книгу не знайдено")
    if book.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Немає прав для видалення")
    db.delete(book)
    db.commit()

@router.post("/{book_id}/photo")
def upload_photo(
    book_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книгу не знайдено")
    if book.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Немає прав")

    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    book.photo_url = f"/static/img/books/{filename}"
    db.commit()
    return {"photo_url": book.photo_url}