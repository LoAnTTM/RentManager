"""
Room model - Phòng trọ
"""
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class RoomStatus(str, enum.Enum):
    VACANT = "vacant"  # Trống
    OCCUPIED = "occupied"  # Đang thuê


class Room(Base):
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    room_code = Column(String(20), nullable=False)  # Mã phòng: "101", "102"
    price = Column(Numeric(10, 0), nullable=False)  # Giá phòng (VND)
    status = Column(Enum(RoomStatus), default=RoomStatus.VACANT)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    location = relationship("Location", back_populates="rooms")
    tenants = relationship("Tenant", back_populates="room", cascade="all, delete-orphan")
    meters = relationship("Meter", back_populates="room", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="room", cascade="all, delete-orphan")

