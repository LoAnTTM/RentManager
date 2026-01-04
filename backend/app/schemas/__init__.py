"""
Pydantic schemas for API validation
"""

from app.schemas.dashboard import DashboardStats, MonthlyReport
from app.schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from app.schemas.invoice import (InvoiceCreate, InvoiceGenerate,
                                 InvoiceResponse, InvoiceUpdate)
from app.schemas.location import (LocationCreate, LocationResponse,
                                  LocationUpdate)
from app.schemas.meter import (MeterCreate, MeterReadingCreate,
                               MeterReadingResponse, MeterReadingUpdate,
                               MeterResponse)
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.schemas.room import (RoomCreate, RoomResponse, RoomUpdate,
                              RoomWithDetails)
from app.schemas.room_type import (RoomTypeCreate, RoomTypeResponse,
                                   RoomTypeUpdate)
from app.schemas.tenant import TenantCreate, TenantResponse, TenantUpdate
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse

__all__ = [
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token",
    "LocationCreate",
    "LocationUpdate",
    "LocationResponse",
    "RoomTypeCreate",
    "RoomTypeUpdate",
    "RoomTypeResponse",
    "RoomCreate",
    "RoomUpdate",
    "RoomResponse",
    "RoomWithDetails",
    "TenantCreate",
    "TenantUpdate",
    "TenantResponse",
    "MeterCreate",
    "MeterReadingCreate",
    "MeterReadingUpdate",
    "MeterResponse",
    "MeterReadingResponse",
    "InvoiceCreate",
    "InvoiceUpdate",
    "InvoiceResponse",
    "InvoiceGenerate",
    "PaymentCreate",
    "PaymentResponse",
    "ExpenseCreate",
    "ExpenseUpdate",
    "ExpenseResponse",
    "DashboardStats",
    "MonthlyReport",
]
