from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class PVZCreate(BaseModel):
    city: str

class PVZOut(BaseModel):
    id: UUID
    registrationDate: datetime
    city: str
