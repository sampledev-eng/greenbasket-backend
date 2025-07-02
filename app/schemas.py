from typing import List, Optional
from pydantic import BaseModel, EmailStr, conint
import datetime
from enum import Enum

# Enums mirror models enums
class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    preparing = "preparing"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    cancelled = "cancelled"

class PaymentStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    failed = "failed"

# Category
class CategoryBase(BaseModel):
    name: str

class Category(CategoryBase):
    id: int

    class Config:
        orm_mode = True

# Product
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    stock: conint(ge=0)
    category_id: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    category: Optional[Category] = None

    class Config:
        orm_mode = True

# User
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    is_delivery_partner: bool = False

class User(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_admin: bool = False
    is_delivery_partner: bool = False

    class Config:
        orm_mode = True

# Token
class Token(BaseModel):
    access_token: str
    token_type: str

# Cart
class CartItemBase(BaseModel):
    product_id: int
    quantity: conint(gt=0)

class CartItem(CartItemBase):
    id: int

    class Config:
        orm_mode = True

# Order / OrderItem
class OrderItem(BaseModel):
    product_id: int
    quantity: int
    price: float

    class Config:
        orm_mode = True

class Order(BaseModel):
    id: int
    created_at: datetime.datetime
    total: float
    status: OrderStatus
    items: List[OrderItem]

    class Config:
        orm_mode = True

# Payment
class Payment(BaseModel):
    id: int
    amount: float
    status: PaymentStatus
    provider_payment_id: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        orm_mode = True

# Delivery Assignment
class DeliveryAssignment(BaseModel):
    id: int
    order_id: int
    delivery_partner_id: int
    assigned_at: datetime.datetime
    delivered_at: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True