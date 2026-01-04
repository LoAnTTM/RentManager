"""
RoomType API - Quản lý loại phòng
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.location import Location
from app.models.room_type import RoomType
from app.schemas.room_type import (RoomTypeCreate, RoomTypeResponse,
                                   RoomTypeUpdate)

router = APIRouter(prefix="/room-types", tags=["Loại phòng"])


@router.get("", response_model=List[RoomTypeResponse])
def get_room_types(
    location_id: Optional[int] = Query(None, description="Lọc theo khu trọ"),
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Lấy danh sách loại phòng"""
    query = db.query(RoomType)

    if location_id:
        query = query.filter(RoomType.location_id == location_id)

    room_types = query.order_by(RoomType.code).all()
    return room_types


@router.post("", response_model=RoomTypeResponse, status_code=status.HTTP_201_CREATED)
def create_room_type(
    room_type_in: RoomTypeCreate,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Thêm loại phòng mới"""
    # Check location exists
    location = (
        db.query(Location).filter(Location.id == room_type_in.location_id).first()
    )
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy khu trọ",
        )

    # Check code unique in location
    existing = (
        db.query(RoomType)
        .filter(
            RoomType.location_id == room_type_in.location_id,
            RoomType.code == room_type_in.code,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã loại phòng đã tồn tại trong khu này",
        )

    room_type = RoomType(**room_type_in.model_dump())
    db.add(room_type)
    db.commit()
    db.refresh(room_type)

    return room_type


@router.get("/{room_type_id}", response_model=RoomTypeResponse)
def get_room_type(
    room_type_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Lấy chi tiết loại phòng"""
    room_type = db.query(RoomType).filter(RoomType.id == room_type_id).first()

    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy loại phòng",
        )

    return room_type


@router.put("/{room_type_id}", response_model=RoomTypeResponse)
def update_room_type(
    room_type_id: int,
    room_type_in: RoomTypeUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Cập nhật loại phòng"""
    room_type = db.query(RoomType).filter(RoomType.id == room_type_id).first()
    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy loại phòng",
        )

    update_data = room_type_in.model_dump(exclude_unset=True)

    # Check code unique if updating
    if "code" in update_data:
        existing = (
            db.query(RoomType)
            .filter(
                RoomType.location_id == room_type.location_id,
                RoomType.code == update_data["code"],
                RoomType.id != room_type_id,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã loại phòng đã tồn tại trong khu này",
            )

    for field, value in update_data.items():
        setattr(room_type, field, value)

    db.commit()
    db.refresh(room_type)

    return room_type


@router.delete("/{room_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room_type(
    room_type_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Xóa loại phòng"""
    room_type = db.query(RoomType).filter(RoomType.id == room_type_id).first()
    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy loại phòng",
        )

    # Check if has rooms using this type
    from app.models.room import Room

    room_count = db.query(Room).filter(Room.room_type_id == room_type_id).count()
    if room_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa loại phòng đang được sử dụng",
        )

    db.delete(room_type)
    db.commit()
