"""
RoomType model - Loại phòng
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.location import Location
    from app.models.room import Room


class RoomType(Base):
    __tablename__ = "room_types"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(50))
    price: Mapped[Decimal] = mapped_column(Numeric(12, 0), nullable=False)
    daily_deduction: Mapped[Decimal] = mapped_column(Numeric(10, 0), default=0)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    location: Mapped[Location] = relationship(
        "Location", back_populates="room_types"
    )
    rooms: Mapped[list[Room]] = relationship(
        "Room", back_populates="room_type"
    )
