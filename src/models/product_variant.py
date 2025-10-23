from sqlalchemy import BigInteger, Column, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..db import Base

class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    name = Column(Text, nullable=False)
    # Otros campos...

    # Relación inversa (opcional, si quieres acceder a los order_items desde aquí)
    order_items = relationship("OrderItem", back_populates="product_variant")