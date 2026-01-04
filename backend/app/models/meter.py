"""
Meter and MeterReading models - Đồng hồ điện nước
"""

import enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class MeterType(str, enum.Enum):
    ELECTRIC = "electric"  # Điện
    WATER = "water"  # Nước


class Meter(Base):
    __tablename__ = "meters"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    meter_type = Column(Enum(MeterType), nullable=False)  # Loại đồng hồ
    meter_code = Column(String(50))  # Mã đồng hồ (nếu có)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    room = relationship("Room", back_populates="meters")
    readings = relationship(
        "MeterReading", back_populates="meter", cascade="all, delete-orphan"
    )


class MeterReading(Base):
    __tablename__ = "meter_readings"

    id = Column(Integer, primary_key=True, index=True)
    meter_id = Column(Integer, ForeignKey("meters.id"), nullable=False)
    month = Column(Integer, nullable=False)  # Tháng (1-12)
    year = Column(Integer, nullable=False)  # Năm
    old_reading = Column(Numeric(10, 2), nullable=False)  # Chỉ số cũ
    new_reading = Column(Numeric(10, 2), nullable=False)  # Chỉ số mới
    consumption = Column(Numeric(10, 2))  # Số tiêu thụ (tự tính)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    meter = relationship("Meter", back_populates="readings")
