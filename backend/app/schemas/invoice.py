"""
Invoice schemas - Hóa đơn
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from app.models.invoice import InvoiceStatus


class InvoiceGenerate(BaseModel):
    """Schema để tạo hóa đơn tháng"""
    month: int
    year: int
    location_id: Optional[int] = None  # Nếu không có thì tạo cho tất cả khu


class InvoiceCreate(BaseModel):
    room_id: int
    month: int
    year: int
    room_fee: Decimal
    electric_fee: Decimal = Decimal("0")
    water_fee: Decimal = Decimal("0")
    other_fee: Decimal = Decimal("0")
    notes: Optional[str] = None


class InvoiceUpdate(BaseModel):
    room_fee: Optional[Decimal] = None
    electric_fee: Optional[Decimal] = None
    water_fee: Optional[Decimal] = None
    other_fee: Optional[Decimal] = None
    status: Optional[InvoiceStatus] = None
    notes: Optional[str] = None


class RoomBrief(BaseModel):
    id: int
    room_code: str
    location_id: int

    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    id: int
    room_id: int
    month: int
    year: int
    room_fee: Decimal
    electric_fee: Decimal
    water_fee: Decimal
    other_fee: Decimal
    total: Decimal
    paid_amount: Decimal
    status: InvoiceStatus
    notes: Optional[str] = None
    created_at: datetime
    room: Optional[RoomBrief] = None

    class Config:
        from_attributes = True

