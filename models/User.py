from pydantic import BaseModel, ConfigDict
from typing import Optional


class User(BaseModel):
    id: Optional[int] = None
    name: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
