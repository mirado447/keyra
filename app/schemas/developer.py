from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime

# Représente les données nécessaires pour créer un nouveau développeur
class DeveloperCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

# Représente les données d'un développeur retournées par l'API
class DeveloperOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    create_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Représente les identifiants nécessaires pour se connecter
class DeveloperLogin(BaseModel):
    email: str
    password: str