# GreenBasket Backend (Advanced)

**Version 2.0 – BigBasket‑level features**

## Major modules

| Domain | Description |
|--------|-------------|
| Auth   | JWT login / register |
| Catalog | Categories, products, search & filters |
| Cart   | Add / View / Stock check |
| Orders | Place orders, admin list |
| Payments | Mock confirmation endpoint (ready to swap with Stripe/Razorpay SDK) |
| Delivery | Delivery partner assignment & status updates |
| Admin | Role‑based (`is_admin`) protection on catalog & orders APIs |

## Quick Start

```bash
git clone <repo> greenbasket-backend-advanced
cd greenbasket-backend-advanced
docker compose up --build           # http://localhost:8000/docs
```

## Roles

- **Admin:** `is_admin=true` user → manage categories/products, view all orders
- **Delivery Partner:** `is_delivery_partner=true` user → take / deliver orders
- **Customer:** default user → shop, checkout

## Switching to Postgres

```bash
export DATABASE_URL=postgresql+psycopg://user:pass@host:5432/greenbasket
docker compose up --build
```

---

Generated on 2025-07-02T06:37:29.794496 UTC