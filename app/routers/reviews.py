from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, crud, auth, models
from ..dependencies import get_db

router = APIRouter(prefix="/products/{product_id}/reviews", tags=["reviews"])

@router.post("/", response_model=schemas.Review)
def create_review(product_id: int, review: schemas.ReviewBase, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return crud.create_review(db, product_id, current_user.id, review)


@router.get("/", response_model=list[schemas.Review])
def list_reviews(product_id: int, db: Session = Depends(get_db)):
    return crud.list_reviews(db, product_id)
