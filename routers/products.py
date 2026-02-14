from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from schemas.product import Product, ProductCreate, ProductUpdate
from functions.product import (
    get_product, get_products, create_product,
    update_product, delete_product, update_product_image
)
from deps import get_current_admin_user
from functions.file_uploads import save_upload_file
from models.user import User

router = APIRouter()


@router.get("/", response_model=List[Product])
def read_products(
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        search: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """Get all products with optional filters"""
    products = get_products(db, skip=skip, limit=limit, category=category, search=search)
    return products


@router.get("/{product_id}", response_model=Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    """Get product by ID"""
    db_product = get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@router.post("/", response_model=Product)
def create_new_product(
        product: ProductCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin_user)
):
    """Create new product (Admin only)"""
    return create_product(db=db, product=product)


@router.put("/{product_id}", response_model=Product)
def update_existing_product(
        product_id: int,
        product: ProductUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin_user)
):
    """Update product (Admin only)"""
    db_product = update_product(db, product_id=product_id, product_update=product)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@router.delete("/{product_id}")
def delete_existing_product(
        product_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin_user)
):
    """Delete product (Admin only)"""
    success = delete_product(db, product_id=product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}


@router.post("/{product_id}/image", response_model=Product)
async def upload_product_image(
        product_id: int,
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin_user)
):
    """Upload product image (Admin only)"""
    # Save file
    file_path = await save_upload_file(file, "products")

    # Update product
    db_product = update_product_image(db, product_id=product_id, image_url=file_path)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return db_product