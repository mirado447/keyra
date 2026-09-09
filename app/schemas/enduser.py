from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime

class EndUserCreate(BaseModel):
    name: str = Field(min_length=2, max_digits=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

class EndUserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    create_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EndUserLogin(BaseModel):
    email: EmailStr
    password: str