from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import uuid

from .. import schemas, models, dependencies, auth as auth_utils, crud

router = APIRouter(tags=["checkout"])


@router.post("/checkout", response_model=schemas.Payment)
def checkout(
    address_id: int,
    coupon_code: str | None = Query(None),
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    # 1. Grab all cart items for the current user
    cart_items = (
        db.query(models.CartItem)
        .filter(models.CartItem.user_id == current_user.id)
        .all()
    )
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # 2. Validate the shipping address
    address = crud.get_address(db, address_id)
    if not address or address.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Address not found")

    # 3. Calculate cart total
    total = sum(ci.quantity * float(ci.product.price) for ci in cart_items)

    # 4. Optional coupon application
    coupon = None
    if coupon_code:
        coupon = (
            db.query(models.Coupon)
            .filter(
                models.Coupon.code == coupon_code,
                models.Coupon.active.is_(True),
            )
            .first()
        )
        if not coupon:
            raise HTTPException(status_code=404, detail="Invalid coupon")
        total *= 1 - (coupon.discount_percent / 100)

    # 5. Create the order
    order = models.Order(
        user_id=current_user.id,
        shipping_address_id=address_id,
        total=total,
        status=models.OrderStatus.paid,
        coupon_id=coupon.id if coupon else None,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # 6. Convert cart items to order items & update stock
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

    # 7. Record payment (simulated here)
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
