"""
Dashboard API - Thống kê tổng quan
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import extract, func
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.expense import Expense
from app.models.invoice import Invoice, InvoiceStatus
from app.models.location import Location
from app.models.room import Room, RoomStatus
from app.models.tenant import Tenant
from app.schemas.dashboard import DashboardStats, MonthlyReport, UnpaidInvoice

router = APIRouter(prefix="/dashboard", tags=["Tổng quan"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db), _: None = Depends(get_current_user)
):
    """Lấy thống kê tổng quan"""
    now = datetime.now()
    current_month = now.month
    current_year = now.year

    # Room stats
    total_rooms = db.query(Room).count()
    occupied_rooms = (
        db.query(Room).filter(Room.status == RoomStatus.OCCUPIED).count()
    )
    vacant_rooms = total_rooms - occupied_rooms

    # Tenant stats
    total_tenants = db.query(Tenant).filter(Tenant.is_active == True).count()

    # Invoice stats for current month
    invoices_this_month = (
        db.query(Invoice)
        .filter(Invoice.month == current_month, Invoice.year == current_year)
        .all()
    )

    total_income = sum(inv.total for inv in invoices_this_month) or Decimal(
        "0"
    )
    total_paid = sum(
        inv.paid_amount for inv in invoices_this_month
    ) or Decimal("0")
    total_unpaid = total_income - total_paid

    # Expense stats for current month
    total_expense = db.query(func.sum(Expense.amount)).filter(
        extract("month", Expense.expense_date) == current_month,
        extract("year", Expense.expense_date) == current_year,
    ).scalar() or Decimal("0")

    return DashboardStats(
        total_rooms=total_rooms,
        occupied_rooms=occupied_rooms,
        vacant_rooms=vacant_rooms,
        total_tenants=total_tenants,
        total_income_this_month=total_income,
        total_paid_this_month=total_paid,
        total_unpaid_this_month=total_unpaid,
        total_expense_this_month=total_expense,
    )


@router.get("/report", response_model=MonthlyReport)
def get_monthly_report(
    month: int = Query(..., description="Tháng"),
    year: int = Query(..., description="Năm"),
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Lấy báo cáo tháng"""
    # Get all invoices for the month
    invoices = (
        db.query(Invoice)
        .options(joinedload(Invoice.room).joinedload(Room.location))
        .filter(Invoice.month == month, Invoice.year == year)
        .all()
    )

    total_income = sum(inv.total for inv in invoices) or Decimal("0")
    total_collected = sum(inv.paid_amount for inv in invoices) or Decimal("0")
    total_pending = total_income - total_collected

    # Get expenses for the month
    total_expense = db.query(func.sum(Expense.amount)).filter(
        extract("month", Expense.expense_date) == month,
        extract("year", Expense.expense_date) == year,
    ).scalar() or Decimal("0")

    net_income = total_collected - total_expense

    # Get unpaid invoices
    unpaid_invoices = []
    for inv in invoices:
        if inv.status != InvoiceStatus.PAID:
            remaining = inv.total - inv.paid_amount
            unpaid_invoices.append(
                UnpaidInvoice(
                    id=inv.id,
                    room_code=inv.room.room_code,
                    location_name=inv.room.location.name,
                    total=inv.total,
                    paid_amount=inv.paid_amount,
                    remaining=remaining,
                )
            )

    return MonthlyReport(
        month=month,
        year=year,
        total_income=total_income,
        total_collected=total_collected,
        total_pending=total_pending,
        total_expense=total_expense,
        net_income=net_income,
        unpaid_invoices=unpaid_invoices,
    )
