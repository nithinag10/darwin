from pydantic import BaseModel, ConfigDict
from typing import Optional
from enum import Enum


class EvaluationStatus(str, Enum):
    START = "START"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class Evaluation(BaseModel):
    id: Optional[int] = None
    proj_id: int
    name: str
    status: EvaluationStatus = EvaluationStatus.START
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
