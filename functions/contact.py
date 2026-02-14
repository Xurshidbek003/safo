from sqlalchemy.orm import Session
from typing import Optional, List
from models.wishlist import Wishlist
from models.contact import Contact, Newsletter
from schemas.contact import WishlistCreate, ContactCreate, NewsletterCreate


# Wishlist CRUD
def get_wishlist(db: Session, user_id: int) -> List[Wishlist]:
    """Get user's wishlist"""
    return db.query(Wishlist).filter(Wishlist.user_id == user_id).all()


def add_to_wishlist(db: Session, user_id: int, wishlist_item: WishlistCreate) -> Wishlist:
    """Add product to wishlist"""
    # Check if already exists
    existing = db.query(Wishlist).filter(
        Wishlist.user_id == user_id,
        Wishlist.product_id == wishlist_item.product_id
    ).first()

    if existing:
        return existing

    db_wishlist = Wishlist(user_id=user_id, product_id=wishlist_item.product_id)
    db.add(db_wishlist)
    db.commit()
    db.refresh(db_wishlist)
    return db_wishlist


def remove_from_wishlist(db: Session, user_id: int, product_id: int) -> bool:
    """Remove product from wishlist"""
    db_wishlist = db.query(Wishlist).filter(
        Wishlist.user_id == user_id,
        Wishlist.product_id == product_id
    ).first()

    if not db_wishlist:
        return False

    db.delete(db_wishlist)
    db.commit()
    return True


def clear_wishlist(db: Session, user_id: int) -> bool:
    """Clear user's wishlist"""
    db.query(Wishlist).filter(Wishlist.user_id == user_id).delete()
    db.commit()
    return True


# Contact CRUD
def create_contact(db: Session, contact: ContactCreate) -> Contact:
    """Create contact message"""
    db_contact = Contact(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def get_contacts(db: Session, skip: int = 0, limit: int = 100, is_read: Optional[bool] = None) -> List[Contact]:
    """Get all contact messages"""
    query = db.query(Contact)
    if is_read is not None:
        query = query.filter(Contact.is_read == is_read)
    return query.order_by(Contact.created_at.desc()).offset(skip).limit(limit).all()


def mark_contact_as_read(db: Session, contact_id: int) -> Optional[Contact]:
    """Mark contact as read"""
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not db_contact:
        return None
    db_contact.is_read = True
    db.commit()
    db.refresh(db_contact)
    return db_contact


# Newsletter CRUD
def subscribe_newsletter(db: Session, newsletter: NewsletterCreate) -> Newsletter:
    """Subscribe to newsletter"""
    # Check if already subscribed
    existing = db.query(Newsletter).filter(Newsletter.email == newsletter.email).first()
    if existing:
        existing.is_active = True
        db.commit()
        db.refresh(existing)
        return existing

    db_newsletter = Newsletter(**newsletter.model_dump())
    db.add(db_newsletter)
    db.commit()
    db.refresh(db_newsletter)
    return db_newsletter


def unsubscribe_newsletter(db: Session, email: str) -> bool:
    """Unsubscribe from newsletter"""
    db_newsletter = db.query(Newsletter).filter(Newsletter.email == email).first()
    if not db_newsletter:
        return False
    db_newsletter.is_active = False
    db.commit()
    return True


def get_newsletter_subscribers(db: Session, skip: int = 0, limit: int = 100) -> List[Newsletter]:
    """Get all newsletter subscribers"""
    return db.query(Newsletter).filter(Newsletter.is_active == True).offset(skip).limit(limit).all()