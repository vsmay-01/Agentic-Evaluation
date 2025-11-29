from pydantic import BaseModel
from typing import Any, Dict

class EvaluationResponse(BaseModel):
    id: str
    score: float
    details: Dict[str, Any] = {}
