"""
Dashboard schemas - Thống kê
"""
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal


class DashboardStats(BaseModel):
    total_rooms: int = 0
    occupied_rooms: int = 0
    vacant_rooms: int = 0
    total_tenants: int = 0
    total_income_this_month: Decimal = Decimal("0")
    total_paid_this_month: Decimal = Decimal("0")
    total_unpaid_this_month: Decimal = Decimal("0")
    total_expense_this_month: Decimal = Decimal("0")


class UnpaidInvoice(BaseModel):
    id: int
    room_code: str
    location_name: str
    total: Decimal
    paid_amount: Decimal
    remaining: Decimal


class MonthlyReport(BaseModel):
    month: int
    year: int
    total_income: Decimal = Decimal("0")
    total_collected: Decimal = Decimal("0")
    total_pending: Decimal = Decimal("0")
    total_expense: Decimal = Decimal("0")
    net_income: Decimal = Decimal("0")
    unpaid_invoices: List[UnpaidInvoice] = []

