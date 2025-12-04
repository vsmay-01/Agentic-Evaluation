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

    # LLM Configuration (Gemini / Vertex AI)
    llm_provider: str = "gemini"
    gcp_project: str = ""
    gcp_location: str = "us-central1"
    gemini_model: str = "gemini-1.5-flash"
    google_application_credentials: str = ""

    # Batch processing
    max_batch_size: int = 100
    batch_timeout_seconds: int = 300

    # Feature flags
    use_llm_evaluation: bool = True
    use_heuristic_fallback: bool = True


settings = Settings()
