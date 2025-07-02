from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas, crud, auth, models
from ..dependencies import get_db

router = APIRouter(prefix="/wallet", tags=["wallet"])

@router.get("/transactions", response_model=list[schemas.WalletTransaction])
def transactions(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.WalletTransaction).filter(models.WalletTransaction.user_id == current_user.id).all()


@router.get("/balance")
def balance(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return {"balance": crud.get_wallet_balance(db, current_user.id)}
