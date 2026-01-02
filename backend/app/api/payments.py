"""
Payment API - Quản lý thanh toán
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from app.core.database import get_db
from app.models.payment import Payment
from app.models.invoice import Invoice, InvoiceStatus
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/payments", tags=["Thanh toán"])


@router.get("", response_model=List[PaymentResponse])
def get_payments(
    invoice_id: Optional[int] = Query(None, description="Lọc theo hóa đơn"),
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user)
):
    """Lấy danh sách thanh toán"""
    query = db.query(Payment)
    
    if invoice_id:
        query = query.filter(Payment.invoice_id == invoice_id)
    
    payments = query.order_by(Payment.payment_date.desc()).all()
    return payments


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_in: PaymentCreate,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user)
):
    """Ghi nhận thanh toán"""
    # Check invoice exists
    invoice = db.query(Invoice).filter(Invoice.id == payment_in.invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hóa đơn",
        )
    
    payment = Payment(**payment_in.model_dump())
    db.add(payment)
    
    # Update invoice paid amount and status
    invoice.paid_amount = invoice.paid_amount + payment_in.amount
    
    if invoice.paid_amount >= invoice.total:
        invoice.status = InvoiceStatus.PAID
    elif invoice.paid_amount > 0:
        invoice.status = InvoiceStatus.PARTIAL
    
    db.commit()
    db.refresh(payment)
    
    return payment

