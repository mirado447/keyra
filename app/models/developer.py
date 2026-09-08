from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from app.database import Base

class Developer(Base): 
    __tablename__ = "developers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255),unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    create_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))