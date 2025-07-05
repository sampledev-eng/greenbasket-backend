from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import schemas, crud, models
from ..dependencies import get_db, admin_required

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=schemas.Product, dependencies=[Depends(admin_required)])
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    # ensure category exists
    if product.category_id is None:
        raise HTTPException(status_code=400, detail="category_id required")
    return crud.create_product(db, product)


@router.get("/", response_model=list[schemas.Product])
def list_products(
    skip: int = 0,
    limit: int = 20,
    search: str | None = Query(None, description="Search query"),
    q: str | None = Query(None, description="Search query"),
    brand: str | None = Query(None),
    price_min: float | None = Query(None),
    price_max: float | None = Query(None),
    category_id: int | None = Query(None),
    sort: str | None = Query(None, description="price_asc or price_desc"),
    db: Session = Depends(get_db),
):
    query = search or q
    return crud.get_products(
        db,
        skip=skip,
        limit=limit,
        q=query,
        category_id=category_id,
        brand=brand,
        price_min=price_min,
        price_max=price_max,
        sort=sort,
    )

