"""
Pydantic schemas for request/response validation.
"""
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
import enum

class RoleEnum(str, enum.Enum):
    customer = "customer"
    restaurant_owner = "restaurant_owner"
    delivery_agent = "delivery_agent"
    customer_support = "customer_support"
    admin = "admin"

class UserAccountBase(BaseModel):
    user_id: str
    name: str
    phone: str
    email: EmailStr
    role: RoleEnum

class UserAccountCreate(BaseModel):
    name: str
    phone: str
    email: EmailStr
    password: str
    role: RoleEnum

class UserAccountOut(UserAccountBase):
    pass

class CustomerCreate(BaseModel):
    name: str
    phone: str
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[RoleEnum] = None

class MenuItemBase(BaseModel):
    item_id: str
    name: str
    description: Optional[str]
    price: float
    category: Optional[str]
    is_available: bool
    restaurant_id: str

class MenuItemCreate(BaseModel):
    name: str
    description: Optional[str]
    price: float
    category: Optional[str]
    is_available: bool = True
    restaurant_id: str

class MenuItemOut(MenuItemBase):
    pass

class OrderBase(BaseModel):
    order_id: str
    customer_id: str
    restaurant_id: str
    agent_id: Optional[str]
    status: str
    total_amount: float
    placed_at: str

class OrderCreate(BaseModel):
    customer_id: str
    restaurant_id: str
    items: List[dict] # [{item_id, quantity}]

class OrderOut(OrderBase):
    pass

class PaymentBase(BaseModel):
    payment_id: str
    order_id: str
    amount: float
    method: str
    status: str
    transaction_ref: Optional[str]

class PaymentCreate(BaseModel):
    order_id: str
    amount: float
    method: str

class PaymentOut(PaymentBase):
    pass

class SupportTicketBase(BaseModel):
    ticket_id: str
    customer_id: str
    order_id: Optional[str]
    support_id: Optional[str]
    issue_type: str
    description: str
    status: str
    created_at: str

class SupportTicketCreate(BaseModel):
    customer_id: str
    order_id: Optional[str]
    issue_type: str
    description: str

class SupportTicketOut(SupportTicketBase):
    pass

class RatingBase(BaseModel):
    rating_id: str
    order_id: str
    customer_id: str
    stars: int
    comment: Optional[str]
    created_at: str

class RatingCreate(BaseModel):
    order_id: str
    customer_id: str
    stars: int
    comment: Optional[str]

class RatingOut(RatingBase):
    pass

class NotificationBase(BaseModel):
    notification_id: str
    user_id: str
    message: str
    created_at: str
    is_read: bool

class NotificationCreate(BaseModel):
    user_id: str
    message: str

class NotificationOut(NotificationBase):
    pass
