"""
Meter and MeterReading models - Đồng hồ điện nước
"""

from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
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
    from app.models.room import Room


class MeterType(str, enum.Enum):
    ELECTRIC = "electric"  # Điện
    WATER = "water"  # Nước


class Meter(Base):
    __tablename__ = "meters"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id"), nullable=False
    )
    meter_type: Mapped[MeterType] = mapped_column(
        Enum(MeterType), nullable=False
    )
    meter_code: Mapped[Optional[str]] = mapped_column(String(50))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    room: Mapped[Room] = relationship("Room", back_populates="meters")
    readings: Mapped[list["MeterReading"]] = relationship(
        "MeterReading", back_populates="meter", cascade="all, delete-orphan"
    )


class MeterReading(Base):
    __tablename__ = "meter_readings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    meter_id: Mapped[int] = mapped_column(
        ForeignKey("meters.id"), nullable=False
    )
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    old_reading: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    new_reading: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    consumption: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    meter: Mapped["Meter"] = relationship("Meter", back_populates="readings")
