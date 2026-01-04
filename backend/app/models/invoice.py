"""
Invoice model - Hóa đơn
"""

from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.payment import Payment
    from app.models.room import Room


class InvoiceStatus(str, enum.Enum):
    UNPAID = "unpaid"  # Chưa thu
    PARTIAL = "partial"  # Thu một phần
    PAID = "paid"  # Đã thu đủ


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id"), nullable=False
    )
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)

    room_fee: Mapped[Decimal] = mapped_column(Numeric(12, 0), nullable=False)
    absent_days: Mapped[int] = mapped_column(Integer, default=0)
    absent_deduction: Mapped[Decimal] = mapped_column(
        Numeric(12, 0), default=0
    )

    electric_fee: Mapped[Decimal] = mapped_column(Numeric(12, 0), default=0)
    water_fee: Mapped[Decimal] = mapped_column(Numeric(12, 0), default=0)

    garbage_fee: Mapped[Decimal] = mapped_column(Numeric(12, 0), default=0)
    wifi_fee: Mapped[Decimal] = mapped_column(Numeric(12, 0), default=0)
    tv_fee: Mapped[Decimal] = mapped_column(Numeric(12, 0), default=0)
    laundry_fee: Mapped[Decimal] = mapped_column(Numeric(12, 0), default=0)

    other_fee: Mapped[Decimal] = mapped_column(Numeric(12, 0), default=0)
    other_fee_note: Mapped[Optional[str]] = mapped_column(String(255))

    previous_debt: Mapped[Decimal] = mapped_column(Numeric(12, 0), default=0)
    previous_credit: Mapped[Decimal] = mapped_column(Numeric(12, 0), default=0)

    total: Mapped[Decimal] = mapped_column(Numeric(12, 0), nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(12, 0), default=0)
    remaining_debt: Mapped[Decimal] = mapped_column(Numeric(12, 0), default=0)
    remaining_credit: Mapped[Decimal] = mapped_column(
        Numeric(12, 0), default=0
    )

    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus), default=InvoiceStatus.UNPAID
    )
    payment_date: Mapped[Optional[date]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    room: Mapped[Room] = relationship("Room", back_populates="invoices")
    payments: Mapped[list[Payment]] = relationship(
        "Payment", back_populates="invoice", cascade="all, delete-orphan"
    )

    def calculate_total(self) -> Decimal:
        """Tính tổng tiền hóa đơn"""
        room_after_deduction = self.room_fee - self.absent_deduction
        fees_total = (
            room_after_deduction
            + self.electric_fee
            + self.water_fee
            + self.garbage_fee
            + self.wifi_fee
            + self.tv_fee
            + self.laundry_fee
            + self.other_fee
            + self.previous_debt
            - self.previous_credit
        )
        return max(fees_total, Decimal("0"))
