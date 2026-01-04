"""
Location model - Khu trọ
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.expense import Expense
    from app.models.room import Room
    from app.models.room_type import RoomType


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(255))

    owner_name: Mapped[Optional[str]] = mapped_column(String(100))
    owner_phone: Mapped[Optional[str]] = mapped_column(String(50))

    electric_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=3500
    )
    water_price: Mapped[Decimal] = mapped_column(Numeric(10, 0), default=8000)

    garbage_fee: Mapped[Decimal] = mapped_column(Numeric(10, 0), default=30000)
    wifi_fee: Mapped[Decimal] = mapped_column(Numeric(10, 0), default=0)
    tv_fee: Mapped[Decimal] = mapped_column(Numeric(10, 0), default=0)
    laundry_fee: Mapped[Decimal] = mapped_column(Numeric(10, 0), default=0)

    payment_due_day: Mapped[int] = mapped_column(Integer, default=5)

    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    rooms: Mapped[list[Room]] = relationship(
        "Room", back_populates="location", cascade="all, delete-orphan"
    )
    room_types: Mapped[list[RoomType]] = relationship(
        "RoomType", back_populates="location", cascade="all, delete-orphan"
    )
    expenses: Mapped[list[Expense]] = relationship(
        "Expense", back_populates="location", cascade="all, delete-orphan"
    )
