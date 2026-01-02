"""
Location schemas - Khu trọ
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal


class LocationBase(BaseModel):
    name: str
    address: Optional[str] = None
    electric_price: Decimal = Decimal("3500")  # Giá điện mặc định
    water_price: Decimal = Decimal("15000")  # Giá nước mặc định
    notes: Optional[str] = None


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    electric_price: Optional[Decimal] = None
    water_price: Optional[Decimal] = None
    notes: Optional[str] = None


class LocationResponse(LocationBase):
    id: int
    created_at: datetime
    room_count: Optional[int] = 0
    occupied_count: Optional[int] = 0

    class Config:
        from_attributes = True

