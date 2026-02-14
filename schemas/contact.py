from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class ContactCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: str
    message: str


class Contact(ContactCreate):
    id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NewsletterCreate(BaseModel):
    email: EmailStr


class Newsletter(NewsletterCreate):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class WishlistCreate(BaseModel):
    product_id: int


class Wishlist(BaseModel):
    id: int
    user_id: int
    product_id: int
    created_at: datetime

    class Config:
        from_attributes = True