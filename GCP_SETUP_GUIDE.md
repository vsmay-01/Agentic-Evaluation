# GCP Setup Guide for Gemini API

This guide walks you through obtaining GCP credentials to use Gemini (Google Vertex AI) with this evaluation system.

---

## 📋 Prerequisites

- A Google Account
- Access to [Google Cloud Console](https://console.cloud.google.com)
- A valid payment method (for free tier or paid usage)

---

## 🎯 Option 1: Using Service Account JSON (Recommended for Development)

### Step 1: Create a GCP Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click the **Project** dropdown at the top
3. Click **NEW PROJECT**
4. Enter a project name (e.g., `LLM-Evaluator`)
5. Click **CREATE**
6. Wait for the project to be created (30 seconds - 2 minutes)

### Step 2: Enable Required APIs

1. In the Cloud Console, search for **"Vertex AI API"** in the search bar
2. Click **Enable** button
3. Search for **"Generative Language API"** and enable it
4. Search for **"IAM API"** and enable it

### Step 3: Create a Service Account

1. In the left sidebar, go to **IAM & Admin** → **Service Accounts**
2. Click **CREATE SERVICE ACCOUNT** at the top
3. Fill in:
   - **Service account name**: `gemini-evaluator`
   - **Service account ID**: Auto-filled
   - **Description**: `Service account for LLM evaluation with Gemini`
4. Click **CREATE AND CONTINUE**
5. On the "Grant this service account access to project" screen:
   - Search and select the role: **Vertex AI User**
   - Click **ADD ANOTHER ROLE**
   - Add role: **Vertex AI Service Agent**
6. Click **CONTINUE** → **DONE**

### Step 4: Create and Download JSON Key

1. In the **Service Accounts** list, click on the **`gemini-evaluator`** account you just created
2. Go to the **KEYS** tab
3. Click **ADD KEY** → **Create new key**
4. Select **JSON**
5. Click **CREATE**
6. A JSON file will automatically download (usually named `[project-id]-[hash].json`)

**⚠️ Important:** Save this file securely. It contains credentials to access your GCP project.

### Step 5: Move JSON to Your Project

Move the downloaded JSON file to your project root (or any safe location):

```powershell
# Example: Copy the file to project root
Move-Item -Path "$env:USERPROFILE\Downloads\[project-id]-[hash].json" -Destination 'C:\Users\Mayank Verma\OneDrive\Desktop\LLM-Evaluator\Agentic-Evaluation\gcp-key.json'
```

### Step 6: Find Your Project ID

1. Open the downloaded JSON file with a text editor
2. Look for the field `"project_id"` (e.g., `"project_id": "my-project-12345"`)
3. Copy this value

---

## 🎯 Option 2: Using Application Default Credentials (ADC - Easier, Local Dev Only)

### Step 1: Install Google Cloud CLI

```powershell
# Download and install gcloud SDK
# Visit: https://cloud.google.com/sdk/docs/install-sdk#windows

# Or use Chocolatey (if installed)
choco install google-cloud-sdk
```

### Step 2: Authenticate with Your Google Account

```powershell
gcloud auth application-default login
```

This will:
1. Open your browser and ask you to sign in with your Google account
2. Ask for permission to access GCP resources
3. Create local credentials that the SDK uses automatically

### Step 3: Set Your Project ID

```powershell
gcloud config set project [YOUR-PROJECT-ID]
```

---

## ✅ Configuration: Add to `.env` File

Create or update `.env` in your project root:

### Option 1: Service Account JSON

```env
# Google Cloud Configuration
GCP_PROJECT=my-project-12345
GCP_LOCATION=us-central1
GEMINI_MODEL=gemini-1.5-flash

# Path to service account JSON
GOOGLE_APPLICATION_CREDENTIALS=C:\Users\Mayank Verma\OneDrive\Desktop\LLM-Evaluator\Agentic-Evaluation\gcp-key.json

# Feature flags
USE_LLM_EVALUATION=true
USE_HEURISTIC_FALLBACK=true
```

### Option 2: Application Default Credentials (ADC)

```env
# Google Cloud Configuration
GCP_PROJECT=my-project-12345
GCP_LOCATION=us-central1
GEMINI_MODEL=gemini-1.5-flash

# Leave GOOGLE_APPLICATION_CREDENTIALS empty to use ADC
# GOOGLE_APPLICATION_CREDENTIALS=

# Feature flags
USE_LLM_EVALUATION=true
USE_HEURISTIC_FALLBACK=true
```

---

## 🧪 Verify Credentials Are Working

### Test 1: Import the SDK

```powershell
cd 'C:\Users\Mayank Verma\OneDrive\Desktop\LLM-Evaluator\Agentic-Evaluation\backend'
python -c "from google.cloud import aiplatform; print('✓ google-cloud-aiplatform installed')"
```

### Test 2: Verify Credentials Are Readable

```powershell
python -c "
import os
from google.cloud import aiplatform

# Check if credentials are available
creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
project_id = os.getenv('GCP_PROJECT')

if creds_path:
    print(f'✓ Credentials file: {creds_path}')
    print(f'✓ File exists: {os.path.exists(creds_path)}')
else:
    print('✓ Using Application Default Credentials (ADC)')

print(f'✓ Project ID: {project_id}')
"
```

### Test 3: Start Backend and Check Health

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

In another terminal:

```powershell
curl http://localhost:8000/health/ready
# Should return: {"status": "ok"}
```

---

## 🚨 Troubleshooting

### Error: `google-cloud-aiplatform is not installed`

**Fix:** Install the package

```powershell
pip install google-cloud-aiplatform
```

### Error: `GOOGLE_APPLICATION_CREDENTIALS not set or file not found`

**Fix:** 
1. Check the file path in `.env` is correct
2. Ensure the JSON file exists at that path
3. Use absolute path, not relative

```powershell
# Verify file exists
Test-Path 'C:\Users\Mayank Verma\OneDrive\Desktop\LLM-Evaluator\Agentic-Evaluation\gcp-key.json'
```

### Error: `Permission denied - insufficient scopes`

**Fix:**
1. Go back to GCP Console
2. Select the service account
3. Ensure it has role **"Vertex AI User"** or **"Editor"**
4. Sometimes changes take 1-2 minutes to apply

### Error: `Project not found`

**Fix:**
1. Double-check `GCP_PROJECT` in `.env` is spelled correctly
2. Ensure the project was created and you're still a member

---

## 📊 Cost Estimation

| Model | Cost per 1M input tokens | Cost per 1M output tokens |
|-------|-------------------------|--------------------------|
| **gemini-1.5-flash** | $0.075 | $0.30 |
| **gemini-1.5-pro** | $3.50 | $10.50 |
| **gemini-2.0-flash** (preview) | $0.075 | $0.30 |

### Example Costs for 1000 Evaluations:
- **gemini-1.5-flash**: ~$0.10 - $1.00 (very cheap)
- **gemini-1.5-pro**: ~$5 - $15 (higher quality, more expensive)

---

## ✨ Next Steps

1. ✅ Get credentials (this guide)
2. ⏳ Add credentials to `.env`
3. ⏳ Run backend: `python -m uvicorn app.main:app --reload`
4. ⏳ Test evaluation endpoint

---

## 🔗 Useful Links

- [Google Cloud Console](https://console.cloud.google.com)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Gemini API Pricing](https://ai.google.dev/pricing)
- [Google Cloud SDK Setup](https://cloud.google.com/sdk/docs/install-sdk)

---

**Questions?** Check the errors section or refer to the official Google Cloud documentation.
