from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ReceptionCreate(BaseModel):
    pvzId: UUID

class ReceptionOut(BaseModel):
    id: UUID
    dateTime: datetime
    # pvzId: UUID
    status: str
