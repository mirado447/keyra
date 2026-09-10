from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ApplicationCreate(BaseModel):
    name: str

class ApplicationOut(BaseModel):
    id: int
    name: str
    public_key: str
    create_at: datetime
    end_user_count: int = 0

    model_config = ConfigDict(from_attributes=True)

class ApplicationCreated(ApplicationOut):
    private_key: str