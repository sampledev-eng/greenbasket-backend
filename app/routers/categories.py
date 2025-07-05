from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, crud, models
from ..dependencies import get_db, admin_required

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=schemas.Category, dependencies=[Depends(admin_required)])
def create_category(category: schemas.CategoryBase, db: Session = Depends(get_db)):
    db_cat = crud.get_or_create_category(db, name=category.name)
    return db_cat


@router.get("/", response_model=list[schemas.Category])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()


@router.put("/{category_id}", response_model=schemas.Category, dependencies=[Depends(admin_required)])
def update_category(category_id: int, data: schemas.CategoryBase, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return crud.update_category(db, category, data)


@router.delete("/{category_id}", status_code=204, dependencies=[Depends(admin_required)])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    crud.delete_category(db, category)
    return None
