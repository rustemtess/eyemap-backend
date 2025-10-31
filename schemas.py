from pydantic import BaseModel, Field, confloat
from typing import Optional
from datetime import datetime

class ReportCreate(BaseModel):
    description: str = Field(..., min_length=3, max_length=2000)
    latitude: confloat(ge=-90, le=90)
    longitude: confloat(ge=-180, le=180)
    category: Optional[str] = None
    source: Optional[str] = None,
    telegram_user_id: Optional[int] = None  # ✅ Добавь

class ReportOut(BaseModel):
    id: int
    description: str
    latitude: float
    longitude: float
    category: Optional[str]
    source: Optional[str]
    cluster_id: Optional[int]
    has_photo: bool = False
    created_at: datetime
    telegram_user_id: Optional[int] = None  # ✅ Добавь

    class Config:
        orm_mode = True
