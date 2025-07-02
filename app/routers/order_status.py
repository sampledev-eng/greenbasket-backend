from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, models, schemas, auth
from ..dependencies import get_db, admin_required, delivery_required

router = APIRouter(prefix="/orders", tags=["orders"])

@router.put("/{order_id}/status", response_model=schemas.Order)
def update_status(order_id: int, status: schemas.OrderStatus, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if not current_user.is_admin and not current_user.is_delivery_partner:
        raise HTTPException(status_code=403, detail="Not allowed")
    return crud.update_order_status(db, order, status)
