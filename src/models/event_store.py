from sqlalchemy import BigInteger, Column, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from ..db import Base

class EventStore(Base):
    __tablename__ = "event_store"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    topic = Column(Text, nullable=False)
    aggregate_type = Column(Text)
    aggregate_id = Column(UUID(as_uuid=True))
    payload = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
