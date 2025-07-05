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
    brand: Optional[str] = None
    mrp: Optional[float] = None
    price: float
    discount_pct: int = 0
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


class TokenPair(Token):
    refresh_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PhoneNumber(BaseModel):
    phone_number: str


class VerifyOTP(BaseModel):
    phone_number: str
    code: str


class EmailAddress(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    email: EmailStr
    code: str
    new_password: str

# Cart
class CartItemBase(BaseModel):
    product_id: int
    quantity: conint(gt=0)

class CartItem(CartItemBase):
    id: int

    class Config:
        orm_mode = True


class WishlistItemBase(BaseModel):
    product_id: int


class WishlistItem(WishlistItemBase):
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
    shipping_address_id: int
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


# -------- Additional Schemas --------
class AddressBase(BaseModel):
    address_line: str
    city: str
    pincode: str
    label: Optional[str] = None
    is_default: bool = False


class Address(AddressBase):
    id: int

    class Config:
        orm_mode = True


class ReviewBase(BaseModel):
    rating: int
    comment: Optional[str] = None


class Review(ReviewBase):
    id: int
    user_id: int
    product_id: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True


class Coupon(BaseModel):
    id: int
    code: str
    discount_percent: int
    active: bool

    class Config:
        orm_mode = True


class WalletTransaction(BaseModel):
    id: int
    user_id: int
    amount: float
    description: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        orm_mode = True


class Notification(BaseModel):
    id: int
    user_id: int
    message: str
    created_at: datetime.datetime
    read: bool

    class Config:
        orm_mode = True


class OTPRequest(BaseModel):
    id: int
    phone_number: str
    code: str
    expires_at: datetime.datetime
    verified: bool

    class Config:
        orm_mode = True
