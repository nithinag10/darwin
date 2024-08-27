from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime


class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)
