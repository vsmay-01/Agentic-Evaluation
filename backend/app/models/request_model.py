from pydantic import BaseModel
from typing import List, Optional

class EvaluationInput(BaseModel):
    prompt: str
    reference: Optional[str] = None

class EvaluationRequest(BaseModel):
    id: str
    model_name: str
    inputs: List[EvaluationInput]
