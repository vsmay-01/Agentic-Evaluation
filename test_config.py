#!/usr/bin/env python
"""Quick test to verify GCP config is loaded from .env"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.config import settings

print("=" * 60)
print("AI Studio / Gemini Configuration Test")
print("=" * 60)
print(f"✓ AI_STUDIO_API_KEY (present): {bool(settings.ai_studio_api_key)}")
print(f"✓ AI_STUDIO_ENDPOINT: {settings.ai_studio_endpoint}")
print(f"✓ GEMINI_MODEL:     {settings.gemini_model}")
print(f"✓ USE_LLM_EVAL:     {settings.use_llm_evaluation}")
print(f"✓ USE_HEURISTIC:    {settings.use_heuristic_fallback}")
print("=" * 60)

# Quick check: is the API key set?
if settings.ai_studio_api_key and settings.ai_studio_api_key != "":
    print("✅ Config loaded successfully! (AI Studio API key present)")
    print("\nNext: Start the backend:")
    print("  cd backend")
    print("  python -m uvicorn app.main:app --reload")
else:
    print("❌ AI_STUDIO_API_KEY is empty. Did you update .env?")
    print("   Edit .env and set AI_STUDIO_API_KEY to your AI Studio API key or set ai_studio_endpoint+api_key in config")
