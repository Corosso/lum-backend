from sqlalchemy import BigInteger, Column, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base

class Payout(Base):
    __tablename__ = "payouts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    external_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    sub_order_id = Column(BigInteger, ForeignKey("sub_orders.id"), nullable=False)
    amount_cop = Column(BigInteger, nullable=False)
    status = Column(Text, nullable=False, server_default="pending")
    provider = Column(Text)
    provider_payout_id = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    processed_at = Column(DateTime(timezone=True))

    # Relaciones
    sub_order = relationship("SubOrder", back_populates="payouts")