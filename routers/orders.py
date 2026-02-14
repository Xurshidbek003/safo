from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from schemas.order import Order, OrderCreate, OrderUpdate
from functions.order import get_order, get_orders, create_order, update_order, delete_order
from deps import get_current_active_user, get_current_admin_user
from models.user import User
from models.order import OrderStatus

router = APIRouter()


@router.get("/", response_model=List[Order])
def read_orders(
        skip: int = 0,
        limit: int = 100,
        status: Optional[OrderStatus] = None,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Get user's orders"""
    # If admin, can see all orders
    user_id = None if current_user.is_admin else current_user.id
    orders = get_orders(db, skip=skip, limit=limit, user_id=user_id, status=status)
    return orders


@router.get("/{order_id}", response_model=Order)
def read_order(
        order_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Get order by ID"""
    db_order = get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check if user owns this order or is admin
    if db_order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")

    return db_order


@router.post("/", response_model=Order)
def create_new_order(
        order: OrderCreate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Create new order"""
    return create_order(db=db, order=order, user_id=current_user.id)


@router.put("/{order_id}", response_model=Order)
def update_existing_order(
        order_id: int,
        order: OrderUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin_user)
):
    """Update order status (Admin only)"""
    db_order = update_order(db, order_id=order_id, order_update=order)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order


@router.delete("/{order_id}")
def delete_existing_order(
        order_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin_user)
):
    """Delete order (Admin only)"""
    success = delete_order(db, order_id=order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted successfully"}