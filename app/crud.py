from sqlalchemy.orm import Session
from sqlalchemy import select, update
from typing import List, Optional

from . import models, schemas
from .auth import get_password_hash

# User CRUD
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        is_delivery_partner=user.is_delivery_partner,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Category CRUD
def get_or_create_category(db: Session, name: str):
    category = db.query(models.Category).filter(models.Category.name == name).first()
    if category:
        return category
    category = models.Category(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

# Product CRUD
def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products(db: Session, skip: int = 0, limit: int = 20, q: Optional[str] = None, category_id: Optional[int] = None):
    query = db.query(models.Product)
    if q:
        query = query.filter(models.Product.name.ilike(f"%{q}%"))
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    return query.offset(skip).limit(limit).all()

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

# Order CRUD helpers
def update_order_status(db: Session, order: models.Order, status: models.OrderStatus):
    order.status = status
    db.commit()
    db.refresh(order)
    return order