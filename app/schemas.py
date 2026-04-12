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

