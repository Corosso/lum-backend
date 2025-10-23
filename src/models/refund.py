from sqlalchemy import BigInteger, Column, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base

class Refund(Base):
    __tablename__ = "refunds"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    external_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    payment_intent_id = Column(BigInteger, ForeignKey("payment_intents.id"))
    order_id = Column(BigInteger, ForeignKey("orders.id"))
    amount_cop = Column(BigInteger, nullable=False)
    reason = Column(Text)
    fee_cop = Column(BigInteger, nullable=False, server_default="0")
    status = Column(Text, nullable=False, server_default="requested")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    processed_at = Column(DateTime(timezone=True))

    # Relaciones
    order = relationship("Order", back_populates="refunds")
    payment_intent = relationship("PaymentIntent")