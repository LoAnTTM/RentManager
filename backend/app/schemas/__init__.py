"""
Pydantic schemas for API validation
"""
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.schemas.location import LocationCreate, LocationUpdate, LocationResponse
from app.schemas.room import RoomCreate, RoomUpdate, RoomResponse, RoomWithDetails
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse
from app.schemas.meter import MeterCreate, MeterReadingCreate, MeterReadingUpdate, MeterResponse, MeterReadingResponse
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceGenerate
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.schemas.dashboard import DashboardStats, MonthlyReport

__all__ = [
    "UserCreate", "UserLogin", "UserResponse", "Token",
    "LocationCreate", "LocationUpdate", "LocationResponse",
    "RoomCreate", "RoomUpdate", "RoomResponse", "RoomWithDetails",
    "TenantCreate", "TenantUpdate", "TenantResponse",
    "MeterCreate", "MeterReadingCreate", "MeterReadingUpdate", "MeterResponse", "MeterReadingResponse",
    "InvoiceCreate", "InvoiceUpdate", "InvoiceResponse", "InvoiceGenerate",
    "PaymentCreate", "PaymentResponse",
    "ExpenseCreate", "ExpenseUpdate", "ExpenseResponse",
    "DashboardStats", "MonthlyReport"
]

