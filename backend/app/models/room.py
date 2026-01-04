"""
Room model - Phòng trọ
"""

import enum

from sqlalchemy import (Column, DateTime, Enum, ForeignKey, Integer, Numeric,
                        String, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class RoomStatus(str, enum.Enum):
    VACANT = "vacant"  # Trống
    OCCUPIED = "occupied"  # Đang thuê


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    room_type_id = Column(
        Integer, ForeignKey("room_types.id")
    )  # Loại phòng (A, B, C...)
    room_code = Column(String(20), nullable=False)  # Mã phòng: "101", "102", "số1"
    price = Column(Numeric(10, 0))  # Giá phòng riêng (nếu khác loại phòng)
    status = Column(Enum(RoomStatus), default=RoomStatus.VACANT)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    location = relationship("Location", back_populates="rooms")
    room_type = relationship("RoomType", back_populates="rooms")
    tenants = relationship(
        "Tenant", back_populates="room", cascade="all, delete-orphan"
    )
    meters = relationship("Meter", back_populates="room", cascade="all, delete-orphan")
    invoices = relationship(
        "Invoice", back_populates="room", cascade="all, delete-orphan"
    )

    @property
    def effective_price(self):
        """Lấy giá phòng thực tế (ưu tiên giá riêng, không thì lấy giá từ loại phòng)"""
        if self.price:
            return self.price
        if self.room_type:
            return self.room_type.price
        return 0

    @property
    def daily_deduction(self):
        """Lấy tiền trừ/ngày nghỉ từ loại phòng"""
        if self.room_type:
            return self.room_type.daily_deduction
        return 0
