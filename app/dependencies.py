from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from .database import SessionLocal
from .auth import get_current_user
from . import models

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def admin_required(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privilege required")
    return current_user

def delivery_required(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_delivery_partner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Delivery partner privilege required")
    return current_user