"""
Invoice model - Hóa đơn
"""

import enum

from sqlalchemy import (
    Column,
    Date,
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

    # Tiền phòng
    room_fee = Column(Numeric(12, 0), nullable=False)  # Tiền phòng gốc
    absent_days = Column(Integer, default=0)  # Số ngày vắng/nghỉ
    absent_deduction = Column(Numeric(12, 0), default=0)  # Tiền trừ do vắng

    # Tiền điện nước
    electric_fee = Column(Numeric(12, 0), default=0)  # Tiền điện
    water_fee = Column(Numeric(12, 0), default=0)  # Tiền nước

    # Phí cố định
    garbage_fee = Column(Numeric(12, 0), default=0)  # Tiền rác
    wifi_fee = Column(Numeric(12, 0), default=0)  # Tiền wifi
    tv_fee = Column(Numeric(12, 0), default=0)  # Tiền TV
    laundry_fee = Column(Numeric(12, 0), default=0)  # Tiền giặt

    # Phí khác và phụ thu
    other_fee = Column(Numeric(12, 0), default=0)  # Phí phụ thu
    other_fee_note = Column(String(255))  # Ghi chú phí phụ thu

    # Nợ/thừa chuyển kỳ
    previous_debt = Column(
        Numeric(12, 0), default=0
    )  # Nợ tháng trước (số dương)
    previous_credit = Column(
        Numeric(12, 0), default=0
    )  # Thừa tháng trước (số dương)

    # Tổng và thanh toán
    total = Column(Numeric(12, 0), nullable=False)  # Tổng tiền phải nộp
    paid_amount = Column(Numeric(12, 0), default=0)  # Số tiền đã nộp
    remaining_debt = Column(
        Numeric(12, 0), default=0
    )  # Nợ lại (chuyển sang tháng sau)
    remaining_credit = Column(
        Numeric(12, 0), default=0
    )  # Thừa lại (chuyển sang tháng sau)

    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.UNPAID)
    payment_date = Column(Date)  # Ngày nộp tiền
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    room = relationship("Room", back_populates="invoices")
    payments = relationship(
        "Payment", back_populates="invoice", cascade="all, delete-orphan"
    )

    def calculate_total(self):
        """Tính tổng tiền hóa đơn"""
        # Tiền phòng sau khi trừ ngày vắng
        room_after_deduction = self.room_fee - self.absent_deduction

        # Tổng các khoản phí
        fees_total = (
            room_after_deduction
            + self.electric_fee
            + self.water_fee
            + self.garbage_fee
            + self.wifi_fee
            + self.tv_fee
            + self.laundry_fee
            + self.other_fee
            + self.previous_debt
            - self.previous_credit
        )

        return max(fees_total, 0)  # Không âm
