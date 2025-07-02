from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import datetime

from .. import schemas, models, dependencies

router = APIRouter(prefix="/delivery", tags=["delivery"])


@router.get("/assignable", response_model=list[schemas.Order], dependencies=[Depends(dependencies.delivery_required)])
def list_assignable_orders(db: Session = Depends(dependencies.get_db)):
    # orders paid and not yet assigned
    return db.query(models.Order).filter(
        models.Order.status == models.OrderStatus.paid,
        models.Order.delivery_assignment == None,  # noqa: E711
    ).all()


@router.post("/assign/{order_id}", response_model=schemas.DeliveryAssignment, dependencies=[Depends(dependencies.delivery_required)])
def take_order(
    order_id: int,
    current_user: models.User = Depends(dependencies.delivery_required),
    db: Session = Depends(dependencies.get_db),
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order or order.status != models.OrderStatus.paid:
        raise HTTPException(status_code=400, detail="Order not assignable")
    if order.delivery_assignment:
        raise HTTPException(status_code=400, detail="Already assigned")
    assignment = models.DeliveryAssignment(order_id=order.id, delivery_partner_id=current_user.id)
    order.status = models.OrderStatus.out_for_delivery
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.post("/delivered/{order_id}", response_model=schemas.Order, dependencies=[Depends(dependencies.delivery_required)])
def mark_delivered(
    order_id: int,
    current_user: models.User = Depends(dependencies.delivery_required),
    db: Session = Depends(dependencies.get_db),
):
    assignment = db.query(models.DeliveryAssignment).filter(
        models.DeliveryAssignment.order_id == order_id,
        models.DeliveryAssignment.delivery_partner_id == current_user.id,
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    assignment.delivered_at = datetime.datetime.utcnow()
    order = assignment.order
    order.status = models.OrderStatus.delivered
    db.commit()
    db.refresh(order)
    return order