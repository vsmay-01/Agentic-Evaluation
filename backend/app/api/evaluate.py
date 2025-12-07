ssufrom fastapi import APIRouter
from ..models.request_model import EvaluationRequest
from ..models.response_model import EvaluationResponse
from ..services import llm_judge, rule_based, score_aggregator
from ..storage import save_results

router = APIRouter()

@router.post("/", response_model=EvaluationResponse)
def evaluate(req: EvaluationRequest):
    """
    Evaluate agent responses on multiple dimensions:
    - Instruction Following: Does the response follow the prompt exactly?
    - Hallucination Prevention: Are facts accurate or made up?
    - Assumption Prevention: Does it avoid unnecessary assumptions?
    - Response Coherence: Is the response logically structured?
    - Response Accuracy: Does it answer the query correctly?
    
    Uses real LLM (GPT-4, Claude) or falls back to heuristics.
    """
    scores = {}
    details = {}
    all_dimension_scores = {
        "instruction_following": [],
        "hallucination_prevention": [],
        "assumption_prevention": [],
        "coherence": [],
        "accuracy": []
    }
    
    for i, input_item in enumerate(req.inputs):
        prompt = input_item.prompt
        agent_response = input_item.agent_response
        reference = input_item.reference  # Optional, used for accuracy comparison
        
        # Rule-based checks (instruction following, coherence, basic accuracy)
        # Evaluate agent_response against the prompt
        rule_result = rule_based.apply_rule_checks(prompt, agent_response)
        scores[f"input_{i}_rule_score"] = rule_result.get("score", 0.0)
        details[f"input_{i}_rule_issues"] = rule_result.get("issues", [])
        
        # LLM-based evaluation (hallucination, assumption prevention, accuracy)
        # Evaluate agent_response against the prompt, optionally using reference for accuracy
        llm_result = llm_judge.judge_with_llm(prompt, agent_response, reference=reference)
        scores[f"input_{i}_llm_score"] = llm_result.get("score", 0.0)
        details[f"input_{i}_llm_reason"] = llm_result.get("reason", "")
        
        # Track dimension scores
        dim_scores = llm_result.get("dimension_scores", {})
        for dim, val in dim_scores.items():
            if dim in all_dimension_scores:
                all_dimension_scores[dim].append(val)
    
    # Aggregate all scores
    from ..core.config import settings
    
    if settings.use_weighted_scoring and aggregated_dimensions:
        # Use weighted aggregation
        final_score = score_aggregator.aggregate_scores_weighted(
            aggregated_dimensions,
            settings.dimension_weights
        )
    else:
        # Use simple average
        score_list = [v for k, v in scores.items() if isinstance(v, float)]
        final_score = score_aggregator.aggregate_scores(score_list)
    
    # Calculate average per dimension
    aggregated_dimensions = {}
    for dim, values in all_dimension_scores.items():
        if values:
            aggregated_dimensions[dim] = sum(values) / len(values)
    
    # Save to storage
    result_obj = {
        "id": req.id,
        "model_name": req.model_name,
        "final_score": final_score,
        "dimension_scores": aggregated_dimensions,
        "individual_scores": scores,
        "details": details,
        "inputs": [
            {
                "prompt": inp.prompt,
                "agent_response": inp.agent_response,
                "reference": inp.reference
            }
            for inp in req.inputs
        ]
    }
    save_results.save_result(result_obj)
    
    return {
        "id": req.id,
        "score": final_score,
        "details": {
            "dimension_scores": aggregated_dimensions,
            "individual_scores": scores,
            "evaluation_details": details,
            "model_name": req.model_name,
        }
    }