from sqlalchemy import BigInteger, Column, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db import Base

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_variant_id = Column(BigInteger, ForeignKey("product_variants.id"))
    product_id = Column(BigInteger, ForeignKey("products.id"))
    user_id = Column(BigInteger, ForeignKey("users.id"))
    quantity = Column(BigInteger, nullable=False, server_default="1")
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    fulfilled = Column(Boolean, nullable=False, server_default="false")

    # Relaciones
    product = relationship("Product")
    product_variant = relationship("ProductVariant")
    user = relationship("User")
