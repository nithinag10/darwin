# schemas/documentation_source_schemas.py
from pydantic import BaseModel, AnyUrl, ConfigDict
from typing import Optional
from datetime import datetime

class DocumentationSourceSchema(BaseModel):
    id: Optional[int] = None
    product_id: int
    type: str
    url: AnyUrl  # Accepts valid URL strings
    storage_url: Optional[str]
    file_size: Optional[int]
    content_type: Optional[str]
    fetched_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)