from sqlalchemy import BigInteger, Column, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..db import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    external_id = Column(Text, nullable=False)
    store_id = Column(BigInteger, ForeignKey("stores.id"), nullable=False)
    sku = Column(Text)
    title = Column(Text, nullable=False)
    description = Column(Text)
    condition = Column(Text, default='new')
    price_cop = Column(BigInteger, nullable=False)
    currency = Column(Text, default='COP')
    is_published = Column(BigInteger, default=False)
    is_visible = Column(BigInteger, default=True)
    attributes = Column(Text)  # jsonb, pero para SQLAlchemy simple puede ser Text
    created_at = Column(Text)  # timestamp with time zone, para SQLAlchemy simple puede ser Text
    updated_at = Column(Text)  # timestamp with time zone
    deleted_at = Column(Text)

    # Relación inversa
    order_items = relationship("OrderItem", back_populates="product")
    store = relationship("Store", back_populates="products")