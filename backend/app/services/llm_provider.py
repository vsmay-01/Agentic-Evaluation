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
    def evaluate_response(self, prompt: str, response: str, reference: str = None) -> Dict[str, Any]:
        """Evaluate agent response using LLM.

        Args:
            prompt: The prompt/instruction given to the agent
            response: The actual response from the agent
            reference: Optional reference/expected answer for accuracy comparison

        Returns a dict with keys: `score` (0-1), `reason` (str),
        and `dimension_scores` (dict).
        """


class GeminiProvider(LLMProvider):
    """Google Vertex AI (Gemini) provider.

    This implementation uses `google.cloud.aiplatform` when available.
    It attempts to initialize the Vertex AI client only on demand so
    the module can be imported even if the dependency is not installed.
    """

    def __init__(self, project_id: str = None, location: str = "us-central1", model: str = "gemini-1.5-flash", credentials_path: str = None, api_key: str = None, endpoint: str = None):
        # For API-key based AI Studio use `api_key` and optionally a full `endpoint`.
        # `project_id` and `location` are optional and only used to construct a default
        # endpoint if `endpoint` is not provided.
        self.project_id = project_id
        self.location = location
        self.model = model
        self.api_key = api_key
        self.endpoint = endpoint

    def evaluate_response(self, prompt: str, response: str, reference: str = None) -> Dict[str, Any]:
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

        # Build the REST endpoint to call. Prefer explicit endpoint; otherwise construct if project_id provided.
        rest_endpoint = None
        if self.endpoint and isinstance(self.endpoint, str) and self.endpoint.strip() != "":
            rest_endpoint = self.endpoint
        elif self.project_id:
            rest_endpoint = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/models/{self.model}:predict"

        # If an API key is provided and we have a REST endpoint, call AI Studio / Vertex REST predict endpoint
        if self.api_key and rest_endpoint:
            try:
                import requests

                params = {"key": self.api_key}
                payload = {"instances": [{"content": evaluation_prompt}]}
                headers = {"Content-Type": "application/json"}

                resp = requests.post(rest_endpoint, params=params, json=payload, headers=headers, timeout=60)
                resp.raise_for_status()
                j = resp.json()

                # Try to extract text from common response shapes
                response_text = None
                if isinstance(j, dict):
                    if "predictions" in j and isinstance(j["predictions"], list) and j["predictions"]:
                        first = j["predictions"][0]
                        if isinstance(first, dict):
                            for key in ("content", "text", "output", "generated_text", "completion"):
                                if key in first:
                                    response_text = first[key]
                                    break
                        elif isinstance(first, str):
                            response_text = first

                    if response_text is None:
                        for candidate_key in ("candidates", "outputs", "response", "data"):
                            if candidate_key in j:
                                val = j[candidate_key]
                                if isinstance(val, list) and val:
                                    item = val[0]
                                    if isinstance(item, dict) and "content" in item:
                                        response_text = item["content"]
                                        break
                                    elif isinstance(item, str):
                                        response_text = item
                                        break

                if response_text is None:
                    response_text = json.dumps(j)

            except Exception as e:
                logger.exception("REST-based Gemini/Vertex call failed")
                raise Exception(f"Gemini evaluation (REST) failed: {str(e)}")

            # Clean up common markdown wrappers
            if response_text is None:
                raise ValueError("Empty response from Gemini model")

            if "```json" in response_text:
                response_text = response_text.split("```json", 1)[1].split("```", 1)[0].strip()
            elif response_text.strip().startswith("```"):
                parts = response_text.split("```")
                if len(parts) >= 2:
                    response_text = parts[1].strip()

            # Attempt to parse JSON
            try:
                result = json.loads(response_text)
            except Exception:
                import re

                m = re.search(r"\{[\s\S]*\}", response_text)
                if m:
                    result = json.loads(m.group(0))
                else:
                    raise

            # Normalize and compute overall score (same as SDK path)
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
                "reason": result.get("reason", "Evaluated by Gemini (REST)"),
                "dimension_scores": {
                    "instruction_following": dims[0],
                    "hallucination_prevention": dims[1],
                    "assumption_prevention": dims[2],
                    "coherence": dims[3],
                    "accuracy": dims[4],
                },
            }

        # SDK-based path removed. This provider is now REST-first and expects an AI Studio
        # API key + endpoint (or a project_id that can be used to construct a default endpoint).
        # If you need SDK behavior, re-install `google-cloud-aiplatform` and re-add SDK support.
        raise Exception(
            "GeminiProvider: only AI Studio / Vertex REST (API key + endpoint) is supported in this deployment. "
            "Provide `api_key` and `endpoint` when creating the provider (or set `ai_studio_api_key` and `ai_studio_endpoint` in config)."
        )


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
            project_id=kwargs.get("project_id"),
            location=kwargs.get("location"),
            model=kwargs.get("model") or kwargs.get("gemini_model"),
            credentials_path=kwargs.get("credentials_path"),
            api_key=kwargs.get("api_key") or kwargs.get("ai_studio_api_key"),
            endpoint=kwargs.get("endpoint") or kwargs.get("ai_studio_endpoint"),
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