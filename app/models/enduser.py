from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime, timezone
from app.database import Base

class Enduser(Base):

    __tablename__ = "endusers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    create_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    id_app = Column(Integer, ForeignKey("applications.id"), nullable=False)