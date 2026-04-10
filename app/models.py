"""
SQLAlchemy ORM models for all entities and actors, following OOP design.
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .database import Base
import enum
import datetime

class RoleEnum(str, enum.Enum):
    customer = "customer"
    restaurant_owner = "restaurant_owner"
    delivery_agent = "delivery_agent"
    customer_support = "customer_support"
    admin = "admin"

class UserAccount(Base):
    __tablename__ = "user_accounts"
    user_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    # Relationships
    customer = relationship("Customer", uselist=False, back_populates="user")
    restaurant_owner = relationship("RestaurantOwner", uselist=False, back_populates="user")
    delivery_agent = relationship("DeliveryAgent", uselist=False, back_populates="user")
    customer_support = relationship("CustomerSupport", uselist=False, back_populates="user")
