from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, models, dependencies, auth as auth_utils, crud

router = APIRouter(prefix="/cart", tags=["cart"])


@router.post("/", response_model=schemas.CartItem)
def add_to_cart(
    item: schemas.CartItemBase,
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(dependencies.get_db),
):
    product = crud.get_product(db, item.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock - product.reserved < item.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    product.reserved += item.quantity
    db_item = models.CartItem(user_id=current_user.id, product_id=item.product_id, quantity=item.quantity)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/", response_model=list[schemas.CartItem])
def get_cart(
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(dependencies.get_db),
):
    return db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).all()


@router.put("/{item_id}", response_model=schemas.CartItem)
def update_cart_item(
    item_id: int,
    quantity: int,
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(dependencies.get_db),
):
    item = db.query(models.CartItem).filter(models.CartItem.id == item_id).first()
    if not item or item.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Item not found")
    diff = quantity - item.quantity
    if diff > 0:
        if item.product.stock - item.product.reserved < diff:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        item.product.reserved += diff
    elif diff < 0:
        item.product.reserved += diff  # diff is negative
    return crud.update_cart_item_quantity(db, item, quantity)


@router.delete("/{item_id}")
def delete_cart_item(
    item_id: int,
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(dependencies.get_db),
):
    item = db.query(models.CartItem).filter(models.CartItem.id == item_id).first()
    if not item or item.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Item not found")
    item.product.reserved -= item.quantity
    crud.delete_cart_item(db, item)
    return {"detail": "deleted"}
