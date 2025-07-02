from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas, crud, auth, models
from ..dependencies import get_db

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/", response_model=list[schemas.Notification])
def get_notifications(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Notification).filter(models.Notification.user_id == current_user.id).all()
