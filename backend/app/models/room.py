"""
Room model - Phòng trọ
"""

from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.invoice import Invoice
    from app.models.location import Location
    from app.models.meter import Meter
    from app.models.room_type import RoomType
    from app.models.tenant import Tenant


class RoomStatus(str, enum.Enum):
    VACANT = "vacant"  # Trống
    OCCUPIED = "occupied"  # Đang thuê


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id"), nullable=False
    )
    room_type_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("room_types.id")
    )
    room_code: Mapped[str] = mapped_column(String(20), nullable=False)
    price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 0))
    status: Mapped[RoomStatus] = mapped_column(
        Enum(RoomStatus), default=RoomStatus.VACANT
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    location: Mapped[Location] = relationship(
        "Location", back_populates="rooms"
    )
    room_type: Mapped[Optional[RoomType]] = relationship(
        "RoomType", back_populates="rooms"
    )
    tenants: Mapped[list[Tenant]] = relationship(
        "Tenant", back_populates="room", cascade="all, delete-orphan"
    )
    meters: Mapped[list[Meter]] = relationship(
        "Meter", back_populates="room", cascade="all, delete-orphan"
    )
    invoices: Mapped[list[Invoice]] = relationship(
        "Invoice", back_populates="room", cascade="all, delete-orphan"
    )

    @property
    def effective_price(self) -> Decimal:
        """Giá thực tế: ưu tiên giá riêng, fallback giá loại phòng."""
        if self.price:
            return self.price
        if self.room_type:
            return self.room_type.price
        return Decimal("0")

    @property
    def daily_deduction(self) -> Decimal:
        """Lấy tiền trừ/ngày nghỉ từ loại phòng"""
        if self.room_type:
            return self.room_type.daily_deduction
        return Decimal("0")
