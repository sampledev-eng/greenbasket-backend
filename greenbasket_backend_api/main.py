"""from fastapi import Header, HTTPException, FastAPI
from typing import Optional
from jose import jwt, JWTError
from pydantic import BaseModel

app = FastAPI()

SECRET_KEY = "greenbasketsecret"
ALGORITHM = "HS256"

# ✅ Dummy user store
users_db = {
    "admin": "admin123",
    "tej": "pass123"
}

class LoginData(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(data: LoginData):
    username = data.username
    password = data.password

    if username not in users_db or users_db[username] != password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # ✅ Generate JWT token
    token = jwt.encode({"sub": username}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/products")
def get_products(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=403, detail="Token is invalid or expired")

    return [
        {"name": "Apple", "price": 1.5},
        {"name": "Milk", "price": 0.99},
        {"name": "Tomato", "price": 0.5}
    ]
"""