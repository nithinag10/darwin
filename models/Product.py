from pydantic import BaseModel, ConfigDict
from typing import Optional

class Product(BaseModel):
    id: Optional[int] = None
    project_id: int
    name: str
    custom_instructions: Optional[str] = None
    created_at: Optional[str] = None  # Use datetime if needed
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)