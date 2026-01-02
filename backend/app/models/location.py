"""
Location model - Khu trọ
"""
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # Tên khu: "Khu A", "Khu B"
    address = Column(String(255))  # Địa chỉ
    electric_price = Column(Numeric(10, 0), default=3500)  # Giá điện/kWh (VND)
    water_price = Column(Numeric(10, 0), default=15000)  # Giá nước/m3 (VND)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    rooms = relationship("Room", back_populates="location", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="location", cascade="all, delete-orphan")

