from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError

import random
from .. import schemas, auth, dependencies, sms, models, crud

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.TokenPair)
def register(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    existing = crud.get_user_by_email(db, email=user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = crud.create_user(db, user)
    access_token = auth.create_access_token({"sub": db_user.email})
    refresh_token = auth.create_refresh_token({"sub": db_user.email})
    expires = datetime.utcnow() + timedelta(minutes=auth.REFRESH_TOKEN_EXPIRE_MINUTES)
    crud.create_refresh_token_record(db, db_user, refresh_token, expires)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.post("/token", response_model=schemas.TokenPair)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(dependencies.get_db),
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = auth.create_access_token({"sub": user.email})
    refresh_token = auth.create_refresh_token({"sub": user.email})
    expires = datetime.utcnow() + timedelta(minutes=auth.REFRESH_TOKEN_EXPIRE_MINUTES)
    crud.create_refresh_token_record(db, user, refresh_token, expires)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/login", response_model=schemas.TokenPair)
def login_json(payload: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    user = auth.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = auth.create_access_token({"sub": user.email})
    refresh_token = auth.create_refresh_token({"sub": user.email})
    expires = datetime.utcnow() + timedelta(minutes=auth.REFRESH_TOKEN_EXPIRE_MINUTES)
    crud.create_refresh_token_record(db, user, refresh_token, expires)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=schemas.TokenPair)
def refresh_token(payload: schemas.RefreshTokenRequest, db: Session = Depends(dependencies.get_db)):
    try:
        data = auth.jwt.decode(payload.refresh_token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    db_token = crud.get_refresh_token(db, payload.refresh_token)
    if not db_token or db_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    email = data.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    crud.delete_refresh_token(db, payload.refresh_token)

    access_token = auth.create_access_token({"sub": email})
    new_refresh = auth.create_refresh_token({"sub": email})
    expires = datetime.utcnow() + timedelta(minutes=auth.REFRESH_TOKEN_EXPIRE_MINUTES)
    user = db.query(models.User).filter(models.User.email == email).first()
    crud.create_refresh_token_record(db, user, new_refresh, expires)
    return {
        "access_token": access_token,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }


@router.post("/request-otp")
def request_otp(payload: schemas.PhoneNumber, db: Session = Depends(dependencies.get_db)):
    code = f"{random.randint(100000, 999999)}"
    expires = datetime.utcnow() + timedelta(minutes=5)
    crud.create_otp_request(db, payload.phone_number, code, expires)
    driver = sms.get_sms_driver()
    driver.send_sms(payload.phone_number, f"Your OTP is {code}")
    return {"detail": "OTP sent"}


@router.post("/verify-otp")
def verify_otp(payload: schemas.VerifyOTP, db: Session = Depends(dependencies.get_db)):
    valid = crud.verify_otp_code(db, payload.phone_number, payload.code)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    return {"detail": "OTP verified"}


@router.post("/forgot-password")
def forgot_password(payload: schemas.EmailAddress, db: Session = Depends(dependencies.get_db)):
    user = crud.get_user_by_email(db, payload.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    code = f"{random.randint(100000, 999999)}"
    expires = datetime.utcnow() + timedelta(minutes=5)
    crud.create_otp_request(db, payload.email, code, expires)
    print(f"Password reset code for {payload.email}: {code}")
    return {"detail": "OTP sent"}


@router.post("/reset-password")
def reset_password(payload: schemas.ResetPassword, db: Session = Depends(dependencies.get_db)):
    valid = crud.verify_otp_code(db, payload.email, payload.code)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    user = crud.get_user_by_email(db, payload.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = auth.get_password_hash(payload.new_password)
    db.commit()
    return {"detail": "Password updated"}

