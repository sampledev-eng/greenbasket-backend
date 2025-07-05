from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, crud, models, auth
from ..dependencies import get_db

router = APIRouter(prefix="/users/{user_id}/addresses", tags=["addresses"])

@router.post("/", response_model=schemas.Address)
def create_address(user_id: int, address: schemas.AddressBase, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not allowed")
    return crud.create_address(db, user_id, address)


@router.get("/", response_model=list[schemas.Address])
def list_addresses(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not allowed")
    return crud.list_addresses(db, user_id)


@router.get("/{address_id}", response_model=schemas.Address)
def get_address(
    user_id: int,
    address_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not allowed")
    addr = crud.get_address(db, address_id)
    if not addr or addr.user_id != user_id:
        raise HTTPException(status_code=404, detail="Address not found")
    return addr


@router.put("/{address_id}", response_model=schemas.Address)
def update_address(
    user_id: int,
    address_id: int,
    address: schemas.AddressBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not allowed")
    addr = crud.get_address(db, address_id)
    if not addr or addr.user_id != user_id:
        raise HTTPException(status_code=404, detail="Address not found")
    return crud.update_address(db, addr, address)


@router.delete("/{address_id}")
def delete_address(
    user_id: int,
    address_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not allowed")
    addr = crud.get_address(db, address_id)
    if not addr or addr.user_id != user_id:
        raise HTTPException(status_code=404, detail="Address not found")
    crud.delete_address(db, addr)
    return {"detail": "deleted"}
