from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    city = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.user)
    created_at = Column(DateTime, default=datetime.utcnow)

    books = relationship("Book", back_populates="owner", foreign_keys="Book.owner_id")
    sent_requests = relationship("ExchangeRequest", back_populates="sender", foreign_keys="ExchangeRequest.sender_id")
    received_requests = relationship("ExchangeRequest", back_populates="owner", foreign_keys="ExchangeRequest.owner_id")
    reviews = relationship("Review", back_populates="user")
    notifications = relationship("Notification", back_populates="user")