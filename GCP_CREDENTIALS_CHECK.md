# Google Cloud Credentials Setup Check

## ✅ What I Found

1. **Credentials File**: ✅ Valid
   - File: `gcp-key.json` exists
   - Project ID: `llm-evaluator-480205`
   - Service Account: `agentic-eval@llm-evaluator-480205.iam.gserviceaccount.com`
   - File structure: Valid JSON with all required fields

2. **Code Issue**: ❌ Fixed
   - **Problem**: The code was not setting `GOOGLE_APPLICATION_CREDENTIALS` environment variable
   - **Fix Applied**: Updated `GeminiProvider` to accept and set credentials path

3. **Configuration**: ⚠️ Needs `.env` file
   - No `.env` file found in project root
   - Need to create one with proper settings

## 🔧 What Was Fixed

### 1. Updated `GeminiProvider` (backend/app/services/llm_provider.py)
- Added `credentials_path` parameter to `__init__`
- Now sets `GOOGLE_APPLICATION_CREDENTIALS` environment variable when credentials path is provided

### 2. Updated `llm_judge.py`
- Now passes `credentials_path` from config to provider

### 3. Updated `get_llm_provider` factory
- Now passes credentials path to GeminiProvider

## 📝 Next Steps - Create `.env` File

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

## 🧪 Test Credentials

After creating `.env`, test with:

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Test
python -c "import os; from pathlib import Path; from google.cloud import aiplatform; os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(Path('gcp-key.json').resolve()); aiplatform.init(project='llm-evaluator-480205', location='us-central1'); print('✓ Success!')"
```

## ✅ Summary

- **Credentials File**: ✅ Valid and in correct location
- **Code**: ✅ Fixed to use credentials properly
- **Configuration**: ⚠️ Need to create `.env` file (see above)

Once you create the `.env` file and restart the backend, Gemini should work correctly!


