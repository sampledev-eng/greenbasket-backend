from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, crud, auth, models
from ..dependencies import get_db

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=list[schemas.Notification])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return (
        db.query(models.Notification)
        .filter(models.Notification.user_id == current_user.id)
        .all()
    )


@router.patch("/{notification_id}/read", response_model=schemas.Notification)
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    notif = (
        db.query(models.Notification)
        .filter(
            models.Notification.id == notification_id,
            models.Notification.user_id == current_user.id,
        )
        .first()
    )
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return crud.mark_notification_read(db, notif)
