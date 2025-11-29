"""
Rule-based evaluation checks for agent responses.
Evaluates: instruction following, response coherence, basic accuracy.
"""

def apply_rule_checks(prompt: str, response: str) -> dict:
    """
    Apply rule-based checks on agent response.
    
    Rules:
    - Check response length (not empty, not too short)
    - Check for basic coherence (sentence structure)
    - Check for missing key terms from prompt
    
    Returns:
        dict with 'score' (0-1) and 'issues' list
    """
    issues = []
    score = 1.0
    
    # Rule 1: Response must not be empty
    if not response or len(response.strip()) == 0:
        issues.append("Response is empty")
        score -= 0.3
    
    # Rule 2: Response must be substantial (at least 10 chars)
    if len(response.strip()) < 10:
        issues.append("Response too short (< 10 chars)")
        score -= 0.2
    
    # Rule 3: Basic coherence check (looks for sentence endings)
    if response.count('.') == 0 and response.count('?') == 0 and response.count('!') == 0:
        issues.append("Response lacks sentence structure")
        score -= 0.15
    
    # Rule 4: Check if response addresses key terms from prompt
    prompt_words = set(prompt.lower().split())
    response_words = set(response.lower().split())
    overlap = len(prompt_words & response_words) / max(len(prompt_words), 1)
    if overlap < 0.1:
        issues.append(f"Low keyword overlap with prompt ({overlap:.1%})")
        score -= 0.1
    
    return {
        "score": max(0.0, min(1.0, score)),
        "issues": issues
    }
