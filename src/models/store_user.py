from sqlalchemy import BigInteger, Column, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base

class StoreUser(Base):
    __tablename__ = "store_users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    store_id = Column(BigInteger, ForeignKey("stores.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    role = Column(Text, nullable=False)
    can_admin_products = Column(Boolean, nullable=False, server_default="false")
    can_view_reports = Column(Boolean, nullable=False, server_default="false")
    can_manage_inventory = Column(Boolean, nullable=False, server_default="false")
    can_handle_messages = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    # Relaciones
    store = relationship("Store", back_populates="store_users")
    user = relationship("User")
