"""
Payment schemas - Thanh toán
"""
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from decimal import Decimal


class PaymentCreate(BaseModel):
    invoice_id: int
    amount: Decimal
    payment_date: date
    notes: Optional[str] = None


class PaymentResponse(BaseModel):
    id: int
    invoice_id: int
    amount: Decimal
    payment_date: date
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

