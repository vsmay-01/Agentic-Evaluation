"""
Batch evaluation API endpoints for processing 1000s of responses.
"""

from fastapi import APIRouter, BackgroundTasks
from typing import List, Dict, Any
from ..models.request_model import EvaluationRequest, EvaluationInput
from ..models.response_model import EvaluationResponse
from ..services import llm_judge, rule_based, score_aggregator
from ..services.batch_processor import batch_processor
from ..storage import save_results

router = APIRouter()

# Store batch status for tracking
batch_status: Dict[str, Dict[str, Any]] = {}


def evaluate_single_input(request_id: str, model_name: str, input_item: EvaluationInput) -> Dict[str, Any]:
    """Evaluate a single input item."""
    prompt = input_item.prompt
    reference = input_item.reference or ""
    
    # Rule-based checks
    rule_result = rule_based.apply_rule_checks(prompt, reference)
    rule_score = rule_result.get("score", 0.0)
    rule_issues = rule_result.get("issues", [])
    
    # LLM evaluation
    llm_result = llm_judge.judge_with_llm(prompt, reference)
    llm_score = llm_result.get("score", 0.0)
    llm_reason = llm_result.get("reason", "")
    dim_scores = llm_result.get("dimension_scores", {})
    
    # Aggregate
    final_score = score_aggregator.aggregate_scores([rule_score, llm_score])
    
    return {
        "id": f"{request_id}-{input_item}",
        "score": final_score,
        "details": {
            "dimension_scores": dim_scores,
            "rule_issues": rule_issues,
            "llm_reason": llm_reason,
        }
    }


@router.post("/batch", response_model=Dict[str, Any])
async def evaluate_batch(req: EvaluationRequest, background_tasks: BackgroundTasks):
    """
    Submit a batch of agent responses for evaluation.
    
    Supports 1000s of responses with async processing.
    
    Request:
        {
            "id": "batch-001",
            "model_name": "gpt-4",
            "inputs": [
                {"prompt": "...", "reference": "..."},
                ...
            ]
        }
    
    Response:
        {
            "batch_id": "batch-001",
            "status": "processing",
            "total": 1000,
            "message": "Batch queued for processing"
        }
    """
    batch_id = req.id
    batch_status[batch_id] = {
        "status": "processing",
        "total": len(req.inputs),
        "processed": 0,
        "result": None
    }
    
    # Queue batch processing in background
    background_tasks.add_task(
        _process_batch,
        batch_id,
        req
    )
    
    return {
        "batch_id": batch_id,
        "status": "queued",
        "total": len(req.inputs),
        "message": f"Batch {batch_id} queued for processing. Check /batch/status/{batch_id} for progress."
    }


async def _process_batch(batch_id: str, req: EvaluationRequest):
    """Background task to process batch."""
    try:
        async def progress_callback(processed: int, total: int):
            batch_status[batch_id]["processed"] = processed
        
        result = await batch_processor.process_batch_async(
            request_id=batch_id,
            model_name=req.model_name,
            inputs=req.inputs,
            evaluate_func=evaluate_single_input,
            progress_callback=progress_callback
        )
        
        # Save batch result
        save_results.save_result(result)
        
        batch_status[batch_id]["status"] = "completed"
        batch_status[batch_id]["result"] = result
        
    except Exception as e:
        batch_status[batch_id]["status"] = "failed"
        batch_status[batch_id]["error"] = str(e)


@router.get("/batch/status/{batch_id}")
def get_batch_status(batch_id: str) -> Dict[str, Any]:
    """
    Get status of a batch evaluation job.
    
    Returns:
        {
            "batch_id": "batch-001",
            "status": "processing|completed|failed",
            "total": 1000,
            "processed": 500,
            "result": {...}  # if completed
        }
    """
    if batch_id not in batch_status:
        return {
            "batch_id": batch_id,
            "status": "not_found",
            "message": "Batch not found"
        }
    
    return batch_status[batch_id]


@router.get("/batch/result/{batch_id}")
def get_batch_result(batch_id: str) -> Dict[str, Any]:
    """
    Get final result of a completed batch.
    
    Returns full batch summary with dimension averages and score distribution.
    """
    if batch_id not in batch_status or batch_status[batch_id]["status"] != "completed":
        return {
            "error": f"Batch {batch_id} not completed or not found"
        }
    
    return batch_status[batch_id]["result"]
