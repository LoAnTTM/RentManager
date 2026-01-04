"""
Location model - Khu trọ
"""

from sqlalchemy import Column, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(
        String(100), nullable=False
    )  # Tên khu: "Khu A", "68 Nguyễn Viết Xuân"
    address = Column(String(255))  # Địa chỉ

    # Thông tin chủ trọ
    owner_name = Column(String(100))  # Tên chủ trọ
    owner_phone = Column(String(50))  # SĐT chủ trọ

    # Giá điện nước
    electric_price = Column(Numeric(10, 2), default=3500)  # Giá điện/kWh (VND)
    water_price = Column(Numeric(10, 0), default=8000)  # Giá nước/m3 (VND)

    # Phí cố định hàng tháng (có thể để 0 nếu không thu)
    garbage_fee = Column(Numeric(10, 0), default=30000)  # Tiền rác
    wifi_fee = Column(Numeric(10, 0), default=0)  # Tiền wifi
    tv_fee = Column(Numeric(10, 0), default=0)  # Tiền TV
    laundry_fee = Column(Numeric(10, 0), default=0)  # Tiền giặt

    # Cấu hình
    payment_due_day = Column(
        Integer, default=5
    )  # Hạn nộp tiền (ngày trong tháng)

    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    rooms = relationship(
        "Room", back_populates="location", cascade="all, delete-orphan"
    )
    room_types = relationship(
        "RoomType", back_populates="location", cascade="all, delete-orphan"
    )
    expenses = relationship(
        "Expense", back_populates="location", cascade="all, delete-orphan"
    )
