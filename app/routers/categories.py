from fastapi import APIRouter, Depends
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