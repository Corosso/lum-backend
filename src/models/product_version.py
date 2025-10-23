from sqlalchemy import BigInteger, Column, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db import Base

class ProductVersion(Base):
    __tablename__ = "product_versions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    snapshot = Column(JSONB, nullable=False)
    changed_by_user_id = Column(BigInteger, ForeignKey("users.id"))
    change_type = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relaciones
    product = relationship("Product")
    changed_by_user = relationship("User")
