from pydantic import BaseModel, ConfigDict
from typing import Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class EvaluationStatus(Enum):
    START = "START"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


@dataclass
class Evaluation:
    id: Optional[int] = None
    name: str = ""
    status: EvaluationStatus = EvaluationStatus.START
    product_id: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
