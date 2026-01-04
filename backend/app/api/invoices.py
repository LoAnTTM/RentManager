"""
Invoice API - Quản lý hóa đơn
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.invoice import Invoice, InvoiceStatus
from app.models.meter import Meter, MeterReading, MeterType
from app.models.room import Room, RoomStatus
from app.schemas.invoice import (
    InvoiceGenerate,
    InvoiceResponse,
    InvoiceUpdate,
)

router = APIRouter(prefix="/invoices", tags=["Hóa đơn"])


def get_previous_invoice(
    db: Session, room_id: int, month: int, year: int
) -> Optional[Invoice]:
    """Lấy hóa đơn tháng trước"""
    prev_month = month - 1
    prev_year = year
    if prev_month < 1:
        prev_month = 12
        prev_year -= 1

    return (
        db.query(Invoice)
        .filter(
            Invoice.room_id == room_id,
            Invoice.month == prev_month,
            Invoice.year == prev_year,
        )
        .first()
    )


@router.get("", response_model=List[InvoiceResponse])
def get_invoices(
    month: Optional[int] = Query(None, description="Tháng"),
    year: Optional[int] = Query(None, description="Năm"),
    location_id: Optional[int] = Query(None, description="Khu trọ"),
    status: Optional[InvoiceStatus] = Query(None, description="Trạng thái"),
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Lấy danh sách hóa đơn"""
    query = db.query(Invoice).options(joinedload(Invoice.room))

    if month:
        query = query.filter(Invoice.month == month)
    if year:
        query = query.filter(Invoice.year == year)
    if location_id:
        query = query.join(Room).filter(Room.location_id == location_id)
    if status:
        query = query.filter(Invoice.status == status)

    invoices = query.order_by(Invoice.year.desc(), Invoice.month.desc()).all()
    return invoices


