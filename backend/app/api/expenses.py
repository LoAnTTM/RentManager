"""
Expense API - Quản lý chi tiêu
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.core.database import get_db
from app.models.expense import Expense, ExpenseCategory
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/expenses", tags=["Chi tiêu"])


@router.get("", response_model=List[ExpenseResponse])
def get_expenses(
    location_id: Optional[int] = Query(None, description="Lọc theo khu"),
    category: Optional[ExpenseCategory] = Query(None, description="Lọc theo loại"),
    month: Optional[int] = Query(None, description="Tháng"),
    year: Optional[int] = Query(None, description="Năm"),
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user)
):
    """Lấy danh sách chi tiêu"""
    query = db.query(Expense)
    
    if location_id:
        query = query.filter(Expense.location_id == location_id)
    if category:
        query = query.filter(Expense.category == category)
    if month and year:
        from sqlalchemy import extract
        query = query.filter(
            extract('month', Expense.expense_date) == month,
            extract('year', Expense.expense_date) == year
        )
    elif year:
        from sqlalchemy import extract
        query = query.filter(extract('year', Expense.expense_date) == year)
    
    expenses = query.order_by(Expense.expense_date.desc()).all()
    return expenses


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense_in: ExpenseCreate,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user)
):
    """Thêm khoản chi"""
    expense = Expense(**expense_in.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    
    return expense


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user)
):
    """Lấy chi tiết khoản chi"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy khoản chi",
        )
    
    return expense


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    expense_in: ExpenseUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user)
):
    """Cập nhật khoản chi"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy khoản chi",
        )
    
    update_data = expense_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(expense, field, value)
    
    db.commit()
    db.refresh(expense)
    
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user)
):
    """Xóa khoản chi"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy khoản chi",
        )
    
    db.delete(expense)
    db.commit()

