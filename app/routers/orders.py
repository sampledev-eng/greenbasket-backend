from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import schemas, models, dependencies, auth as auth_utils, crud

router = APIRouter(prefix="/orders", tags=["orders"])


# ──────────────────────────
# 1.  Place an order
# ──────────────────────────
@router.post("/", response_model=schemas.Order)
def place_order(
    address_id: int,
    coupon_code: str | None = Query(None),
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    # ── Fetch cart items ──────────────────────────────────────────────
    cart_items = (
        db.query(models.CartItem)
        .filter(models.CartItem.user_id == current_user.id)
        .all()
    )
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # ── Validate shipping address ─────────────────────────────────────
    address = crud.get_address(db, address_id)
    if not address or address.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Address not found")

    # ── Calculate total & apply coupon (if any) ───────────────────────
    total = sum(ci.quantity * float(ci.product.price) for ci in cart_items)
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

    # ── Create order ──────────────────────────────────────────────────
    order = models.Order(
        user_id=current_user.id,
        shipping_address_id=address_id,
        total=total,
        status=models.OrderStatus.pending,
        coupon_id=coupon.id if coupon else None,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # ── Transfer cart items → order items & update stock ──────────────
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

    db.commit()
    db.refresh(order)
    return order


# ──────────────────────────
# 2.  List current user orders
# ──────────────────────────
@router.get("/", response_model=list[schemas.Order])
def list_orders(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    return (
        db.query(models.Order)
        .filter(models.Order.user_id == current_user.id)
        .all()
    )


# ──────────────────────────
# 3.  Admin: list *all* orders
# ──────────────────────────
@router.get(
    "/all",
    response_model=list[schemas.Order],
    dependencies=[Depends(dependencies.admin_required)],
)
def list_all_orders(db: Session = Depends(dependencies.get_db)):
    return db.query(models.Order).all()


# ──────────────────────────
# 4.  Get single order
# ──────────────────────────
@router.get("/{order_id}", response_model=schemas.Order)
def get_order(
    order_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not allowed")
    return order
