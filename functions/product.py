from sqlalchemy.orm import Session
from typing import Optional, List
from models.product import Product
from schemas.product import ProductCreate, ProductUpdate


def get_product(db: Session, product_id: int) -> Optional[Product]:
    """Get product by ID"""
    return db.query(Product).filter(Product.id == product_id).first()


def get_products(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        search: Optional[str] = None,
        is_active: bool = True
) -> List[Product]:
    """Get all products with filters"""
    query = db.query(Product)

    if is_active is not None:
        query = query.filter(Product.is_active == is_active)

    if category:
        query = query.filter(Product.category == category)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Product.name_uz.ilike(search_filter)) |
            (Product.name_ru.ilike(search_filter)) |
            (Product.name_en.ilike(search_filter))
        )

    return query.offset(skip).limit(limit).all()


def create_product(db: Session, product: ProductCreate) -> Product:
    """Create new product"""
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
    """Update product"""
    db_product = get_product(db, product_id)
    if not db_product:
        return None

    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)

    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int) -> bool:
    """Delete product"""
    db_product = get_product(db, product_id)
    if not db_product:
        return False
    db.delete(db_product)
    db.commit()
    return True


def update_product_image(db: Session, product_id: int, image_url: str) -> Optional[Product]:
    """Update product image"""
    db_product = get_product(db, product_id)
    if not db_product:
        return None

    db_product.image_url = image_url
    db.commit()
    db.refresh(db_product)
    return db_product