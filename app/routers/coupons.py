from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, models, crud, auth
from ..dependencies import get_db, admin_required

router = APIRouter(prefix="/coupons", tags=["coupons"])

@router.post("/", response_model=schemas.Coupon, dependencies=[Depends(admin_required)])
def create_coupon(coupon: schemas.Coupon, db: Session = Depends(get_db)):
    db_coupon = models.Coupon(**coupon.dict())
    db.add(db_coupon)
    db.commit()
    db.refresh(db_coupon)
    return db_coupon


@router.post("/apply-coupon")
def apply_coupon(code: str, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    coupon = db.query(models.Coupon).filter(models.Coupon.code == code, models.Coupon.active == True).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Invalid coupon")
    return coupon
