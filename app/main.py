from fastapi import FastAPI
from .database import Base, engine
from .routers import (
    users,
    products,
    categories,
    cart,
    orders,
    payments,
    delivery,
    auth as auth_router,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GreenBasket API (Advanced)",
    description="BigBasket‑level backend with admin, delivery, payments",
    version="2.0.0",
)

app.include_router(auth_router.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(payments.router)
app.include_router(delivery.router)