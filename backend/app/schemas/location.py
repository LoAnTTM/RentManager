"""
Location schemas - Khu trọ
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class RoomTypeInLocation(BaseModel):
    id: int
    code: str
    name: Optional[str] = None
    price: Decimal
    daily_deduction: Decimal

    class Config:
        from_attributes = True


class LocationBase(BaseModel):
    name: str
    address: Optional[str] = None
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    electric_price: Decimal = Decimal("3500")
    water_price: Decimal = Decimal("8000")
    garbage_fee: Decimal = Decimal("30000")
    wifi_fee: Decimal = Decimal("0")
    tv_fee: Decimal = Decimal("0")
    laundry_fee: Decimal = Decimal("0")
    payment_due_day: int = 5
    notes: Optional[str] = None


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    electric_price: Optional[Decimal] = None
    water_price: Optional[Decimal] = None
    garbage_fee: Optional[Decimal] = None
    wifi_fee: Optional[Decimal] = None
    tv_fee: Optional[Decimal] = None
    laundry_fee: Optional[Decimal] = None
    payment_due_day: Optional[int] = None
    notes: Optional[str] = None


class LocationResponse(LocationBase):
    id: int
    created_at: datetime
    room_count: Optional[int] = 0
    occupied_count: Optional[int] = 0
    room_types: Optional[List[RoomTypeInLocation]] = []

    class Config:
        from_attributes = True
