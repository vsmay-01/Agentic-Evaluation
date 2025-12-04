#!/usr/bin/env python
"""Quick test to verify GCP config is loaded from .env"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.config import settings

print("=" * 60)
print("GCP Configuration Test")
print("=" * 60)
print(f"✓ GCP_PROJECT:      {settings.gcp_project}")
print(f"✓ GCP_LOCATION:     {settings.gcp_location}")
print(f"✓ GEMINI_MODEL:     {settings.gemini_model}")
print(f"✓ USE_LLM_EVAL:     {settings.use_llm_evaluation}")
print(f"✓ USE_HEURISTIC:    {settings.use_heuristic_fallback}")
print("=" * 60)

# Quick check: is the project ID set?
if settings.gcp_project and settings.gcp_project != "":
    print("✅ Config loaded successfully!")
    print("\nNext: Verify credentials by starting backend:")
    print("  cd backend")
    print("  python -m uvicorn app.main:app --reload")
else:
    print("❌ GCP_PROJECT is empty. Did you update .env?")
    print("   Edit .env and set GCP_PROJECT to your actual GCP project ID")
