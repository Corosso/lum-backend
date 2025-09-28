# src/models/users.py
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    external_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    email = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text)
    full_name = Column(Text)
    phone = Column(Text)
    is_verified = Column(Boolean, nullable=False, server_default="false")
    can_sell = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    # Relaciones
    orders = relationship("Order", back_populates="user")
    owned_stores = relationship("Store", back_populates="owner")
    sent_messages = relationship("OrderMessage", foreign_keys="OrderMessage.from_user_id", back_populates="from_user")
    received_messages = relationship("OrderMessage", foreign_keys="OrderMessage.to_user_id", back_populates="to_user")

    __table_args__ = (
        Index("users_created_at_idx", "created_at"),
        Index("users_email_idx", "email"),
    )