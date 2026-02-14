from typing import Optional, List
from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from datetime import datetime

class Fact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    category: str  # e.g., "Project", "Personal", "Preference"
    content: str
    confidence_score: float = Field(default=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class Memory(BaseModel):
    content: str
    metadata: dict = {}
