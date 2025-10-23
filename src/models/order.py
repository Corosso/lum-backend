from sqlalchemy import BigInteger, Boolean, Column, DateTime, Text, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base
from .payment_intent import PaymentIntent
from .refund import Refund
from .payout import Payout
from .product import Product
from .product_variant import ProductVariant

class Order(Base):
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    external_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    total_amount_cop = Column(BigInteger, nullable=False)
    currency = Column(Text, nullable=False, server_default="COP")
    status = Column(Text, nullable=False, server_default="pending")
    shipping_address = Column(JSONB)
    billing_address = Column(JSONB)
    order_metadata = Column(JSONB)  # Cambiado de metadataimg a order_metadata
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relaciones
    user = relationship("User", back_populates="orders")
    sub_orders = relationship("SubOrder", back_populates="order", cascade="all, delete-orphan")
    payment_intents = relationship("PaymentIntent", back_populates="order")
    order_messages = relationship("OrderMessage", back_populates="order", cascade="all, delete-orphan")
    refunds = relationship("Refund", back_populates="order")

    __table_args__ = (
        Index("orders_user_id_idx", "user_id"),
        Index("orders_created_at_idx", "created_at"),
    )

class SubOrder(Base):
    __tablename__ = "sub_orders"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    external_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False)
    store_id = Column(BigInteger, ForeignKey("stores.id"), nullable=False)
    subtotal_cop = Column(BigInteger, nullable=False)
    shipping_cop = Column(BigInteger, nullable=False, server_default="0")
    marketplace_fee_cop = Column(BigInteger, nullable=False, server_default="0")
    seller_net_cop = Column(BigInteger, nullable=False)
    status = Column(Text, nullable=False, server_default="pending")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relaciones
    order = relationship("Order", back_populates="sub_orders")
    store = relationship("Store", back_populates="sub_orders")
    order_items = relationship("OrderItem", back_populates="sub_order", cascade="all, delete-orphan")
    payouts = relationship("Payout", back_populates="sub_order")

    __table_args__ = (
        Index("sub_orders_order_id_idx", "order_id"),
        Index("sub_orders_store_id_idx", "store_id"),
    )

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sub_order_id = Column(BigInteger, ForeignKey("sub_orders.id"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    product_variant_id = Column(BigInteger, ForeignKey("product_variants.id"))
    title = Column(Text, nullable=False)
    unit_price_cop = Column(BigInteger, nullable=False)
    quantity = Column(BigInteger, nullable=False)
    total_price_cop = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relaciones
    sub_order = relationship("SubOrder", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")
    product_variant = relationship("ProductVariant", back_populates="order_items")

    __table_args__ = (
        Index("order_items_sub_order_id_idx", "sub_order_id"),
        Index("order_items_product_id_idx", "product_id"),
    )

class OrderMessage(Base):
    __tablename__ = "order_messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False)
    from_user_id = Column(BigInteger, ForeignKey("users.id"))
    to_user_id = Column(BigInteger, ForeignKey("users.id"))
    body = Column(Text, nullable=False)
    attachments = Column(JSONB)
    is_read = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relaciones
    order = relationship("Order", back_populates="order_messages")
    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="sent_messages")
    to_user = relationship("User", foreign_keys=[to_user_id], back_populates="received_messages")

    __table_args__ = (
        Index("order_messages_order_id_idx", "order_id"),
        Index("order_messages_from_user_id_idx", "from_user_id"),
        Index("order_messages_to_user_id_idx", "to_user_id"),
    )
