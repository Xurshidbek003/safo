from sqlalchemy.orm import Session
from typing import Optional, List
from models.order import Order, OrderItem, OrderStatus
from schemas.order import OrderCreate, OrderUpdate
from functions.product import get_product


def get_order(db: Session, order_id: int) -> Optional[Order]:
    """Get order by ID"""
    return db.query(Order).filter(Order.id == order_id).first()


def get_orders(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        status: Optional[OrderStatus] = None
) -> List[Order]:
    """Get all orders with filters"""
    query = db.query(Order)

    if user_id:
        query = query.filter(Order.user_id == user_id)

    if status:
        query = query.filter(Order.status == status)

    return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


def create_order(db: Session, order: OrderCreate, user_id: int) -> Order:
    """Create new order"""
    # Calculate total amount
    total_amount = 0
    order_items = []

    for item in order.items:
        product = get_product(db, item.product_id)
        if not product:
            continue

        item_total = product.price * item.quantity
        total_amount += item_total

        order_items.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "price": product.price
        })

    # Create order
    db_order = Order(
        user_id=user_id,
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        delivery_address=order.delivery_address,
        payment_method=order.payment_method,
        notes=order.notes,
        total_amount=total_amount
    )
    db.add(db_order)
    db.flush()

    # Create order items
    for item_data in order_items:
        order_item = OrderItem(order_id=db_order.id, **item_data)
        db.add(order_item)

    db.commit()
    db.refresh(db_order)
    return db_order


def update_order(db: Session, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
    """Update order"""
    db_order = get_order(db, order_id)
    if not db_order:
        return None

    update_data = order_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_order, field, value)

    db.commit()
    db.refresh(db_order)
    return db_order


def delete_order(db: Session, order_id: int) -> bool:
    """Delete order"""
    db_order = get_order(db, order_id)
    if not db_order:
        return False
    db.delete(db_order)
    db.commit()
    return True