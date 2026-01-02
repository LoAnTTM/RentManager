"""
Tenant model - Người thuê trọ
"""
from sqlalchemy import Column, Integer, String, Text, Date, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    full_name = Column(String(100), nullable=False)  # Họ tên
    phone = Column(String(20))  # Số điện thoại
    id_card = Column(String(20))  # CCCD/CMND
    move_in_date = Column(Date, nullable=False)  # Ngày vào ở
    move_out_date = Column(Date)  # Ngày trả phòng
    is_active = Column(Boolean, default=True)  # Còn đang thuê không
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    room = relationship("Room", back_populates="tenants")

