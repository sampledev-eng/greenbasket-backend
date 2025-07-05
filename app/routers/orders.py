from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, models, dependencies, auth as auth_utils, crud

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=schemas.Order)
def place_order(
    address_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    address = crud.get_address(db, address_id)
    if not address or address.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Address not found")

    # Calculate total and create order
    total = sum(ci.quantity * ci.product.price for ci in cart_items)
    order = models.Order(
        user_id=current_user.id,
        shipping_address_id=address_id,
        total=total,
        status=models.OrderStatus.pending,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Transfer items
    for ci in cart_items:
        order_item = models.OrderItem(
            order_id=order.id,
            product_id=ci.product_id,
            quantity=ci.quantity,
            price=ci.product.price,
        )
        # Reduce stock
        ci.product.stock -= ci.quantity
        db.add(order_item)
        db.delete(ci)
    db.commit()
    db.refresh(order)
    return order


@router.get("/", response_model=list[schemas.Order])
def list_orders(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    return db.query(models.Order).filter(models.Order.user_id == current_user.id).all()

# Admin endpoint
@router.get("/all", response_model=list[schemas.Order], dependencies=[Depends(dependencies.admin_required)])
def list_all_orders(db: Session = Depends(dependencies.get_db)):
    return db.query(models.Order).all()