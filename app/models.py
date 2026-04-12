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


class Customer(Base):
    __tablename__ = "customers"
    user_id = Column(String, ForeignKey("user_accounts.user_id"), primary_key=True)
    wallet_balance = Column(Float, default=0.0)
    loyalty_points = Column(Integer, default=0)
    user = relationship("UserAccount", back_populates="customer")
    orders = relationship("Order", back_populates="customer")
    tickets = relationship("SupportTicket", back_populates="customer")

class RestaurantOwner(Base):
    __tablename__ = "restaurant_owners"
    user_id = Column(String, ForeignKey("user_accounts.user_id"), primary_key=True)
    restaurant_id = Column(String, unique=True, nullable=False)
    restaurant_name = Column(String, nullable=False)
    opening_hours = Column(String)
    is_verified = Column(Boolean, default=False)
    user = relationship("UserAccount", back_populates="restaurant_owner")
    menu_items = relationship("MenuItem", back_populates="restaurant_owner")
    orders = relationship("Order", back_populates="restaurant_owner")

    def verify_restaurant(self):
        """OOP method to transition a restaurant to verified state"""
        self.is_verified = True


class DeliveryAgent(Base):
    __tablename__ = "delivery_agents"
    user_id = Column(String, ForeignKey("user_accounts.user_id"), primary_key=True)
    agent_id = Column(String, unique=True, nullable=False)
    vehicle_type = Column(String)
    current_location = Column(String)
    is_available = Column(Boolean, default=True)
    user = relationship("UserAccount", back_populates="delivery_agent")
    orders = relationship("Order", back_populates="delivery_agent")

class CustomerSupport(Base):
    __tablename__ = "customer_supports"
    user_id = Column(String, ForeignKey("user_accounts.user_id"), primary_key=True)
    support_id = Column(String, unique=True, nullable=False)
    availability_status = Column(String, default="AVAILABLE")
    department = Column(String)
    user = relationship("UserAccount", back_populates="customer_support")
    assigned_tickets = relationship("SupportTicket", back_populates="support_agent")

class OrderStatus(str, enum.Enum):
    pending = "PENDING"
    confirmed = "CONFIRMED"
    accepted = "ACCEPTED"
    preparing = "PREPARING"
    out_for_delivery = "OUT_FOR_DELIVERY"
    delivered = "DELIVERED"
    cancelled = "CANCELLED"

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.user_id"))
    restaurant_id = Column(String, ForeignKey("restaurant_owners.restaurant_id"))
    agent_id = Column(String, ForeignKey("delivery_agents.agent_id"), nullable=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    total_amount = Column(Float, default=0.0)
    special_instructions = Column(String, nullable=True)
    delivery_address = Column(String, nullable=False, default="Default Address")
    placed_at = Column(DateTime, default=datetime.datetime.utcnow)
    customer = relationship("Customer", back_populates="orders")
    restaurant_owner = relationship("RestaurantOwner", back_populates="orders")
    delivery_agent = relationship("DeliveryAgent", back_populates="orders")
    items = relationship("OrderMenuItem", back_populates="order")
    payment = relationship("Payment", uselist=False, back_populates="order")

class MenuItem(Base):
    __tablename__ = "menu_items"
    item_id = Column(String, primary_key=True, index=True)
    restaurant_id = Column(String, ForeignKey("restaurant_owners.restaurant_id"))
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    category = Column(String)
    is_available = Column(Boolean, default=True)
    restaurant_owner = relationship("RestaurantOwner", back_populates="menu_items")
    orders = relationship("OrderMenuItem", back_populates="menu_item")

class OrderMenuItem(Base):
    __tablename__ = "order_menu_items"
    order_id = Column(String, ForeignKey("orders.order_id"), primary_key=True)
    item_id = Column(String, ForeignKey("menu_items.item_id"), primary_key=True)
    quantity = Column(Integer, default=1)
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="orders")
