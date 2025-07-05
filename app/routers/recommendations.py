# app/routers/recommendations.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas, dependencies   # <- import schemas!

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/", response_model=list[schemas.Product])   # <- use schemas.Product
def get_recommendations(
    db: Session = Depends(dependencies.get_db),
):
    # whatever recommendation logic you have…
    return db.query(models.Product).order_by(models.Product.id.desc()).limit(10).all()
