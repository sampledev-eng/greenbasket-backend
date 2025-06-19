
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt

app = FastAPI()

SECRET_KEY = "greenbasketsecret"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

fake_users_db = {
    "test@example.com": {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "1234567890",
        "password": "password",
        "role": "customer"
    }
}

class User(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/login", response_model=Token)
def login(user: User):
    db_user = fake_users_db.get(user.email)
    if not db_user or db_user["password"] != user.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token_data = {
        "sub": user.email,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    jwt_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": jwt_token, "token_type": "bearer"}

@app.get("/products")
def get_products(token: str = Depends(oauth2_scheme)):
    return [
        {"name": "Apple", "price": 1.5},
        {"name": "Milk", "price": 0.99},
        {"name": "Tomato", "price": 0.5}
    ]
