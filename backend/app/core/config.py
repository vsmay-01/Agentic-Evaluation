from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    app_name: str = "llm-evaluation"
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///../../data/evaluations.db")
    
    # LLM Configuration
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")  # "openai", "claude", or "heuristic"
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    claude_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    claude_model: str = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
    
    # Batch processing
    max_batch_size: int = 100
    batch_timeout_seconds: int = 300
    
    # Feature flags
    use_llm_evaluation: bool = os.getenv("USE_LLM_EVALUATION", "true").lower() == "true"
    use_heuristic_fallback: bool = os.getenv("USE_HEURISTIC_FALLBACK", "true").lower() == "true"

settings = Settings()
