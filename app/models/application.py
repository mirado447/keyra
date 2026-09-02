from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.database import Base

class Application(Base):

    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    public_key = Column(String(255), unique=True, nullable=False)
    private_key_hash = Column(String(255), nullable=False)
    create_at = Column(DateTime, default=datetime.utcnow)
    id_developer = Column(Integer, ForeignKey("developers.id"), nullable= False)