from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ProductCreate(BaseModel):
    type: str
    pvzId: UUID

class ProductOut(BaseModel):
    id: UUID
    dateTime: datetime
    type: str
    receptionId: UUID
