from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from .. import schemas, models
from ..dependencies import get_db, admin_required

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(admin_required)])

@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    total_orders = db.query(func.count(models.Order.id)).scalar()
    revenue = db.query(func.sum(models.Order.total)).scalar() or 0
    return {"total_orders": total_orders, "revenue": revenue}


@router.get("/top-products", response_model=list[schemas.Product])
def top_products(limit: int = 5, db: Session = Depends(get_db)):
    products = db.query(models.Product).join(models.OrderItem).group_by(models.Product.id).order_by(func.sum(models.OrderItem.quantity).desc()).limit(limit).all()
    return products
