from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class UserAgentDefinition(BaseModel):
    id: Optional[int]
    created_by_user_id: int
    name: str
    description: str
    characteristics: Dict[str, Any]
    is_predefined: bool
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
