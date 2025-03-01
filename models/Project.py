from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class Project(BaseModel):
    id: Optional[int] = None
    name: str
    user_id: int
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
