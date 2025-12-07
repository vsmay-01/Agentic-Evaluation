"""
Save evaluation results to both database and JSON (for backward compatibility).
"""

from pathlib import Path
import json
from datetime import datetime
from .database import SessionLocal, Evaluation, BatchEvaluation


DATA_FILE = Path(__file__).resolve().parents[2] / ".." / ".." / "data" / "evaluations.json"


def save_result(result: dict):
    """
    Save evaluation result to both database and JSON file.
    
    Args:
        result: Dictionary containing evaluation results
    """
    # Save to database
    try:
        db = SessionLocal()
        try:
            # Check if evaluation already exists
            existing = db.query(Evaluation).filter(Evaluation.id == result.get("id")).first()
            
            eval_data = {
                "id": result.get("id"),
                "model_name": result.get("model_name", "unknown"),
                "final_score": result.get("final_score") or result.get("score", 0.0),
                "dimension_scores": result.get("dimension_scores", {}),
                "individual_scores": result.get("individual_scores", {}),
                "details": result.get("details", {}),
            }
            
            # Extract prompt, agent_response and reference from inputs if available
            if "inputs" in result and result["inputs"]:
                eval_data["prompt"] = result["inputs"][0].get("prompt", "")
                eval_data["agent_response"] = result["inputs"][0].get("agent_response", "")
                eval_data["reference"] = result["inputs"][0].get("reference", "")
            
            if existing:
                # Update existing
                for key, value in eval_data.items():
                    setattr(existing, key, value)
            else:
                # Create new
                evaluation = Evaluation(**eval_data)
                db.add(evaluation)
            
            db.commit()
        finally:
            db.close()
    except Exception as e:
        print(f"Database save failed: {e}. Falling back to JSON only.")
    
    # Also save to JSON for backward compatibility
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = []
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = []
    data.append(result)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def save_batch_result(batch_id: str, result: dict):
    """
    Save batch evaluation result to database.
    
    Args:
        batch_id: Unique batch identifier
        result: Dictionary containing batch results
    """
    try:
        db = SessionLocal()
        try:
            existing = db.query(BatchEvaluation).filter(BatchEvaluation.batch_id == batch_id).first()
            
            batch_data = {
                "batch_id": batch_id,
                "model_name": result.get("model_name", "unknown"),
                "total_evaluated": result.get("total_evaluated", 0),
                "average_score": result.get("average_score", 0.0),
                "dimension_averages": result.get("dimension_averages", {}),
                "score_distribution": result.get("score_distribution", {}),
                "results": result.get("results", []),
                "status": "completed",
                "completed_at": datetime.utcnow(),
            }
            
            if existing:
                for key, value in batch_data.items():
                    setattr(existing, key, value)
            else:
                batch_eval = BatchEvaluation(**batch_data)
                db.add(batch_eval)
            
            db.commit()
        finally:
            db.close()
    except Exception as e:
        print(f"Database save failed: {e}")
