from sqlalchemy import BigInteger, Column, Text, Numeric, DateTime
from sqlalchemy.sql import func
from ..db import Base

class Plan(Base):
    __tablename__ = "plans"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    plan_key = Column(Text, nullable=False, unique=True)
    display_name = Column(Text, nullable=False)
    monthly_price_cop = Column(BigInteger, nullable=False, server_default="0")
    annual_price_cop = Column(BigInteger)
    commission_rate = Column(Numeric(5,3), nullable=False)
    product_limit = Column(BigInteger)
    subuser_limit = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
