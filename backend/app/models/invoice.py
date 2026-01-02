"""
Invoice model - Hóa đơn
"""
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class InvoiceStatus(str, enum.Enum):
    UNPAID = "unpaid"  # Chưa thu
    PARTIAL = "partial"  # Thu một phần
    PAID = "paid"  # Đã thu đủ


class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    month = Column(Integer, nullable=False)  # Tháng
    year = Column(Integer, nullable=False)  # Năm
    room_fee = Column(Numeric(12, 0), nullable=False)  # Tiền phòng
    electric_fee = Column(Numeric(12, 0), default=0)  # Tiền điện
    water_fee = Column(Numeric(12, 0), default=0)  # Tiền nước
    other_fee = Column(Numeric(12, 0), default=0)  # Phí khác
    total = Column(Numeric(12, 0), nullable=False)  # Tổng tiền
    paid_amount = Column(Numeric(12, 0), default=0)  # Số tiền đã thu
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.UNPAID)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    room = relationship("Room", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")

