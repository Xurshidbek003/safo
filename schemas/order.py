from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models.order import OrderStatus, PaymentMethod


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int


class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    id: int
    order_id: int
    price: float

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    customer_name: str
    customer_phone: str
    delivery_address: str
    payment_method: PaymentMethod
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    notes: Optional[str] = None


class Order(OrderBase):
    id: int
    user_id: int
    status: OrderStatus
    total_amount: float
    created_at: datetime
    updated_at: datetime
    items: List[OrderItem] = []

    class Config:
        from_attributes = True