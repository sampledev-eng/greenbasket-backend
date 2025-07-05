from sqlalchemy.orm import Session
from sqlalchemy import select, update
from typing import List, Optional
import datetime

from . import models, schemas, sms
from .auth import get_password_hash
from .email_utils import send_email


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


def update_category(
    db: Session, category: models.Category, data: schemas.CategoryBase
) -> models.Category:
    """Update a category with the provided data."""
    for field, value in data.dict().items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: models.Category) -> None:
    """Delete a category object."""
    db.delete(category)
    db.commit()


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
    brand: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    sort: Optional[str] = None,
):
    query = db.query(models.Product)
    if q:
        query = query.filter(models.Product.name.ilike(f"%{q}%"))
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    if brand:
        query = query.filter(models.Product.brand.ilike(f"%{brand}%"))
    if price_min is not None:
        query = query.filter(models.Product.price >= price_min)
    if price_max is not None:
        query = query.filter(models.Product.price <= price_max)
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

    # Create a notification for the user
    message = f"Order {order.id} status updated to {status.value}"
    create_notification(db, order.user_id, message)

    # Notify via SMS and email (best effort)
    try:
        sms.get_sms_driver().send_sms("", message)
    except Exception:
        pass

    try:
        user = db.query(models.User).filter(models.User.id == order.user_id).first()
        if user:
            send_email(user.email, "Order Update", message)
    except Exception:
        pass

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


def get_address(db: Session, address_id: int) -> Optional[models.Address]:
    return db.query(models.Address).filter(models.Address.id == address_id).first()


def update_address(
    db: Session, address: models.Address, new_data: schemas.AddressBase
) -> models.Address:
    for field, value in new_data.dict().items():
        setattr(address, field, value)
    db.commit()
    db.refresh(address)
    return address


def delete_address(db: Session, address: models.Address) -> None:
    db.delete(address)
    db.commit()


def create_review(
    db: Session, product_id: int, user_id: int, review: schemas.ReviewBase
):
    db_review = models.Review(product_id=product_id, user_id=user_id, **review.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


def list_reviews(db: Session, product_id: int):
    return db.query(models.Review).filter(models.Review.product_id == product_id).all()


def create_wallet_txn(db: Session, user_id: int, amount: float, description: str = ""):
    txn = models.WalletTransaction(
        user_id=user_id, amount=amount, description=description
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


def get_wallet_balance(db: Session, user_id: int) -> float:
    total = db.query(models.WalletTransaction).filter(
        models.WalletTransaction.user_id == user_id
    )
    return sum(tx.amount for tx in total)


def create_notification(db: Session, user_id: int, message: str):
    notif = models.Notification(user_id=user_id, message=message)
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def mark_notification_read(
    db: Session, notif: models.Notification
) -> models.Notification:
    notif.read = True
    db.commit()
    db.refresh(notif)
    return notif


# ---- Cart helpers ----
def update_cart_item_quantity(
    db: Session, item: models.CartItem, quantity: int
) -> models.CartItem:
    item.quantity = quantity
    db.commit()
    db.refresh(item)
    return item


def delete_cart_item(db: Session, item: models.CartItem) -> None:
    db.delete(item)
    db.commit()


# ---- Wishlist helpers ----
def add_to_wishlist(db: Session, user_id: int, product_id: int) -> models.WishlistItem:
    item = (
        db.query(models.WishlistItem)
        .filter(
            models.WishlistItem.user_id == user_id,
            models.WishlistItem.product_id == product_id,
        )
        .first()
    )
    if item:
        return item
    item = models.WishlistItem(user_id=user_id, product_id=product_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def remove_from_wishlist(db: Session, user_id: int, product_id: int) -> None:
    db.query(models.WishlistItem).filter(
        models.WishlistItem.user_id == user_id,
        models.WishlistItem.product_id == product_id,
    ).delete()
    db.commit()


def list_wishlist(db: Session, user_id: int) -> List[models.WishlistItem]:
    return (
        db.query(models.WishlistItem)
        .filter(models.WishlistItem.user_id == user_id)
        .all()
    )


# ---- Auth helpers ----
def create_refresh_token_record(
    db: Session, user: models.User, token: str, expires_at: datetime.datetime
):
    db_obj = models.RefreshToken(user_id=user.id, token=token, expires_at=expires_at)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_refresh_token(db: Session, token: str) -> Optional[models.RefreshToken]:
    return (
        db.query(models.RefreshToken).filter(models.RefreshToken.token == token).first()
    )


def delete_refresh_token(db: Session, token: str) -> None:
    db.query(models.RefreshToken).filter(models.RefreshToken.token == token).delete()
    db.commit()


def create_otp_request(
    db: Session, phone_number: str, code: str, expires_at: datetime.datetime
) -> models.OTPRequest:
    req = models.OTPRequest(phone_number=phone_number, code=code, expires_at=expires_at)
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


def verify_otp_code(db: Session, phone_number: str, code: str) -> bool:
    now = datetime.datetime.utcnow()
    req = (
        db.query(models.OTPRequest)
        .filter(
            models.OTPRequest.phone_number == phone_number,
            models.OTPRequest.code == code,
            models.OTPRequest.expires_at > now,
            models.OTPRequest.verified.is_(False),
        )
        .first()
    )
    if not req:
        return False
    req.verified = True
    db.commit()
    return True
