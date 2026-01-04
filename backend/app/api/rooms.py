"""
Room API - Quản lý phòng trọ
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.core.database import get_db
from app.models.room import Room, RoomStatus
from app.models.location import Location
from app.models.room_type import RoomType
from app.models.tenant import Tenant
from app.models.meter import Meter, MeterType
from app.schemas.room import RoomCreate, RoomUpdate, RoomResponse, RoomWithDetails
from app.api.deps import get_current_user

router = APIRouter(prefix="/rooms", tags=["Phòng trọ"])


@router.get("", response_model=List[RoomWithDetails])
def get_rooms(
    location_id: Optional[int] = Query(None, description="Lọc theo khu trọ"),
    room_type_id: Optional[int] = Query(None, description="Lọc theo loại phòng"),
    status: Optional[RoomStatus] = Query(None, description="Lọc theo trạng thái"),
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user)
):
    """Lấy danh sách phòng"""
    query = db.query(Room).options(
        joinedload(Room.location),
        joinedload(Room.room_type),
        joinedload(Room.tenants)
    )
    
    if location_id:
        query = query.filter(Room.location_id == location_id)
    if room_type_id:
        query = query.filter(Room.room_type_id == room_type_id)
    if status:
        query = query.filter(Room.status == status)
    
    rooms = query.order_by(Room.location_id, Room.room_code).all()
    
    result = []
    for room in rooms:
        active_tenants = [t for t in room.tenants if t.is_active]
        room_data = RoomWithDetails.model_validate(room)
        room_data.tenants = active_tenants
        # Calculate effective price
        room_data.effective_price = room.price if room.price else (room.room_type.price if room.room_type else None)
        result.append(room_data)
    
    return result


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(
    room_in: RoomCreate,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user)
):
    """Thêm phòng mới"""
    # Check location exists
    location = db.query(Location).filter(Location.id == room_in.location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy khu trọ",
        )
    
    # Check room_type if provided
    if room_in.room_type_id:
        room_type = db.query(RoomType).filter(
            RoomType.id == room_in.room_type_id,
            RoomType.location_id == room_in.location_id
        ).first()
        if not room_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy loại phòng trong khu này",
            )
    
    # Check room_code unique in location
    existing = db.query(Room).filter(
        Room.location_id == room_in.location_id,
        Room.room_code == room_in.room_code
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã phòng đã tồn tại trong khu này",
        )
    
    room = Room(**room_in.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    
    # Auto create meters for room
    electric_meter = Meter(room_id=room.id, meter_type=MeterType.ELECTRIC)
    water_meter = Meter(room_id=room.id, meter_type=MeterType.WATER)
    db.add(electric_meter)
    db.add(water_meter)
    db.commit()
    
    # Load relationships
    db.refresh(room)
    room = db.query(Room).options(
        joinedload(Room.location),
        joinedload(Room.room_type)
    ).filter(Room.id == room.id).first()
    
    return room


@router.get("/{room_id}", response_model=RoomWithDetails)
def get_room(
    room_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user)
):
    """Lấy chi tiết phòng"""
    room = db.query(Room).options(
        joinedload(Room.location),
        joinedload(Room.room_type),
        joinedload(Room.tenants)
    ).filter(Room.id == room_id).first()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy phòng",
        )
    
    active_tenants = [t for t in room.tenants if t.is_active]
    room_data = RoomWithDetails.model_validate(room)
    room_data.tenants = active_tenants
    room_data.effective_price = room.price if room.price else (room.room_type.price if room.room_type else None)
    return room_data


@router.put("/{room_id}", response_model=RoomResponse)
def update_room(
    room_id: int,
    room_in: RoomUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user)
):
    """Cập nhật phòng"""
    room = db.query(Room).options(
        joinedload(Room.location),
        joinedload(Room.room_type)
    ).filter(Room.id == room_id).first()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy phòng",
        )
    
    update_data = room_in.model_dump(exclude_unset=True)
    
    # Check room_code unique if updating
    if "room_code" in update_data:
        existing = db.query(Room).filter(
            Room.location_id == room.location_id,
            Room.room_code == update_data["room_code"],
            Room.id != room_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã phòng đã tồn tại trong khu này",
            )
    
    # Check room_type if updating
    if "room_type_id" in update_data and update_data["room_type_id"]:
        room_type = db.query(RoomType).filter(
            RoomType.id == update_data["room_type_id"],
            RoomType.location_id == room.location_id
        ).first()
        if not room_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy loại phòng trong khu này",
            )
    
    for field, value in update_data.items():
        setattr(room, field, value)
    
    db.commit()
    db.refresh(room)
    
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user)
):
    """Xóa phòng"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy phòng",
        )
    
    # Check if has active tenants
    active_tenants = db.query(Tenant).filter(
        Tenant.room_id == room_id,
        Tenant.is_active == True
    ).count()
    if active_tenants > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa phòng đang có người thuê",
        )
    
    db.delete(room)
    db.commit()
