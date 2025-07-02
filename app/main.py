from fastapi import FastAPI
from .database import Base, engine
from .routers import seed as seed_router

# ────────── 1️⃣  create the FastAPI app first
app = FastAPI(
    title="GreenBasket API (Advanced)",
    description="BigBasket-level backend with admin, delivery, payments",
    version="2.0.0",
)

# ────────── 2️⃣  create tables (if you use SQLAlchemy 2 metadata)
Base.metadata.create_all(bind=engine)

# ────────── 3️⃣  import routers AFTER the app object exists
from .routers import (   # noqa: E402  (import after app creation is intentional)
    users,
    products,
    categories,
    cart,
    orders,
    payments,
    delivery,
    auth as auth_router,
    seed as seed_router,          # ← new seed router
)

# ────────── 4️⃣  register every router
app.include_router(auth_router.router)       # /auth/…
app.include_router(users.router)             # /users/…
app.include_router(categories.router)        # /categories/…
app.include_router(products.router)          # /products/…
app.include_router(cart.router)              # /cart/…
app.include_router(orders.router)            # /orders/…
app.include_router(payments.router)          # /payments/…
app.include_router(delivery.router)          # /delivery/…
app.include_router(seed_router.router)       # /seed   (dev-only)
