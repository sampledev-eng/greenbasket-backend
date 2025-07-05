from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from .. import schemas, models, dependencies, auth as auth_utils, crud

router = APIRouter(tags=["checkout"])


@router.post("/checkout", response_model=schemas.Payment)
def checkout(
    address_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    cart_items = (
        db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).all()
    )
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    address = crud.get_address(db, address_id)
    if not address or address.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Address not found")

    total = sum(ci.quantity * float(ci.product.price) for ci in cart_items)
    order = models.Order(
        user_id=current_user.id,
        shipping_address_id=address_id,
        total=total,
        status=models.OrderStatus.paid,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    for ci in cart_items:
        order_item = models.OrderItem(
            order_id=order.id,
            product_id=ci.product_id,
            quantity=ci.quantity,
            price=float(ci.product.price),
        )
        ci.product.stock -= ci.quantity
        db.add(order_item)
        db.delete(ci)

    payment = models.Payment(
        order_id=order.id,
        provider_payment_id=str(uuid.uuid4()),
        amount=total,
        status=models.PaymentStatus.confirmed,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
