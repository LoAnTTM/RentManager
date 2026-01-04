"""
Room schemas - Phòng trọ
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel

from app.models.room import RoomStatus


class RoomBase(BaseModel):
    location_id: int
    room_type_id: Optional[int] = None
    room_code: str
    price: Optional[Decimal] = None  # Giá riêng (nếu khác loại phòng)
    notes: Optional[str] = None


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    room_type_id: Optional[int] = None
    room_code: Optional[str] = None
    price: Optional[Decimal] = None
    status: Optional[RoomStatus] = None
    notes: Optional[str] = None


class TenantBrief(BaseModel):
    id: int
    full_name: str
    phone: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class RoomTypeBrief(BaseModel):
    id: int
    code: str
    name: Optional[str] = None
    price: Decimal
    daily_deduction: Decimal

    class Config:
        from_attributes = True


class LocationBrief(BaseModel):
    id: int
    name: str
    electric_price: Decimal
    water_price: Decimal
    garbage_fee: Decimal
    wifi_fee: Decimal
    tv_fee: Decimal
    laundry_fee: Decimal

    class Config:
        from_attributes = True


class RoomResponse(RoomBase):
    id: int
    status: RoomStatus
    created_at: datetime
    location: Optional[LocationBrief] = None
    room_type: Optional[RoomTypeBrief] = None
    effective_price: Optional[Decimal] = None

    class Config:
        from_attributes = True


class RoomWithDetails(RoomResponse):
    tenants: List[TenantBrief] = []

    class Config:
        from_attributes = True
