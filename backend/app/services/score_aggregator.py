"""
Score aggregation for multi-dimensional evaluation.
Combines rule-based and LLM-based scores into a final evaluation score.
"""

def aggregate_scores(scores: list) -> float:
    """
    Aggregate individual dimension scores into a final score.
    
    Handles empty lists and normalizes to 0-1 range.
    
    Args:
        scores: list of float scores (each 0-1)
    
    Returns:
        float: aggregated final score (0-1)
    """
    if not scores:
        return 0.0
    
    # Simple average (can be enhanced with weighted average)
    final = sum(scores) / len(scores)
    return max(0.0, min(1.0, final))


def aggregate_scores_weighted(scores: dict, weights: dict) -> float:
    """
    Weighted aggregation of scores by dimension.
    
    Args:
        scores: dict of dimension -> score (0-1)
        weights: dict of dimension -> weight (sums to 1)
    
    Returns:
        float: weighted final score (0-1)
    """
    if not scores:
        return 0.0
    
    weighted_sum = sum(scores.get(dim, 0) * weights.get(dim, 0) for dim in weights)
    total_weight = sum(weights.values())
    
    if total_weight == 0:
        return 0.0
    
    final = weighted_sum / total_weight
    return max(0.0, min(1.0, final))
