from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine

# 1️⃣  create FastAPI app first
app = FastAPI(
    title="GreenBasket API (Advanced)",
    description="BigBasket-level backend with admin, delivery, payments",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sampledev-eng.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    admin_products,
    addresses,
    order_status,
    notifications,
    reviews,
    coupons,
    wallet,
    wishlist,
    checkout,
    admin_analytics,
    recommendations as recommendations_router,
    misc,
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
app.include_router(admin_products.router)
app.include_router(addresses.router)
app.include_router(order_status.router)
app.include_router(notifications.router)
app.include_router(reviews.router)
app.include_router(coupons.router)
app.include_router(wallet.router)
app.include_router(wishlist.router)
app.include_router(checkout.router)
app.include_router(admin_analytics.router)
app.include_router(recommendations_router.router)
app.include_router(misc.router)
