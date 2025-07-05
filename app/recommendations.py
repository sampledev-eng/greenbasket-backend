from sqlalchemy.orm import Session
from sqlalchemy import func

from . import models


def top_products(db: Session, limit: int = 5) -> list[models.Product]:
    """Return products with highest order quantities overall."""
    return (
        db.query(models.Product)
        .join(models.OrderItem)
        .group_by(models.Product.id)
        .order_by(func.sum(models.OrderItem.quantity).desc())
        .limit(limit)
        .all()
    )


def user_purchase_history(db: Session, user_id: int, limit: int = 5) -> list[models.Product]:
    """Return products previously purchased by the user."""
    return (
        db.query(models.Product)
        .join(models.OrderItem)
        .join(models.Order)
        .filter(models.Order.user_id == user_id)
        .group_by(models.Product.id)
        .order_by(func.sum(models.OrderItem.quantity).desc())
        .limit(limit)
        .all()
    )


def get_recommendations(db: Session, user_id: int, limit: int = 5) -> list[models.Product]:
    """Simple recommendation combining user history and top products."""
    history = user_purchase_history(db, user_id, limit)
    if history:
        return history
    return top_products(db, limit)
