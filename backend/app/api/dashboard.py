"""
Dashboard API endpoints for analytics and statistics.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Dict, Any, List
from datetime import datetime, timedelta
from ..storage.database import get_db, Evaluation, BatchEvaluation

router = APIRouter()


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get overall dashboard statistics."""
    
    # Total evaluations
    total_evaluations = db.query(func.count(Evaluation.id)).scalar() or 0
    
    # Average score
    avg_score = db.query(func.avg(Evaluation.final_score)).scalar() or 0.0
    
    # Models evaluated
    models_count = db.query(func.count(func.distinct(Evaluation.model_name))).scalar() or 0
    
    # Excellent responses (score >= 0.9)
    excellent_count = db.query(func.count(Evaluation.id)).filter(
        Evaluation.final_score >= 0.9
    ).scalar() or 0
    
    return {
        "total_evaluations": total_evaluations,
        "average_score": round(float(avg_score), 4),
        "models_evaluated": models_count,
        "excellent_responses": excellent_count,
    }


@router.get("/dimension-stats")
def get_dimension_stats(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get average scores per dimension."""
    
    evaluations = db.query(Evaluation).all()
    
    dimension_totals = {
        "instruction_following": [],
        "hallucination_prevention": [],
        "assumption_prevention": [],
        "coherence": [],
        "accuracy": [],
    }
    
    for eval in evaluations:
        if eval.dimension_scores:
            for dim, score in eval.dimension_scores.items():
                if dim in dimension_totals:
                    dimension_totals[dim].append(score)
    
    result = []
    for dim, scores in dimension_totals.items():
        if scores:
            avg = sum(scores) / len(scores)
            result.append({
                "name": dim.replace("_", " ").title(),
                "score": round(avg, 4),
            })
    
    return result


@router.get("/model-comparison")
def get_model_comparison(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get comparison statistics by model."""
    
    results = db.query(
        Evaluation.model_name,
        func.avg(Evaluation.final_score).label("avg_score"),
        func.count(Evaluation.id).label("count")
    ).group_by(Evaluation.model_name).all()
    
    return [
        {
            "model": r.model_name,
            "score": round(float(r.avg_score), 4),
            "count": r.count,
        }
        for r in results
    ]


@router.get("/score-distribution")
def get_score_distribution(db: Session = Depends(get_db)) -> Dict[str, int]:
    """Get score distribution across categories."""
    
    excellent = db.query(func.count(Evaluation.id)).filter(
        Evaluation.final_score >= 0.9
    ).scalar() or 0
    
    good = db.query(func.count(Evaluation.id)).filter(
        Evaluation.final_score >= 0.7,
        Evaluation.final_score < 0.9
    ).scalar() or 0
    
    fair = db.query(func.count(Evaluation.id)).filter(
        Evaluation.final_score >= 0.5,
        Evaluation.final_score < 0.7
    ).scalar() or 0
    
    poor = db.query(func.count(Evaluation.id)).filter(
        Evaluation.final_score < 0.5
    ).scalar() or 0
    
    return {
        "excellent": excellent,
        "good": good,
        "fair": fair,
        "poor": poor,
    }


@router.get("/trend")
def get_score_trend(
    days: int = 7,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get score trend over time."""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    results = db.query(
        func.date(Evaluation.created_at).label("date"),
        func.avg(Evaluation.final_score).label("avg_score")
    ).filter(
        Evaluation.created_at >= start_date
    ).group_by(
        func.date(Evaluation.created_at)
    ).order_by(
        func.date(Evaluation.created_at)
    ).all()
    
    return [
        {
            "date": r.date.strftime("%b %d"),
            "score": round(float(r.avg_score), 4),
        }
        for r in results
    ]


@router.get("/recent")
def get_recent_evaluations(
    limit: int = 10,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get recent evaluations."""
    
    evaluations = db.query(Evaluation).order_by(
        desc(Evaluation.created_at)
    ).limit(limit).all()
    
    return [
        {
            "id": e.id,
            "model": e.model_name,
            "score": round(float(e.final_score), 4),
            "date": e.created_at.strftime("%Y-%m-%d") if e.created_at else "",
        }
        for e in evaluations
    ]

