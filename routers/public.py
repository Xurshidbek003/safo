from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from schemas.contact import Contact, ContactCreate, Newsletter, NewsletterCreate
from functions.contact import (
    create_contact, get_contacts, mark_contact_as_read,
    subscribe_newsletter, unsubscribe_newsletter, get_newsletter_subscribers
)
from deps import get_current_admin_user
from models.user import User

router = APIRouter()

# Contact routes
@router.post("/contact", response_model=Contact)
def send_contact_message(contact: ContactCreate, db: Session = Depends(get_db)):
    """Send contact message (Public)"""
    return create_contact(db=db, contact=contact)

@router.get("/contact", response_model=List[Contact])
def read_contacts(
    skip: int = 0,
    limit: int = 100,
    is_read: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all contact messages (Admin only)"""
    return get_contacts(db, skip=skip, limit=limit, is_read=is_read)

@router.put("/contact/{contact_id}/read", response_model=Contact)
def mark_as_read(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Mark contact message as read (Admin only)"""
    db_contact = mark_contact_as_read(db, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

# Newsletter routes
@router.post("/newsletter/subscribe", response_model=Newsletter)
def subscribe(newsletter: NewsletterCreate, db: Session = Depends(get_db)):
    """Subscribe to newsletter (Public)"""
    return subscribe_newsletter(db=db, newsletter=newsletter)

@router.post("/newsletter/unsubscribe")
def unsubscribe(email: str, db: Session = Depends(get_db)):
    """Unsubscribe from newsletter (Public)"""
    success = unsubscribe_newsletter(db, email=email)
    if not success:
        raise HTTPException(status_code=404, detail="Email not found")
    return {"message": "Successfully unsubscribed"}

@router.get("/newsletter/subscribers", response_model=List[Newsletter])
def read_subscribers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all newsletter subscribers (Admin only)"""
    return get_newsletter_subscribers(db, skip=skip, limit=limit)