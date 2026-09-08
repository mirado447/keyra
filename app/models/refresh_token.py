from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime, timezone
from app.database import Base

class RefreshToken(Base):

    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token_hash = Column(String(255), unique=True, nullable=False)
    create_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    revoked = Column(Boolean, default=False)
    expire_at = Column(DateTime(timezone=True), nullable=False)
    id_user = Column(Integer, ForeignKey("endusers.id"), nullable=False)