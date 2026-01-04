"""
Payment schemas - Thanh toán
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


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
