"""
Expense model - Chi tiêu
"""

from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.location import Location


class ExpenseCategory(str, enum.Enum):
    REPAIR = "repair"  # Sửa chữa
    UTILITY = "utility"  # Điện nước chung
    MAINTENANCE = "maintenance"  # Bảo trì
    OTHER = "other"  # Khác


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    location_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id")
    )
    category: Mapped[ExpenseCategory] = mapped_column(
        Enum(ExpenseCategory), default=ExpenseCategory.OTHER
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 0), nullable=False)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    location: Mapped[Optional[Location]] = relationship(
        "Location", back_populates="expenses"
    )
