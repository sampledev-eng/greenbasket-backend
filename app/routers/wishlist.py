from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, models, dependencies, crud, auth as auth_utils

router = APIRouter(prefix="/wishlist", tags=["wishlist"])


@router.post("/add", response_model=schemas.WishlistItem)
def add_item(
    item: schemas.WishlistItemBase,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    product = crud.get_product(db, item.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return crud.add_to_wishlist(db, current_user.id, item.product_id)


@router.post("/remove")
def remove_item(
    item: schemas.WishlistItemBase,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    crud.remove_from_wishlist(db, current_user.id, item.product_id)
    return {"detail": "removed"}


@router.get("/", response_model=list[schemas.WishlistItem])
def list_items(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    return crud.list_wishlist(db, current_user.id)
