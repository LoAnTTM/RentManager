"""
RoomType model - Loại phòng
"""

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, Numeric, String,
                        Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class RoomType(Base):
    __tablename__ = "room_types"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    code = Column(String(10), nullable=False)  # Mã loại: A, B, C, D, E, F, G, H
    name = Column(String(50))  # Tên loại: "Loại A", "Phòng VIP"
    price = Column(Numeric(12, 0), nullable=False)  # Giá thuê/tháng
    daily_deduction = Column(Numeric(10, 0), default=0)  # Tiền trừ mỗi ngày nghỉ
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    location = relationship("Location", back_populates="room_types")
    rooms = relationship("Room", back_populates="room_type")
