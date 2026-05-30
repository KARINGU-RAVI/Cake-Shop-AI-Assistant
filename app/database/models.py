import datetime
import uuid
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.db import Base

def generate_uuid():
    return str(uuid.uuid4())

class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, default=generate_uuid)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    preferred_language = Column(String, default="English")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="customer", cascade="all, delete-orphan")


class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=generate_uuid)
    customer_id = Column(String, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default="PENDING")  # PENDING, CONFIRMED, COMPLETED, CANCELLED
    delivery_type = Column(String, nullable=True)  # DELIVERY, PICKUP
    address = Column(String, nullable=True)
    delivery_date = Column(String, nullable=True)
    delivery_time = Column(String, nullable=True)
    name_on_cake = Column(String, nullable=True)
    message_on_cake = Column(String, nullable=True)
    total_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="order", uselist=False, cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String, primary_key=True, default=generate_uuid)
    order_id = Column(String, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_name = Column(String, nullable=False)
    size = Column(String, nullable=False)  # 1kg, 2kg, 3kg
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)

    # Relationships
    order = relationship("Order", back_populates="items")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=generate_uuid)
    order_id = Column(String, ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="PENDING")  # PENDING, COMPLETED, FAILED
    payment_link = Column(String, nullable=True)
    transaction_reference = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="payment")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    customer_id = Column(String, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    sender_type = Column(String, nullable=False)  # USER, AGENT
    content = Column(String, nullable=False)
    whatsapp_message_id = Column(String, unique=True, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="messages")
