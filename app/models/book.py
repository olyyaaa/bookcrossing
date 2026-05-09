from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum

class BookStatus(str, enum.Enum):
    available = "available"
    reserved = "reserved"
    exchanged = "exchanged"

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    author = Column(String(150), nullable=False)
    genre = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(BookStatus), default=BookStatus.available, index=True)
    photo_url = Column(String(500), nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="books", foreign_keys=[owner_id])
    location = relationship("BookLocation", back_populates="book", uselist=False, cascade="all, delete-orphan")
    requests = relationship("ExchangeRequest", back_populates="book")
    reviews = relationship("Review", back_populates="book")

class BookLocation(Base):
    __tablename__ = "book_locations"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), unique=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(300), nullable=True)

    book = relationship("Book", back_populates="location")