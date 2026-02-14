from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas.contact import Wishlist, WishlistCreate
from functions.contact import get_wishlist, add_to_wishlist, remove_from_wishlist, clear_wishlist
from deps import get_current_active_user
from models.user import User

router = APIRouter()

@router.get("/", response_model=List[Wishlist])
def read_wishlist(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's wishlist"""
    return get_wishlist(db, user_id=current_user.id)

@router.post("/", response_model=Wishlist)
def add_product_to_wishlist(
    wishlist_item: WishlistCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add product to wishlist"""
    return add_to_wishlist(db, user_id=current_user.id, wishlist_item=wishlist_item)

@router.delete("/{product_id}")
def remove_product_from_wishlist(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove product from wishlist"""
    success = remove_from_wishlist(db, user_id=current_user.id, product_id=product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found in wishlist")
    return {"message": "Product removed from wishlist"}

@router.delete("/")
def clear_user_wishlist(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Clear user's wishlist"""
    clear_wishlist(db, user_id=current_user.id)
    return {"message": "Wishlist cleared"}