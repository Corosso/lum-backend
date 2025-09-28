# src/models/store.py
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Text, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base

class Store(Base):
    __tablename__ = "stores"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    external_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    owner_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    name = Column(Text, nullable=False)
    slug = Column(Text, nullable=False)
    description = Column(Text)
    logo_key = Column(Text)
    banner_key = Column(Text)
    country = Column(Text, nullable=False, server_default="CO")
    city = Column(Text)
    is_active = Column(Boolean, nullable=False, server_default="true")
    plan = Column(Text, nullable=False, server_default="free")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    # Relaciones
    owner = relationship("User", back_populates="owned_stores")
    sub_orders = relationship("SubOrder", back_populates="store")
    products = relationship("Product", back_populates="store", cascade="all, delete-orphan")
    store_users = relationship("StoreUser", back_populates="store", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="store", cascade="all, delete-orphan")

    __table_args__ = (
        Index("stores_owner_user_id_slug_idx", "owner_user_id", "slug"),
        Index("stores_plan_idx", "plan"),
    )