@router.post("/generate", status_code=status.HTTP_201_CREATED)
def generate_invoices(
    invoice_gen: InvoiceGenerate,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Tạo hóa đơn tháng tự động"""
    # Get rooms to generate invoices for
    query = db.query(Room).filter(Room.status == RoomStatus.OCCUPIED)
    if invoice_gen.location_id:
        query = query.filter(Room.location_id == invoice_gen.location_id)

    rooms = query.options(
        joinedload(Room.location), joinedload(Room.room_type)
    ).all()

    created = []
    skipped = []

    for room in rooms:
        # Check if invoice already exists
        existing = (
            db.query(Invoice)
            .filter(
                Invoice.room_id == room.id,
                Invoice.month == invoice_gen.month,
                Invoice.year == invoice_gen.year,
            )
            .first()
        )

        if existing:
            skipped.append(room.room_code)
            continue

        location = room.location

        # Calculate room fee
        room_fee = (
            room.price
            if room.price
            else (room.room_type.price if room.room_type else Decimal("0"))
        )

        # Get meter readings for this month
        electric_fee = Decimal("0")
        water_fee = Decimal("0")

        # Electric
        electric_meter = (
            db.query(Meter)
            .filter(
                Meter.room_id == room.id,
                Meter.meter_type == MeterType.ELECTRIC,
            )
            .first()
        )
        if electric_meter:
            reading = (
                db.query(MeterReading)
                .filter(
                    MeterReading.meter_id == electric_meter.id,
                    MeterReading.month == invoice_gen.month,
                    MeterReading.year == invoice_gen.year,
                )
                .first()
            )
            if reading and reading.consumption:
                electric_fee = reading.consumption * location.electric_price

        # Water
        water_meter = (
            db.query(Meter)
            .filter(
                Meter.room_id == room.id, Meter.meter_type == MeterType.WATER
            )
            .first()
        )
        if water_meter:
            reading = (
                db.query(MeterReading)
                .filter(
                    MeterReading.meter_id == water_meter.id,
                    MeterReading.month == invoice_gen.month,
                    MeterReading.year == invoice_gen.year,
                )
                .first()
            )
            if reading and reading.consumption:
                water_fee = reading.consumption * location.water_price

        # Get previous invoice for debt/credit transfer
        previous_debt = Decimal("0")
        previous_credit = Decimal("0")
        prev_invoice = get_previous_invoice(
            db, room.id, invoice_gen.month, invoice_gen.year
        )
        if prev_invoice:
            previous_debt = prev_invoice.remaining_debt or Decimal("0")
            previous_credit = prev_invoice.remaining_credit or Decimal("0")

        # Fixed fees from location
        garbage_fee = location.garbage_fee or Decimal("0")
        wifi_fee = location.wifi_fee or Decimal("0")
        tv_fee = location.tv_fee or Decimal("0")
        laundry_fee = location.laundry_fee or Decimal("0")

        # Calculate total
        total = (
            room_fee
            + electric_fee
            + water_fee
            + garbage_fee
            + wifi_fee
            + tv_fee
            + laundry_fee
            + previous_debt
            - previous_credit
        )

        # Create invoice
        invoice = Invoice(
            room_id=room.id,
            month=invoice_gen.month,
            year=invoice_gen.year,
            room_fee=room_fee,
            absent_days=0,
            absent_deduction=Decimal("0"),
            electric_fee=electric_fee,
            water_fee=water_fee,
            garbage_fee=garbage_fee,
            wifi_fee=wifi_fee,
            tv_fee=tv_fee,
            laundry_fee=laundry_fee,
            other_fee=Decimal("0"),
            previous_debt=previous_debt,
            previous_credit=previous_credit,
            total=total,
        )
        db.add(invoice)
        created.append(room.room_code)

    db.commit()

    return {
        "message": f"Đã tạo {len(created)} hóa đơn",
        "created": created,
        "skipped": skipped,
    }


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Lấy chi tiết hóa đơn"""
    invoice = (
        db.query(Invoice)
        .options(joinedload(Invoice.room))
        .filter(Invoice.id == invoice_id)
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hóa đơn",
        )

    return invoice


@router.put("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: int,
    invoice_in: InvoiceUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Cập nhật hóa đơn"""
    invoice = (
        db.query(Invoice)
        .options(joinedload(Invoice.room))
        .filter(Invoice.id == invoice_id)
        .first()
    )
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hóa đơn",
        )

    update_data = invoice_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(invoice, field, value)

    # Recalculate total
    room_after_deduction = invoice.room_fee - invoice.absent_deduction
    invoice.total = (
        room_after_deduction
        + invoice.electric_fee
        + invoice.water_fee
        + invoice.garbage_fee
        + invoice.wifi_fee
        + invoice.tv_fee
        + invoice.laundry_fee
        + invoice.other_fee
        + invoice.previous_debt
        - invoice.previous_credit
    )

    # Calculate remaining debt/credit
    if invoice.paid_amount >= invoice.total:
        invoice.remaining_credit = invoice.paid_amount - invoice.total
        invoice.remaining_debt = Decimal("0")
    else:
        invoice.remaining_debt = invoice.total - invoice.paid_amount
        invoice.remaining_credit = Decimal("0")

    db.commit()
    db.refresh(invoice)

    return invoice


@router.put("/{invoice_id}/pay", response_model=InvoiceResponse)
def pay_invoice(
    invoice_id: int,
    amount: Optional[Decimal] = Query(
        None, description="Số tiền nộp (nếu không có thì nộp đủ)"
    ),
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Thu tiền hóa đơn"""
    invoice = (
        db.query(Invoice)
        .options(joinedload(Invoice.room))
        .filter(Invoice.id == invoice_id)
        .first()
    )
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hóa đơn",
        )

    # Default to full payment
    pay_amount = amount if amount is not None else invoice.total

    invoice.paid_amount = invoice.paid_amount + pay_amount
    invoice.payment_date = date.today()

    # Update status
    if invoice.paid_amount >= invoice.total:
        invoice.status = InvoiceStatus.PAID
        invoice.remaining_credit = invoice.paid_amount - invoice.total
        invoice.remaining_debt = Decimal("0")
    elif invoice.paid_amount > 0:
        invoice.status = InvoiceStatus.PARTIAL
        invoice.remaining_debt = invoice.total - invoice.paid_amount
        invoice.remaining_credit = Decimal("0")

    db.commit()
    db.refresh(invoice)

    return invoice


@router.put("/{invoice_id}/absent", response_model=InvoiceResponse)
def update_absent_days(
    invoice_id: int,
    absent_days: int = Query(..., description="Số ngày vắng"),
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Cập nhật số ngày vắng và tính tiền trừ"""
    invoice = (
        db.query(Invoice)
        .options(joinedload(Invoice.room).joinedload(Room.room_type))
        .filter(Invoice.id == invoice_id)
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hóa đơn",
        )

    # Get daily deduction from room type
    daily_deduction = Decimal("0")
    if invoice.room and invoice.room.room_type:
        daily_deduction = invoice.room.room_type.daily_deduction or Decimal(
            "0"
        )

    invoice.absent_days = absent_days
    invoice.absent_deduction = daily_deduction * absent_days

    # Recalculate total
    room_after_deduction = invoice.room_fee - invoice.absent_deduction
    invoice.total = (
        room_after_deduction
        + invoice.electric_fee
        + invoice.water_fee
        + invoice.garbage_fee
        + invoice.wifi_fee
        + invoice.tv_fee
        + invoice.laundry_fee
        + invoice.other_fee
        + invoice.previous_debt
        - invoice.previous_credit
    )

    # Recalculate remaining
    if invoice.paid_amount >= invoice.total:
        invoice.remaining_credit = invoice.paid_amount - invoice.total
        invoice.remaining_debt = Decimal("0")
        invoice.status = InvoiceStatus.PAID
    elif invoice.paid_amount > 0:
        invoice.remaining_debt = invoice.total - invoice.paid_amount
        invoice.remaining_credit = Decimal("0")
        invoice.status = InvoiceStatus.PARTIAL
    else:
        invoice.remaining_debt = invoice.total
        invoice.remaining_credit = Decimal("0")

    db.commit()
    db.refresh(invoice)

    return invoice
