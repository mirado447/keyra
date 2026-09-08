from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

# Représente les données nécessaires pour créer un nouveau développeur
class DeveloperCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
# Représente les données d'un développeur retournées par l'API
class DeveloperOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    create_at: datetime

# Représente les identifiants nécessaires pour se connecter
class DeveloperLogin(BaseModel):
    email: str
    password: str

    model_config = ConfigDict(from_attributes=True)