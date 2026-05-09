from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LocationIn(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None

class LocationOut(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None

    class Config:
        from_attributes = True

class BookCreate(BaseModel):
    title: str
    author: str
    genre: Optional[str] = None
    description: Optional[str] = None
    latitude: float
    longitude: float
    address: Optional[str] = None

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None
    description: Optional[str] = None

class BookOut(BaseModel):
    id: int
    title: str
    author: str
    genre: Optional[str] = None
    description: Optional[str] = None
    status: str
    photo_url: Optional[str] = None
    owner_id: int
    added_at: datetime
    location: Optional[LocationOut] = None

    class Config:
        from_attributes = True