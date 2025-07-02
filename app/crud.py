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

def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    q: Optional[str] = None,
    category_id: Optional[int] = None,
    sort: Optional[str] = None,
):
    query = db.query(models.Product)
    if q:
        query = query.filter(models.Product.name.ilike(f"%{q}%"))
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    if sort == "price_asc":
        query = query.order_by(models.Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(models.Product.price.desc())
    return query.offset(skip).limit(limit).all()

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

# Order CRUD helpers
def update_order_status(db: Session, order: models.Order, status: models.OrderStatus):
    order.status = status
    db.commit()
    db.refresh(order)
    return order


# ----- Additional CRUD helpers -----
def update_product(db: Session, product: models.Product, data: schemas.ProductCreate):
    for field, value in data.dict().items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: models.Product):
    db.delete(product)
    db.commit()


def create_address(db: Session, user_id: int, address: schemas.AddressBase):
    db_obj = models.Address(user_id=user_id, **address.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def list_addresses(db: Session, user_id: int):
    return db.query(models.Address).filter(models.Address.user_id == user_id).all()


def create_review(db: Session, product_id: int, user_id: int, review: schemas.ReviewBase):
    db_review = models.Review(product_id=product_id, user_id=user_id, **review.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


def list_reviews(db: Session, product_id: int):
    return db.query(models.Review).filter(models.Review.product_id == product_id).all()


def create_wallet_txn(db: Session, user_id: int, amount: float, description: str = ""):
    txn = models.WalletTransaction(user_id=user_id, amount=amount, description=description)
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


def get_wallet_balance(db: Session, user_id: int) -> float:
    total = db.query(models.WalletTransaction).filter(models.WalletTransaction.user_id == user_id)
    return sum(tx.amount for tx in total)


def create_notification(db: Session, user_id: int, message: str):
    notif = models.Notification(user_id=user_id, message=message)
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif
