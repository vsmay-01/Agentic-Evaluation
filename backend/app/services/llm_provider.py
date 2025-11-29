"""
LLM Provider abstraction for multi-LLM support.
Supports OpenAI GPT-4, Claude, and heuristic fallback.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import os


class LLMProvider(ABC):
    """Abstract base for LLM providers."""
    
    @abstractmethod
    def evaluate_response(self, prompt: str, response: str) -> Dict[str, Any]:
        """
        Evaluate agent response using LLM.
        
        Returns:
            dict with 'score' (0-1) and 'reason' string
        """
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT-4 evaluation."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        self.api_key = api_key
        self.model = model
        
    def evaluate_response(self, prompt: str, response: str) -> Dict[str, Any]:
        """Use GPT-4 to evaluate response on multiple dimensions."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            evaluation_prompt = f"""
You are an expert evaluator of agent responses. Evaluate this response on:
1. Instruction Following (0-1): Does it follow the prompt exactly?
2. Hallucination Prevention (0-1): Are facts accurate or made-up?
3. Assumption Prevention (0-1): Are unnecessary assumptions avoided?
4. Response Coherence (0-1): Is it logically structured?
5. Response Accuracy (0-1): Does it answer correctly?

Prompt: {prompt}

Response: {response}

Respond in JSON format:
{{"instruction_following": 0.X, "hallucination_prevention": 0.X, "assumption_prevention": 0.X, "coherence": 0.X, "accuracy": 0.X, "reason": "brief explanation"}}
"""
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": evaluation_prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            import json
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            # Calculate average score
            scores = [
                result.get("instruction_following", 0.5),
                result.get("hallucination_prevention", 0.5),
                result.get("assumption_prevention", 0.5),
                result.get("coherence", 0.5),
                result.get("accuracy", 0.5)
            ]
            avg_score = sum(scores) / len(scores)
            
            return {
                "score": avg_score,
                "reason": result.get("reason", "Evaluated by GPT-4"),
                "dimension_scores": {
                    "instruction_following": result.get("instruction_following", 0.5),
                    "hallucination_prevention": result.get("hallucination_prevention", 0.5),
                    "assumption_prevention": result.get("assumption_prevention", 0.5),
                    "coherence": result.get("coherence", 0.5),
                    "accuracy": result.get("accuracy", 0.5)
                }
            }
        except Exception as e:
            raise RuntimeError(f"OpenAI evaluation failed: {str(e)}")


class ClaudeProvider(LLMProvider):
    """Anthropic Claude evaluation."""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        self.api_key = api_key
        self.model = model
        
    def evaluate_response(self, prompt: str, response: str) -> Dict[str, Any]:
        """Use Claude to evaluate response on multiple dimensions."""
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.api_key)
            
            evaluation_prompt = f"""
You are an expert evaluator of agent responses. Evaluate this response on:
1. Instruction Following (0-1): Does it follow the prompt exactly?
2. Hallucination Prevention (0-1): Are facts accurate or made-up?
3. Assumption Prevention (0-1): Are unnecessary assumptions avoided?
4. Response Coherence (0-1): Is it logically structured?
5. Response Accuracy (0-1): Does it answer correctly?

Prompt: {prompt}

Response: {response}

Respond in JSON format:
{{"instruction_following": 0.X, "hallucination_prevention": 0.X, "assumption_prevention": 0.X, "coherence": 0.X, "accuracy": 0.X, "reason": "brief explanation"}}
"""
            
            result = client.messages.create(
                model=self.model,
                max_tokens=200,
                messages=[{"role": "user", "content": evaluation_prompt}]
            )
            
            import json
            result_text = result.content[0].text
            parsed = json.loads(result_text)
            
            # Calculate average score
            scores = [
                parsed.get("instruction_following", 0.5),
                parsed.get("hallucination_prevention", 0.5),
                parsed.get("assumption_prevention", 0.5),
                parsed.get("coherence", 0.5),
                parsed.get("accuracy", 0.5)
            ]
            avg_score = sum(scores) / len(scores)
            
            return {
                "score": avg_score,
                "reason": parsed.get("reason", "Evaluated by Claude"),
                "dimension_scores": {
                    "instruction_following": parsed.get("instruction_following", 0.5),
                    "hallucination_prevention": parsed.get("hallucination_prevention", 0.5),
                    "assumption_prevention": parsed.get("assumption_prevention", 0.5),
                    "coherence": parsed.get("coherence", 0.5),
                    "accuracy": parsed.get("accuracy", 0.5)
                }
            }
        except Exception as e:
            raise RuntimeError(f"Claude evaluation failed: {str(e)}")


def get_llm_provider(provider_name: str, **kwargs) -> LLMProvider:
    """Factory function to get the appropriate LLM provider."""
    if provider_name == "openai":
        return OpenAIProvider(
            api_key=kwargs.get("openai_api_key"),
            model=kwargs.get("openai_model", "gpt-4o-mini")
        )
    elif provider_name == "claude":
        return ClaudeProvider(
            api_key=kwargs.get("claude_api_key"),
            model=kwargs.get("claude_model", "claude-3-5-sonnet-20241022")
        )
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
