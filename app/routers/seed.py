# app/routers/seed.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product  # adjust import path if different

router = APIRouter(tags=["dev-tools"])

DEMO_PRODUCTS = [
    {
        "name": "Fresh Apples (1 kg)",
        "description": "Crisp Washington apples",
        "price": 3.99,
        "stock": 50,
        "image_url": "https://images.unsplash.com/photo-1567306226416-28f0efdc88ce"
    },
    {
        "name": "Organic Bananas (6 pcs)",
        "description": "Sweet Cavendish bananas",
        "price": 1.49,
        "stock": 40,
        "image_url": "https://images.unsplash.com/photo-1574226516831-e1dff420e37d"
    },
    {
        "name": "Whole Milk (1 L)",
        "description": "Farm-fresh whole milk",
        "price": 0.99,
        "stock": 120,
        "image_url": "https://images.unsplash.com/photo-1585238341980-06d04ca6a27a"
    },
]

@router.post("/seed", summary="Insert demo products (dev only)")
def seed_products(db: Session = Depends(get_db)):
    # safety: only seed if table is empty
    if db.query(Product).count() > 0:
        raise HTTPException(status_code=400, detail="Products already exist")

    for item in DEMO_PRODUCTS:
        db.add(Product(**item))

    db.commit()
    return {"inserted": len(DEMO_PRODUCTS)}
