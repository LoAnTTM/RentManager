"""
Meter API - Quản lý điện nước
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.meter import Meter, MeterReading, MeterType
from app.models.room import Room
from app.schemas.meter import (
    MeterCreate,
    MeterReadingBatch,
    MeterReadingCreate,
    MeterReadingResponse,
    MeterReadingUpdate,
    MeterResponse,
)

router = APIRouter(prefix="/meters", tags=["Điện nước"])


@router.get("", response_model=List[MeterResponse])
def get_meters(
    room_id: Optional[int] = Query(None, description="Lọc theo phòng"),
    meter_type: Optional[MeterType] = Query(None, description="Lọc theo loại"),
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Lấy danh sách đồng hồ"""
    query = db.query(Meter)

    if room_id:
        query = query.filter(Meter.room_id == room_id)
    if meter_type:
        query = query.filter(Meter.meter_type == meter_type)

    meters = query.all()

    result = []
    for meter in meters:
        # Get latest reading
        latest = (
            db.query(MeterReading)
            .filter(MeterReading.meter_id == meter.id)
            .order_by(MeterReading.year.desc(), MeterReading.month.desc())
            .first()
        )

        meter_data = MeterResponse.model_validate(meter)
        meter_data.latest_reading = latest.new_reading if latest else None
        result.append(meter_data)

    return result


@router.post(
    "", response_model=MeterResponse, status_code=status.HTTP_201_CREATED
)
def create_meter(
    meter_in: MeterCreate,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Thêm đồng hồ mới"""
    # Check room exists
    room = db.query(Room).filter(Room.id == meter_in.room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy phòng",
        )

    # Check if meter type already exists for room
    existing = (
        db.query(Meter)
        .filter(
            Meter.room_id == meter_in.room_id,
            Meter.meter_type == meter_in.meter_type,
        )
        .first()
    )
    if existing:
        existing_type = (
            "điện"
            if meter_in.meter_type == MeterType.ELECTRIC
            else "nước"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Phòng đã có đồng hồ {existing_type}",
        )

    meter = Meter(**meter_in.model_dump())
    db.add(meter)
    db.commit()
    db.refresh(meter)

    return meter


@router.get("/readings", response_model=List[MeterReadingResponse])
def get_readings(
    month: Optional[int] = Query(None, description="Tháng"),
    year: Optional[int] = Query(None, description="Năm"),
    room_id: Optional[int] = Query(None, description="Phòng"),
    meter_type: Optional[MeterType] = Query(None, description="Loại đồng hồ"),
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Lấy danh sách chỉ số"""
    query = db.query(MeterReading).join(Meter)

    if month:
        query = query.filter(MeterReading.month == month)
    if year:
        query = query.filter(MeterReading.year == year)
    if room_id:
        query = query.filter(Meter.room_id == room_id)
    if meter_type:
        query = query.filter(Meter.meter_type == meter_type)

    readings = query.order_by(
        MeterReading.year.desc(), MeterReading.month.desc()
    ).all()
    return readings


@router.post(
    "/readings",
    response_model=MeterReadingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_reading(
    reading_in: MeterReadingCreate,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Ghi chỉ số mới"""
    # Check meter exists
    meter = db.query(Meter).filter(Meter.id == reading_in.meter_id).first()
    if not meter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy đồng hồ",
        )

    # Check if reading for this month already exists
    existing = (
        db.query(MeterReading)
        .filter(
            MeterReading.meter_id == reading_in.meter_id,
            MeterReading.month == reading_in.month,
            MeterReading.year == reading_in.year,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Đã có chỉ số cho tháng này",
        )

    # Calculate consumption
    consumption = reading_in.new_reading - reading_in.old_reading
    if consumption < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ số mới phải lớn hơn chỉ số cũ",
        )

    reading = MeterReading(**reading_in.model_dump(), consumption=consumption)
    db.add(reading)
    db.commit()
    db.refresh(reading)

    return reading


@router.post("/readings/batch", status_code=status.HTTP_201_CREATED)
def create_readings_batch(
    batch: MeterReadingBatch,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Ghi chỉ số hàng loạt"""
    created = []
    errors = []

    for item in batch.readings:
        # Find meter
        meter = (
            db.query(Meter)
            .filter(
                Meter.room_id == item.room_id,
                Meter.meter_type == item.meter_type,
            )
            .first()
        )

        if not meter:
            errors.append(f"Không tìm thấy đồng hồ cho phòng {item.room_id}")
            continue

        # Check if reading exists
        existing = (
            db.query(MeterReading)
            .filter(
                MeterReading.meter_id == meter.id,
                MeterReading.month == batch.month,
                MeterReading.year == batch.year,
            )
            .first()
        )

        if existing:
            # Update existing
            existing.old_reading = item.old_reading
            existing.new_reading = item.new_reading
            existing.consumption = item.new_reading - item.old_reading
            created.append(existing.id)
        else:
            # Create new
            consumption = item.new_reading - item.old_reading
            reading = MeterReading(
                meter_id=meter.id,
                month=batch.month,
                year=batch.year,
                old_reading=item.old_reading,
                new_reading=item.new_reading,
                consumption=consumption,
            )
            db.add(reading)
            db.flush()
            created.append(reading.id)

    db.commit()

    return {
        "message": f"Đã ghi {len(created)} chỉ số",
        "created_ids": created,
        "errors": errors,
    }


@router.put("/readings/{reading_id}", response_model=MeterReadingResponse)
def update_reading(
    reading_id: int,
    reading_in: MeterReadingUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Cập nhật chỉ số"""
    reading = (
        db.query(MeterReading).filter(MeterReading.id == reading_id).first()
    )
    if not reading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy chỉ số",
        )

    update_data = reading_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(reading, field, value)

    # Recalculate consumption
    reading.consumption = reading.new_reading - reading.old_reading

    db.commit()
    db.refresh(reading)

    return reading
