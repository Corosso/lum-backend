from sqlalchemy import BigInteger, Column, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base

class PaymentIntent(Base):
    __tablename__ = "payment_intents"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    external_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    provider = Column(Text, nullable=False)
    provider_payment_id = Column(Text)
    provider_payload = Column(JSONB)
    amount_cop = Column(BigInteger, nullable=False)
    currency = Column(Text, nullable=False, server_default="COP")
    status = Column(Text, nullable=False, server_default="created")
    order_id = Column(BigInteger, ForeignKey("orders.id"))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relaciones
    order = relationship("Order", back_populates="payment_intents")