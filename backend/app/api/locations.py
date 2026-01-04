"""
Location API - Quản lý khu trọ
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.location import Location
from app.models.room import Room, RoomStatus
from app.models.room_type import RoomType
from app.schemas.location import (LocationCreate, LocationResponse,
                                  LocationUpdate)

router = APIRouter(prefix="/locations", tags=["Khu trọ"])


@router.get("", response_model=List[LocationResponse])
def get_locations(db: Session = Depends(get_db), _: None = Depends(get_current_user)):
    """Lấy danh sách khu trọ"""
    locations = db.query(Location).options(joinedload(Location.room_types)).all()

    result = []
    for loc in locations:
        room_count = db.query(Room).filter(Room.location_id == loc.id).count()
        occupied_count = (
            db.query(Room)
            .filter(Room.location_id == loc.id, Room.status == RoomStatus.OCCUPIED)
            .count()
        )

        loc_data = LocationResponse.model_validate(loc)
        loc_data.room_count = room_count
        loc_data.occupied_count = occupied_count
        result.append(loc_data)

    return result


@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def create_location(
    location_in: LocationCreate,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Thêm khu trọ mới"""
    location = Location(**location_in.model_dump())
    db.add(location)
    db.commit()
    db.refresh(location)

    loc_data = LocationResponse.model_validate(location)
    loc_data.room_count = 0
    loc_data.occupied_count = 0
    loc_data.room_types = []
    return loc_data


@router.get("/{location_id}", response_model=LocationResponse)
def get_location(
    location_id: int, db: Session = Depends(get_db), _: None = Depends(get_current_user)
):
    """Lấy chi tiết khu trọ"""
    location = (
        db.query(Location)
        .options(joinedload(Location.room_types))
        .filter(Location.id == location_id)
        .first()
    )

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy khu trọ",
        )

    room_count = db.query(Room).filter(Room.location_id == location.id).count()
    occupied_count = (
        db.query(Room)
        .filter(Room.location_id == location.id, Room.status == RoomStatus.OCCUPIED)
        .count()
    )

    loc_data = LocationResponse.model_validate(location)
    loc_data.room_count = room_count
    loc_data.occupied_count = occupied_count
    return loc_data


@router.put("/{location_id}", response_model=LocationResponse)
def update_location(
    location_id: int,
    location_in: LocationUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Cập nhật khu trọ"""
    location = (
        db.query(Location)
        .options(joinedload(Location.room_types))
        .filter(Location.id == location_id)
        .first()
    )

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy khu trọ",
        )

    update_data = location_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(location, field, value)

    db.commit()
    db.refresh(location)

    room_count = db.query(Room).filter(Room.location_id == location.id).count()
    occupied_count = (
        db.query(Room)
        .filter(Room.location_id == location.id, Room.status == RoomStatus.OCCUPIED)
        .count()
    )

    loc_data = LocationResponse.model_validate(location)
    loc_data.room_count = room_count
    loc_data.occupied_count = occupied_count
    return loc_data


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(
    location_id: int, db: Session = Depends(get_db), _: None = Depends(get_current_user)
):
    """Xóa khu trọ"""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy khu trọ",
        )

    # Check if has rooms
    room_count = db.query(Room).filter(Room.location_id == location_id).count()
    if room_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa khu trọ đang có phòng",
        )

    db.delete(location)
    db.commit()
