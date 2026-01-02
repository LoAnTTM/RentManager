"""
Expense model - Chi tiêu
"""
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Date, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ExpenseCategory(str, enum.Enum):
    REPAIR = "repair"  # Sửa chữa
    UTILITY = "utility"  # Điện nước chung
    MAINTENANCE = "maintenance"  # Bảo trì
    OTHER = "other"  # Khác


class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"))  # Khu trọ (có thể null nếu chi chung)
    category = Column(Enum(ExpenseCategory), default=ExpenseCategory.OTHER)
    description = Column(String(255), nullable=False)  # Mô tả
    amount = Column(Numeric(12, 0), nullable=False)  # Số tiền
    expense_date = Column(Date, nullable=False)  # Ngày chi
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    location = relationship("Location", back_populates="expenses")

