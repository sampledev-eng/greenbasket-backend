import os
import tempfile
import pytest
from fastapi.testclient import TestClient

# prepare isolated test database before importing the app
DB_FD, DB_PATH = tempfile.mkstemp()
os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"

from app import auth, models, database
from app.main import app
from app.crud import create_wallet_txn, create_notification
from app.dependencies import get_db as orig_get_db

# create tables on the new database
models.Base.metadata.create_all(bind=database.engine)

# override get_db dependency so each request uses the same session maker
def override_get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[orig_get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module")
def tokens():
    db = database.SessionLocal()
    admin = models.User(
        email="admin@example.com",
        hashed_password=auth.get_password_hash("admin"),
        is_admin=True,
    )
    user = models.User(
        email="user@example.com",
        hashed_password=auth.get_password_hash("user"),
    )
    db.add_all([admin, user])
    db.commit()
    db.refresh(user)
    admin_token = auth.create_access_token({"sub": admin.email})
    user_token = auth.create_access_token({"sub": user.email})
    db.close()
    return {
        "admin": f"Bearer {admin_token}",
        "user": f"Bearer {user_token}",
        "user_id": user.id,
    }

def test_full_flow(tokens):
    # admin creates a category
    resp = client.post(
        "/categories/",
        json={"name": "Fruits"},
        headers={"Authorization": tokens["admin"]},
    )
    assert resp.status_code == 200
    category_id = resp.json()["id"]

    # admin creates a product
    product_payload = {
        "name": "Apple",
        "description": "Red apple",
        "price": 1.0,
        "stock": 10,
        "category_id": category_id,
    }
    resp = client.post(
        "/products/",
        json=product_payload,
        headers={"Authorization": tokens["admin"]},
    )
    assert resp.status_code == 200
    product_id = resp.json()["id"]

    # user adds an address
    resp = client.post(
        f"/users/{tokens['user_id']}/addresses/",
        json={"address_line": "123 Street", "city": "Town", "pincode": "560001"},
        headers={"Authorization": tokens["user"]},
    )
    assert resp.status_code == 200

    # user submits a review
    resp = client.post(
        f"/products/{product_id}/reviews/",
        json={"rating": 5, "comment": "Great"},
        headers={"Authorization": tokens["user"]},
    )
    assert resp.status_code == 200

    # admin creates coupon and user applies it
    resp = client.post(
        "/coupons/",
        json={"id": 1, "code": "DISC10", "discount_percent": 10, "active": True},
        headers={"Authorization": tokens["admin"]},
    )
    assert resp.status_code == 200
    resp = client.post(
        "/coupons/apply-coupon",
        params={"code": "DISC10"},
        headers={"Authorization": tokens["user"]},
    )
    assert resp.status_code == 200

    # record wallet transaction and verify balance
    db = database.SessionLocal()
    create_wallet_txn(db, tokens["user_id"], 5, "bonus")
    db.close()
    resp = client.get("/wallet/balance", headers={"Authorization": tokens["user"]})
    assert resp.status_code == 200
    assert resp.json()["balance"] == 5

    # serviceability check
    resp = client.get("/serviceable/560001")
    assert resp.status_code == 200
    assert resp.json()["serviceable"] is True

    # user places an order
    resp = client.post(
        "/cart/",
        json={"product_id": product_id, "quantity": 2},
        headers={"Authorization": tokens["user"]},
    )
    assert resp.status_code == 200
    resp = client.post("/orders/", headers={"Authorization": tokens["user"]})
    assert resp.status_code == 200
    order_id = resp.json()["id"]

    # confirm payment
    resp = client.post(f"/payments/{order_id}")
    assert resp.status_code == 200

    # admin updates order status
    resp = client.put(
        f"/orders/{order_id}/status",
        json="preparing",
        headers={"Authorization": tokens["admin"]},
    )
    assert resp.status_code == 200

    # create notification and fetch it
    db = database.SessionLocal()
    create_notification(db, tokens["user_id"], "Order preparing")
    db.close()
    resp = client.get("/notifications/", headers={"Authorization": tokens["user"]})
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # admin analytics endpoint
    resp = client.get("/admin/stats", headers={"Authorization": tokens["admin"]})
    assert resp.status_code == 200
