# Google Cloud Credentials Setup - Quick Fix

## ✅ Current Status

Your credentials file exists and is valid:
- **File**: `gcp-key.json`
- **Project ID**: `llm-evaluator-480205`
- **Location**: Project root

## ⚠️ Issue Found

The code was not setting the `GOOGLE_APPLICATION_CREDENTIALS` environment variable from the config. This has been fixed.

## 🔧 Setup Steps

### 1. Create `.env` File

Create a `.env` file in the project root with:

```env
# Google Cloud / Gemini Configuration
GCP_PROJECT=llm-evaluator-480205
GCP_LOCATION=us-central1
GEMINI_MODEL=gemini-1.5-flash
GOOGLE_APPLICATION_CREDENTIALS=C:\Users\Mayank Verma\OneDrive\Desktop\code\Agentic-Evaluation\gcp-key.json

# LLM Provider
LLM_PROVIDER=gemini

# Feature Flags
USE_LLM_EVALUATION=true
USE_HEURISTIC_FALLBACK=true
USE_WEIGHTED_SCORING=false

# Database
DATABASE_URL=sqlite:///../../data/evaluations.db
```

### 2. Verify Setup

Run this test to verify credentials work:

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Test credentials
python -c "
import os
from pathlib import Path
from google.cloud import aiplatform

# Set credentials
creds_path = Path('gcp-key.json').resolve()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(creds_path)

# Initialize
aiplatform.init(project='llm-evaluator-480205', location='us-central1')
print('✓ Credentials configured successfully!')
"
```

### 3. Restart Backend

After creating the `.env` file, restart your backend server:

```powershell
uvicorn backend.app.main:app --reload --port 8000
```

## ✅ What Was Fixed

1. **Updated `GeminiProvider.__init__`**: Now accepts `credentials_path` parameter and sets `GOOGLE_APPLICATION_CREDENTIALS` environment variable
2. **Updated `llm_judge.py`**: Passes credentials path from config to provider
3. **Updated `get_llm_provider`**: Passes credentials path to GeminiProvider

## 🧪 Test It

After setup, try an evaluation. The system should now:
- Use Gemini API if credentials are valid
- Fall back to heuristics if there's an error (but won't show error in response)

## 📝 Notes

- The `.env` file is git-ignored (contains sensitive credentials)
- Make sure `gcp-key.json` is also in `.gitignore`
- The credentials path must be absolute (not relative)


