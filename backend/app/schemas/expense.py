"""
Expense schemas - Chi tiêu
"""
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from decimal import Decimal
from app.models.expense import ExpenseCategory


class ExpenseBase(BaseModel):
    location_id: Optional[int] = None
    category: ExpenseCategory = ExpenseCategory.OTHER
    description: str
    amount: Decimal
    expense_date: date
    notes: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    location_id: Optional[int] = None
    category: Optional[ExpenseCategory] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    expense_date: Optional[date] = None
    notes: Optional[str] = None


class ExpenseResponse(ExpenseBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

