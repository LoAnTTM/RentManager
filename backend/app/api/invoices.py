"""
Invoice API - Quản lý hóa đơn
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import List, Optional
from decimal import Decimal
from app.core.database import get_db
from app.models.invoice import Invoice, InvoiceStatus
from app.models.room import Room, RoomStatus
from app.models.location import Location
from app.models.meter import Meter, MeterReading, MeterType
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceGenerate
from app.api.deps import get_current_user

router = APIRouter(prefix="/invoices", tags=["Hóa đơn"])


@router.get("", response_model=List[InvoiceResponse])
def get_invoices(
    month: Optional[int] = Query(None, description="Tháng"),
    year: Optional[int] = Query(None, description="Năm"),
    location_id: Optional[int] = Query(None, description="Khu trọ"),
    status: Optional[InvoiceStatus] = Query(None, description="Trạng thái"),
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user)
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
    _: None = Depends(get_current_user)
):
    """Tạo hóa đơn tháng tự động"""
    # Get rooms to generate invoices for
    query = db.query(Room).filter(Room.status == RoomStatus.OCCUPIED)
    if invoice_gen.location_id:
        query = query.filter(Room.location_id == invoice_gen.location_id)
    
    rooms = query.options(joinedload(Room.location)).all()
    
    created = []
    skipped = []
    
    for room in rooms:
        # Check if invoice already exists
        existing = db.query(Invoice).filter(
            Invoice.room_id == room.id,
            Invoice.month == invoice_gen.month,
            Invoice.year == invoice_gen.year
        ).first()
        
        if existing:
            skipped.append(room.room_code)
            continue
        
        # Get meter readings for this month
        electric_fee = Decimal("0")
        water_fee = Decimal("0")
        
        # Electric
        electric_meter = db.query(Meter).filter(
            Meter.room_id == room.id,
            Meter.meter_type == MeterType.ELECTRIC
        ).first()
        if electric_meter:
            reading = db.query(MeterReading).filter(
                MeterReading.meter_id == electric_meter.id,
                MeterReading.month == invoice_gen.month,
                MeterReading.year == invoice_gen.year
            ).first()
            if reading and reading.consumption:
                electric_fee = reading.consumption * room.location.electric_price
        
        # Water
        water_meter = db.query(Meter).filter(
            Meter.room_id == room.id,
            Meter.meter_type == MeterType.WATER
        ).first()
        if water_meter:
            reading = db.query(MeterReading).filter(
                MeterReading.meter_id == water_meter.id,
                MeterReading.month == invoice_gen.month,
                MeterReading.year == invoice_gen.year
            ).first()
            if reading and reading.consumption:
                water_fee = reading.consumption * room.location.water_price
        
        # Create invoice
        room_fee = room.price
        total = room_fee + electric_fee + water_fee
        
        invoice = Invoice(
            room_id=room.id,
            month=invoice_gen.month,
            year=invoice_gen.year,
            room_fee=room_fee,
            electric_fee=electric_fee,
            water_fee=water_fee,
            total=total
        )
        db.add(invoice)
        created.append(room.room_code)
    
    db.commit()
    
    return {
        "message": f"Đã tạo {len(created)} hóa đơn",
        "created": created,
        "skipped": skipped
    }


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user)
):
    """Lấy chi tiết hóa đơn"""
    invoice = db.query(Invoice).options(joinedload(Invoice.room)).filter(Invoice.id == invoice_id).first()
    
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
    _: None = Depends(get_current_user)
):
    """Cập nhật hóa đơn"""
    invoice = db.query(Invoice).options(joinedload(Invoice.room)).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hóa đơn",
        )
    
    update_data = invoice_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(invoice, field, value)
    
    # Recalculate total
    invoice.total = invoice.room_fee + invoice.electric_fee + invoice.water_fee + invoice.other_fee
    
    db.commit()
    db.refresh(invoice)
    
    return invoice


@router.put("/{invoice_id}/pay", response_model=InvoiceResponse)
def mark_invoice_paid(
    invoice_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user)
):
    """Đánh dấu đã thu tiền"""
    invoice = db.query(Invoice).options(joinedload(Invoice.room)).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hóa đơn",
        )
    
    invoice.status = InvoiceStatus.PAID
    invoice.paid_amount = invoice.total
    
    db.commit()
    db.refresh(invoice)
    
    return invoice

