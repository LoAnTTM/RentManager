"""
Invoice schemas - Hóa đơn
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.models.invoice import InvoiceStatus


class InvoiceGenerate(BaseModel):
    """Schema để tạo hóa đơn tháng"""

    month: int
    year: int
    location_id: Optional[int] = None


class InvoiceCreate(BaseModel):
    room_id: int
    month: int
    year: int
    room_fee: Decimal
    absent_days: int = 0
    absent_deduction: Decimal = Decimal("0")
    electric_fee: Decimal = Decimal("0")
    water_fee: Decimal = Decimal("0")
    garbage_fee: Decimal = Decimal("0")
    wifi_fee: Decimal = Decimal("0")
    tv_fee: Decimal = Decimal("0")
    laundry_fee: Decimal = Decimal("0")
    other_fee: Decimal = Decimal("0")
    other_fee_note: Optional[str] = None
    previous_debt: Decimal = Decimal("0")
    previous_credit: Decimal = Decimal("0")
    notes: Optional[str] = None


class InvoiceUpdate(BaseModel):
    room_fee: Optional[Decimal] = None
    absent_days: Optional[int] = None
    absent_deduction: Optional[Decimal] = None
    electric_fee: Optional[Decimal] = None
    water_fee: Optional[Decimal] = None
    garbage_fee: Optional[Decimal] = None
    wifi_fee: Optional[Decimal] = None
    tv_fee: Optional[Decimal] = None
    laundry_fee: Optional[Decimal] = None
    other_fee: Optional[Decimal] = None
    other_fee_note: Optional[str] = None
    previous_debt: Optional[Decimal] = None
    previous_credit: Optional[Decimal] = None
    status: Optional[InvoiceStatus] = None
    payment_date: Optional[date] = None
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
    absent_days: int
    absent_deduction: Decimal
    electric_fee: Decimal
    water_fee: Decimal
    garbage_fee: Decimal
    wifi_fee: Decimal
    tv_fee: Decimal
    laundry_fee: Decimal
    other_fee: Decimal
    other_fee_note: Optional[str] = None
    previous_debt: Decimal
    previous_credit: Decimal
    total: Decimal
    paid_amount: Decimal
    remaining_debt: Decimal
    remaining_credit: Decimal
    status: InvoiceStatus
    payment_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime
    room: Optional[RoomBrief] = None

    class Config:
        from_attributes = True
