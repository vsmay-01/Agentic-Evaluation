"""
LLM Provider abstraction (Gemini-only / Vertex AI)

This module provides a compact provider that uses Google Vertex AI
generative models (Gemini) to produce evaluation scores. It returns
a dictionary with an overall `score`, `reason`, and `dimension_scores`.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import json
import logging


logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base for LLM providers."""

    @abstractmethod
    def evaluate_response(self, prompt: str, response: str) -> Dict[str, Any]:
        """Evaluate agent response using LLM.

        Returns a dict with keys: `score` (0-1), `reason` (str),
        and `dimension_scores` (dict).
        """


class GeminiProvider(LLMProvider):
    """Google Vertex AI (Gemini) provider.

    This implementation uses `google.cloud.aiplatform` when available.
    It attempts to initialize the Vertex AI client only on demand so
    the module can be imported even if the dependency is not installed.
    """

    def __init__(self, project_id: str, location: str = "us-central1", model: str = "gemini-1.5-flash"):
        if not project_id:
            raise ValueError("GCP project id must be provided")
        self.project_id = project_id
        self.location = location
        self.model = model

    def evaluate_response(self, prompt: str, response: str) -> Dict[str, Any]:
        evaluation_prompt = f"""
You are an expert evaluator of agent responses. Evaluate this response on the following five dimensions and return ONLY valid JSON with numeric scores between 0.0 and 1.0:

1. instruction_following: Does the response follow the prompt exactly?
2. hallucination_prevention: Are facts accurate or made-up?
3. assumption_prevention: Are unnecessary assumptions avoided?
4. coherence: Is it logically structured?
5. accuracy: Does it answer correctly?

Prompt: {prompt}

Response: {response}

Return JSON with keys: instruction_following, hallucination_prevention, assumption_prevention, coherence, accuracy, reason
"""

        # Lazy import to avoid hard dependency at import time
        try:
            from google.cloud import aiplatform
        except Exception as e:  # pragma: no cover - external dependency
            logger.exception("google-cloud-aiplatform is not installed or failed to import")
            return {
                "score": 0.5,
                "reason": f"Vertex AI client unavailable: {str(e)}",
                "dimension_scores": {
                    "instruction_following": 0.5,
                    "hallucination_prevention": 0.5,
                    "assumption_prevention": 0.5,
                    "coherence": 0.5,
                    "accuracy": 0.5,
                },
            }

        try:
            # Initialize Vertex AI (no-op if already configured)
            aiplatform.init(project=self.project_id, location=self.location)

            # High-level interface: GenerativeModel / TextGenerationModel depending on SDK
            # Try recommended high-level API if available
            model_obj = None
            if hasattr(aiplatform, "GenerativeModel"):
                model_obj = aiplatform.GenerativeModel(self.model)
                response_obj = model_obj.generate(evaluation_prompt) if hasattr(model_obj, "generate") else model_obj.generate_content(evaluation_prompt)
            elif hasattr(aiplatform, "TextGenerationModel"):
                model_obj = aiplatform.TextGenerationModel.from_pretrained(self.model)
                response_obj = model_obj.generate(evaluation_prompt)
            else:
                # Fallback to the generic Model class (older SDKs)
                model_obj = aiplatform.Model(self.model)
                # Use `predict` or `batch_predict` if available; attempt a gentle call
                if hasattr(model_obj, "predict"):
                    response_obj = model_obj.predict(evaluation_prompt)
                else:
                    # As last resort, attempt to call the gapic PredictionServiceClient
                    from google.cloud.aiplatform.gapic import PredictionServiceClient
                    client = PredictionServiceClient()
                    endpoint = model_obj.resource_name if hasattr(model_obj, "resource_name") else f"projects/{self.project_id}/locations/{self.location}/models/{self.model}"
                    response_obj = client.predict(endpoint=endpoint, instances=[{"content": evaluation_prompt}])

            # Extract text from response object in a robust way
            response_text = None
            if isinstance(response_obj, dict) and "text" in response_obj:
                response_text = response_obj["text"]
            elif hasattr(response_obj, "text"):
                response_text = getattr(response_obj, "text")
            elif hasattr(response_obj, "generations"):
                # Some SDKs return generations -> list -> text
                gens = getattr(response_obj, "generations")
                if gens and isinstance(gens, list) and hasattr(gens[0], "text"):
                    response_text = gens[0].text
                elif isinstance(gens, list) and isinstance(gens[0], dict) and "text" in gens[0]:
                    response_text = gens[0]["text"]
            else:
                response_text = str(response_obj)

            # Clean up common markdown wrappers
            if response_text is None:
                raise ValueError("Empty response from Gemini model")

            if "```json" in response_text:
                response_text = response_text.split("```json", 1)[1].split("```", 1)[0].strip()
            elif response_text.strip().startswith("```"):
                # remove triple-backticks
                parts = response_text.split("```")
                if len(parts) >= 2:
                    response_text = parts[1].strip()

            # Attempt to parse JSON
            try:
                result = json.loads(response_text)
            except Exception:
                # If response is not strict JSON, attempt to extract JSON substring
                import re

                m = re.search(r"\{[\s\S]*\}", response_text)
                if m:
                    result = json.loads(m.group(0))
                else:
                    raise

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
                "reason": result.get("reason", "Evaluated by Gemini"),
                "dimension_scores": {
                    "instruction_following": dims[0],
                    "hallucination_prevention": dims[1],
                    "assumption_prevention": dims[2],
                    "coherence": dims[3],
                    "accuracy": dims[4],
                },
            }

        except Exception as e:
            logger.exception("Gemini evaluation failed")
            return {
                "score": 0.5,
                "reason": f"Gemini evaluation error: {str(e)}",
                "dimension_scores": {
                    "instruction_following": 0.5,
                    "hallucination_prevention": 0.5,
                    "assumption_prevention": 0.5,
                    "coherence": 0.5,
                    "accuracy": 0.5,
                },
            }


def get_llm_provider(provider_name: str = "gemini", **kwargs) -> LLMProvider:
    """Factory function to get LLM provider instance.

    Supported providers: gemini, openai, anthropic
    
    Extra kwargs depend on provider:
    - gemini: project_id, location, model
    - openai: api_key, model
    - anthropic: api_key, model
    """
    if provider_name == "gemini":
        return GeminiProvider(
            project_id=kwargs.get("project_id") or kwargs.get("gcp_project"),
            location=kwargs.get("location") or kwargs.get("gcp_location"),
            model=kwargs.get("model") or kwargs.get("gemini_model"),
        )
    elif provider_name == "openai":
        from .llm_provider_openai import OpenAIProvider
        return OpenAIProvider(
            api_key=kwargs.get("api_key") or kwargs.get("openai_api_key"),
            model=kwargs.get("model") or kwargs.get("openai_model", "gpt-4"),
        )
    elif provider_name == "anthropic":
        from .llm_provider_anthropic import AnthropicProvider
        return AnthropicProvider(
            api_key=kwargs.get("api_key") or kwargs.get("anthropic_api_key"),
            model=kwargs.get("model") or kwargs.get("anthropic_model", "claude-3-opus-20240229"),
        )
    else:
        raise ValueError(f"Unsupported provider: {provider_name}. Supported: gemini, openai, anthropic")