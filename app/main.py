from fastapi import FastAPI
from .database import Base, engine

# 1️⃣  create FastAPI app first
app = FastAPI(
    title="GreenBasket API (Advanced)",
    description="BigBasket-level backend with admin, delivery, payments",
    version="2.0.0",
)

# 2️⃣  create DB tables
Base.metadata.create_all(bind=engine)

# 3️⃣  import routers (after app exists)
from .routers import (          # noqa: E402
    users,
    products,
    categories,
    cart,
    orders,
    payments,
    delivery,
    auth as auth_router,
    seed as seed_router,        # 👈 new
)

# 4️⃣  register routers
app.include_router(auth_router.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(payments.router)
app.include_router(delivery.router)
app.include_router(seed_router.router)      # 👈 /seed
