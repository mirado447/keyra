from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime
from app.database import Base

class RefreshToken(Base):

    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token_hash = Column(String(255), unique=True, nullable=False)
    create_at = Column(DateTime, default=datetime.utcnow)
    revoked = Column(Boolean, default=False)
    expire_at = Column(DateTime, default=datetime.utcnow)
    id_user = Column(Integer, ForeignKey("endusers.id"), nullable=False)