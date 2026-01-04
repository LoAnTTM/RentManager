"""
Minh Rental API - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, locations, room_types, rooms, tenants, meters, invoices, payments, expenses, dashboard

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API quản lý nhà trọ Cô Minh - 68 Nguyễn Viết Xuân",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(locations.router, prefix="/api/v1")
app.include_router(room_types.router, prefix="/api/v1")
app.include_router(rooms.router, prefix="/api/v1")
app.include_router(tenants.router, prefix="/api/v1")
app.include_router(meters.router, prefix="/api/v1")
app.include_router(invoices.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")
app.include_router(expenses.router, prefix="/api/v1")


@app.get("/")
def root():
    """Health check"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
