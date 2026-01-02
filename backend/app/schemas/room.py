"""
Room schemas - Phòng trọ
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from app.models.room import RoomStatus


class RoomBase(BaseModel):
    location_id: int
    room_code: str
    price: Decimal
    notes: Optional[str] = None


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
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


class LocationBrief(BaseModel):
    id: int
    name: str
    electric_price: Decimal
    water_price: Decimal

    class Config:
        from_attributes = True


class RoomResponse(RoomBase):
    id: int
    status: RoomStatus
    created_at: datetime
    location: Optional[LocationBrief] = None

    class Config:
        from_attributes = True


class RoomWithDetails(RoomResponse):
    tenants: List[TenantBrief] = []

    class Config:
        from_attributes = True

