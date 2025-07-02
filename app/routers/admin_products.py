from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, models, crud
from ..dependencies import get_db, admin_required

router = APIRouter(prefix="/admin/products", tags=["admin"], dependencies=[Depends(admin_required)])

@router.put("/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, data: schemas.ProductCreate, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return crud.update_product(db, product, data)


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    crud.delete_product(db, product)
    return None
