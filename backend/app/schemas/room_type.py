"""
RoomType schemas - Loại phòng
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class RoomTypeBase(BaseModel):
    location_id: int
    code: str  # A, B, C, D, E, F, G, H
    name: Optional[str] = None
    price: Decimal
    daily_deduction: Decimal = Decimal("0")  # Tiền trừ/ngày nghỉ
    description: Optional[str] = None


class RoomTypeCreate(RoomTypeBase):
    pass


class RoomTypeUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    price: Optional[Decimal] = None
    daily_deduction: Optional[Decimal] = None
    description: Optional[str] = None


class RoomTypeResponse(RoomTypeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
