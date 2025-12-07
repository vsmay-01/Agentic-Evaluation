"""
Anthropic Claude LLM Provider for evaluation.
"""

from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


class AnthropicProvider:
    """Anthropic Claude provider for evaluation."""

    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        if not api_key:
            raise ValueError("Anthropic API key must be provided")
        self.api_key = api_key
        self.model = model

    def evaluate_response(self, prompt: str, response: str, reference: str = None) -> Dict[str, Any]:
        """Evaluate agent response using Anthropic Claude."""
        
        reference_text = f"\n\nReference/Expected Answer: {reference}" if reference else ""
        evaluation_prompt = f"""
You are an expert evaluator of agent responses. Evaluate this response on the following five dimensions and return ONLY valid JSON with numeric scores between 0.0 and 1.0:

1. instruction_following: Does the response follow the prompt exactly?
2. hallucination_prevention: Are facts accurate or made-up?
3. assumption_prevention: Are unnecessary assumptions avoided?
4. coherence: Is it logically structured?
5. accuracy: Does it answer correctly?{f" Compare with the reference answer if provided." if reference else ""}

Prompt: {prompt}

Agent Response: {response}{reference_text}

Return JSON with keys: instruction_following, hallucination_prevention, assumption_prevention, coherence, accuracy, reason
"""

        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            message = client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": evaluation_prompt
                    }
                ]
            )
            
            response_text = message.content[0].text
            
            # Clean up markdown wrappers
            if "```json" in response_text:
                response_text = response_text.split("```json", 1)[1].split("```", 1)[0].strip()
            elif response_text.strip().startswith("```"):
                parts = response_text.split("```")
                if len(parts) >= 2:
                    response_text = parts[1].strip()
            
            # Parse JSON
            result = json.loads(response_text)
            
            # Normalize and compute overall score
            dims = [
                float(result.get("instruction_following", 0.5)),
                float(result.get("hallucination_prevention", 0.5)),
                float(result.get("assumption_prevention", 0.5)),
                float(result.get("coherence", 0.5)),
                float(result.get("accuracy", 0.5)),
            ]
            overall = sum(dims) / len(dims)

            return {
                "score": max(0.0, min(1.0, overall)),
                "reason": result.get("reason", "Evaluated by Anthropic Claude"),
                "dimension_scores": {
                    "instruction_following": dims[0],
                    "hallucination_prevention": dims[1],
                    "assumption_prevention": dims[2],
                    "coherence": dims[3],
                    "accuracy": dims[4],
                },
            }

        except ImportError:
            logger.exception("anthropic package is not installed")
            return self._fallback_response("Anthropic client unavailable")
        except Exception as e:
            logger.exception("Anthropic evaluation failed")
            return self._fallback_response(f"Anthropic evaluation error: {str(e)}")

    def _fallback_response(self, reason: str) -> Dict[str, Any]:
        """Return fallback response when Anthropic fails."""
        return {
            "score": 0.5,
            "reason": reason,
            "dimension_scores": {
                "instruction_following": 0.5,
                "hallucination_prevention": 0.5,
                "assumption_prevention": 0.5,
                "coherence": 0.5,
                "accuracy": 0.5,
            },
        }

