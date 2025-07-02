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
    if product.stock < item.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
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