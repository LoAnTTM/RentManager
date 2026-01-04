"""
Meter schemas - Đồng hồ điện nước
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel

from app.models.meter import MeterType


class MeterCreate(BaseModel):
    room_id: int
    meter_type: MeterType
    meter_code: Optional[str] = None
    notes: Optional[str] = None


class MeterReadingCreate(BaseModel):
    meter_id: int
    month: int
    year: int
    old_reading: Decimal
    new_reading: Decimal


class MeterReadingBatchItem(BaseModel):
    room_id: int
    meter_type: MeterType
    old_reading: Decimal
    new_reading: Decimal


class MeterReadingBatch(BaseModel):
    month: int
    year: int
    readings: List[MeterReadingBatchItem]


class MeterReadingUpdate(BaseModel):
    old_reading: Optional[Decimal] = None
    new_reading: Optional[Decimal] = None


class MeterReadingResponse(BaseModel):
    id: int
    meter_id: int
    month: int
    year: int
    old_reading: Decimal
    new_reading: Decimal
    consumption: Optional[Decimal] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MeterResponse(BaseModel):
    id: int
    room_id: int
    meter_type: MeterType
    meter_code: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    latest_reading: Optional[Decimal] = None

    class Config:
        from_attributes = True
