"""
Tenant API - Quản lý người thuê
"""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.room import Room, RoomStatus
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantResponse, TenantUpdate

router = APIRouter(prefix="/tenants", tags=["Người thuê"])


@router.get("", response_model=List[TenantResponse])
def get_tenants(
    room_id: Optional[int] = Query(None, description="Lọc theo phòng"),
    is_active: Optional[bool] = Query(None, description="Lọc theo trạng thái"),
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Lấy danh sách người thuê"""
    query = db.query(Tenant).options(joinedload(Tenant.room))

    if room_id:
        query = query.filter(Tenant.room_id == room_id)
    if is_active is not None:
        query = query.filter(Tenant.is_active == is_active)

    tenants = query.order_by(Tenant.full_name).all()
    return tenants


@router.post(
    "", response_model=TenantResponse, status_code=status.HTTP_201_CREATED
)
def create_tenant(
    tenant_in: TenantCreate,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Thêm người thuê mới"""
    # Check room exists
    room = db.query(Room).filter(Room.id == tenant_in.room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy phòng",
        )

    tenant = Tenant(**tenant_in.model_dump())
    db.add(tenant)

    # Update room status to occupied
    room.status = RoomStatus.OCCUPIED

    db.commit()
    db.refresh(tenant)

    # Load room
    tenant.room = room

    return tenant


@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Lấy chi tiết người thuê"""
    tenant = (
        db.query(Tenant)
        .options(joinedload(Tenant.room))
        .filter(Tenant.id == tenant_id)
        .first()
    )

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người thuê",
        )

    return tenant


@router.put("/{tenant_id}", response_model=TenantResponse)
def update_tenant(
    tenant_id: int,
    tenant_in: TenantUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Cập nhật người thuê"""
    tenant = (
        db.query(Tenant)
        .options(joinedload(Tenant.room))
        .filter(Tenant.id == tenant_id)
        .first()
    )
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người thuê",
        )

    update_data = tenant_in.model_dump(exclude_unset=True)

    # If changing room, check new room exists
    if "room_id" in update_data and update_data["room_id"] != tenant.room_id:
        new_room = (
            db.query(Room).filter(Room.id == update_data["room_id"]).first()
        )
        if not new_room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy phòng mới",
            )
        new_room.status = RoomStatus.OCCUPIED

        # Check if old room has other active tenants
        old_room = tenant.room
        other_tenants = (
            db.query(Tenant)
            .filter(
                Tenant.room_id == old_room.id,
                Tenant.id != tenant_id,
                Tenant.is_active == True,
            )
            .count()
        )
        if other_tenants == 0:
            old_room.status = RoomStatus.VACANT

    for field, value in update_data.items():
        setattr(tenant, field, value)

    db.commit()
    db.refresh(tenant)

    return tenant


@router.put("/{tenant_id}/move-out", response_model=TenantResponse)
def move_out_tenant(
    tenant_id: int,
    move_out_date: Optional[date] = None,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Đánh dấu người thuê trả phòng"""
    tenant = (
        db.query(Tenant)
        .options(joinedload(Tenant.room))
        .filter(Tenant.id == tenant_id)
        .first()
    )
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người thuê",
        )

    tenant.is_active = False
    tenant.move_out_date = move_out_date or date.today()

    # Check if room has other active tenants
    room = tenant.room
    other_tenants = (
        db.query(Tenant)
        .filter(
            Tenant.room_id == room.id,
            Tenant.id != tenant_id,
            Tenant.is_active == True,
        )
        .count()
    )
    if other_tenants == 0:
        room.status = RoomStatus.VACANT

    db.commit()
    db.refresh(tenant)

    return tenant


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Xóa người thuê"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người thuê",
        )

    room = db.query(Room).filter(Room.id == tenant.room_id).first()

    db.delete(tenant)

    # Check if room has other active tenants
    if room:
        other_tenants = (
            db.query(Tenant)
            .filter(
                Tenant.room_id == room.id,
                Tenant.id != tenant_id,
                Tenant.is_active == True,
            )
            .count()
        )
        if other_tenants == 0:
            room.status = RoomStatus.VACANT

    db.commit()
