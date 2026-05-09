from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReviewCreate(BaseModel):
    book_id: int
    rating: int = Field(..., ge=1, le=5)
    text: Optional[str] = None

class ReviewOut(BaseModel):
    id: int
    book_id: int
    user_id: int
    rating: int
    text: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True