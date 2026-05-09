from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ExchangeCreate(BaseModel):
    book_id: int
    comment: Optional[str] = None

class ExchangeUpdate(BaseModel):
    status: str

class ExchangeOut(BaseModel):
    id: int
    book_id: int
    sender_id: int
    owner_id: int
    status: str
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True