from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

class EndUserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class EndUserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    create_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EndUserLogin(BaseModel):
    email: EmailStr
    password: str