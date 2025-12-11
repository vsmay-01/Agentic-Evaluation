from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import os
from pathlib import Path

# Explicitly load .env file using python-dotenv
try:
    from dotenv import load_dotenv
    
    # Find and load .env from project root
    root = Path(__file__).parent
    for _ in range(4):
        env_path = root / '.env'
        if env_path.exists():
            load_dotenv(env_path)
            break
        root = root.parent
except ImportError:
    pass


class Settings(BaseSettings):
    """Application settings.

    This file is migrated to use Google Vertex AI (Gemini) as the
    single LLM provider. Load sensitive values from environment
    variables or a `.env` file in development.
    """

    # Configure pydantic to read from environment variables
    model_config = ConfigDict(extra='ignore')

    app_name: str = "llm-evaluation"

    # Database
    database_url: str = "sqlite:///../../data/evaluations.db"

    # LLM Configuration (Gemini via AI Studio / Vertex REST)
    llm_provider: str = "gemini"
    # Full AI Studio / Vertex REST endpoint (optional). If not provided, a default constructed URL
    # will be used when a project/location are available. Example:
    # https://us-central1-aiplatform.googleapis.com/v1/projects/<project>/locations/us-central1/models/<model>:predict
    ai_studio_endpoint: str = ""
    # API key for AI Studio / Vertex REST (preferred for API-key based access)
    ai_studio_api_key: str = ""
    # Gemini model id (model name or resource id)
    gemini_model: str = "gemini-1.5-flash"

    # Batch processing
    max_batch_size: int = 100
    batch_timeout_seconds: int = 300

    # Feature flags
    use_llm_evaluation: bool = True
    use_heuristic_fallback: bool = True
    
    # Weighted scoring configuration
    use_weighted_scoring: bool = False
    dimension_weights: dict = {
        "instruction_following": 0.2,
        "hallucination_prevention": 0.25,
        "assumption_prevention": 0.15,
        "coherence": 0.15,
        "accuracy": 0.25,
    }
    
    # OpenAI Configuration (optional)
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    
    # Anthropic Configuration (optional)
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-opus-20240229"


settings = Settings()
