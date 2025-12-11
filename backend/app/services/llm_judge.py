"""
LLM-based evaluation for agent responses.
Evaluates: hallucination prevention, assumption prevention, response accuracy.
Supports real LLM (GPT-4, Claude) or heuristic fallback.
"""

from ..core.config import settings
from .llm_provider import get_llm_provider
from typing import Dict, Any, Optional

def judge_with_llm(prompt: str, response: str, reference: Optional[str] = None) -> Dict[str, Any]:
    """
    Evaluate agent response using real LLM or heuristics.
    
    Evaluates:
    - Hallucination detection (facts not grounded in prompt)
    - Assumption prevention (unnecessary or risky assumptions)
    - Response accuracy (how well it answers the prompt)
    
    Falls back to heuristics if LLM API fails.
    
    Returns:
        dict with 'score' (0-1), 'reason' string, and 'dimension_scores'
    """
    if not settings.use_llm_evaluation:
        return judge_with_heuristics(prompt, response, reference=reference)
    
    try:
        # Build kwargs based on provider
        provider_kwargs = {}
        if settings.llm_provider == "gemini":
            provider_kwargs = {
                "model": settings.gemini_model,
                "api_key": settings.ai_studio_api_key,
                "endpoint": settings.ai_studio_endpoint,
            }
        elif settings.llm_provider == "openai":
            provider_kwargs = {
                "openai_api_key": settings.openai_api_key,
                "openai_model": settings.openai_model,
            }
        elif settings.llm_provider == "anthropic":
            provider_kwargs = {
                "anthropic_api_key": settings.anthropic_api_key,
                "anthropic_model": settings.anthropic_model,
            }
        
        provider = get_llm_provider(settings.llm_provider, **provider_kwargs)
        result = provider.evaluate_response(prompt, response, reference=reference)
        return result
        
    except Exception as e:
        if settings.use_heuristic_fallback:
            # Log error but don't expose it in response - use heuristics instead
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"LLM evaluation failed: {str(e)}. Falling back to heuristics.")
            return judge_with_heuristics(prompt, response, reference=reference)
        else:
            raise


def judge_with_heuristics(prompt: str, response: str, reference: str = None) -> Dict[str, Any]:
    """
    Fallback: Use heuristics when LLM API is unavailable.
    
    Heuristic-based evaluation on:
    - Hallucination detection (phrases that indicate speculation)
    - Assumption prevention (uncertain language)
    - Response accuracy (response detail/confidence level)
    """
    score = 0.8  # default good score
    reasons = []
    
    dimension_scores = {
        "instruction_following": 0.8,
        "hallucination_prevention": 0.8,
        "assumption_prevention": 0.8,
        "coherence": 0.8,
        "accuracy": 0.8
    }
    
    # Heuristic 1: Hallucination detection
    hallucination_phrases = ["i think", "probably", "maybe", "i guess", "it seems", "could be"]
    hallucination_count = sum(1 for phrase in hallucination_phrases if phrase in response.lower())
    if hallucination_count > 2:
        score -= 0.15
        dimension_scores["hallucination_prevention"] -= 0.2
        reasons.append(f"Detected {hallucination_count} speculative phrases (possible hallucination)")
    
    # Heuristic 2: Assumption prevention
    assumption_phrases = ["assuming", "if we assume", "without knowing", "unclear if"]
    assumption_count = sum(1 for phrase in assumption_phrases if phrase in response.lower())
    if assumption_count > 1:
        score -= 0.1
        dimension_scores["assumption_prevention"] -= 0.15
        reasons.append(f"Detected {assumption_count} assumptions")
    
    # Heuristic 3: Response consistency with prompt
    if len(response.strip()) < 50:
        score -= 0.1
        dimension_scores["accuracy"] -= 0.15
        reasons.append("Response is brief; may lack detail")
    
    # Heuristic 5: Compare with reference if provided (for accuracy)
    if reference:
        # Simple similarity check (word overlap)
        response_words = set(response.lower().split())
        reference_words = set(reference.lower().split())
        if reference_words:
            similarity = len(response_words & reference_words) / len(reference_words)
            if similarity < 0.3:
                score -= 0.1
                dimension_scores["accuracy"] -= 0.15
                reasons.append(f"Low similarity with reference ({similarity:.1%})")
    
    # Heuristic 4: Confidence language
    hedge_words = ["somewhat", "slightly", "relatively", "quite", "rather"]
    hedge_count = sum(1 for word in hedge_words if word in response.lower())
    if hedge_count > 1:
        score -= 0.05
        dimension_scores["coherence"] -= 0.1
        reasons.append(f"Detected {hedge_count} hedging words (lower confidence)")
    
    # Normalize scores
    for key in dimension_scores:
        dimension_scores[key] = max(0.0, min(1.0, dimension_scores[key]))
    
    return {
        "score": max(0.0, min(1.0, score)),
        "reason": "; ".join(reasons) if reasons else "Response meets evaluation criteria (heuristic evaluation)",
        "dimension_scores": dimension_scores
    }
