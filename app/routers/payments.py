from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid, random

from .. import schemas, models, dependencies, crud

router = APIRouter(prefix="/payments", tags=["payments"])

# Simple mock payment confirmation
@router.post("/{order_id}", response_model=schemas.Payment)
def confirm_payment(order_id: int, db: Session = Depends(dependencies.get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != models.OrderStatus.pending:
        raise HTTPException(status_code=400, detail="Payment already processed or order invalid")

    payment = models.Payment(
        order_id=order.id,
        provider_payment_id=str(uuid.uuid4()),
        amount=order.total,
        status=models.PaymentStatus.confirmed,
    )
    db.add(payment)
    # Update order status
    order.status = models.OrderStatus.paid
    db.commit()
    db.refresh(payment)
    db.refresh(order)
    return payment