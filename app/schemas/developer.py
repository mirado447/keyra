from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

class DeveloperCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class DeveloperOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    create_at: datetime

    model_config = ConfigDict(from_attributes=True)