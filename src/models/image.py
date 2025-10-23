from sqlalchemy import BigInteger, Column, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from ..db import Base

class Image(Base):
    __tablename__ = "images"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    external_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    owner_type = Column(Text, nullable=False)
    owner_id = Column(BigInteger, nullable=False)
    object_key = Column(Text, nullable=False)
    variant = Column(Text)
    width = Column(BigInteger)
    height = Column(BigInteger)
    format = Column(Text)
    is_primary = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    deleted_at = Column(DateTime(timezone=True))
