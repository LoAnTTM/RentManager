"""
Tenant schemas - Người thuê
"""
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional


class TenantBase(BaseModel):
    room_id: int
    full_name: str
    phone: Optional[str] = None
    id_card: Optional[str] = None
    move_in_date: date
    notes: Optional[str] = None


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    room_id: Optional[int] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    id_card: Optional[str] = None
    move_in_date: Optional[date] = None
    move_out_date: Optional[date] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class RoomBrief(BaseModel):
    id: int
    room_code: str
    location_id: int

    class Config:
        from_attributes = True


class TenantResponse(TenantBase):
    id: int
    move_out_date: Optional[date] = None
    is_active: bool
    created_at: datetime
    room: Optional[RoomBrief] = None

    class Config:
        from_attributes = True

