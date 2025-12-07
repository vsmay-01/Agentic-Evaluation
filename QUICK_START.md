# Quick Start Guide

## Prerequisites
- Python 3.8+ installed
- Node.js 16+ and npm installed

## Step 1: Backend Setup

### Windows (PowerShell)
```powershell
# Navigate to project root
cd C:\Users\Mayank Verma\OneDrive\Desktop\code\Agentic-Evaluation

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
cd backend\app
pip install -r requirements.txt

# Go back to project root
cd ..\..

# Start backend server
uvicorn backend.app.main:app --reload --port 8000
```

### Linux/Mac
```bash
# Navigate to project root
cd /path/to/Agentic-Evaluation

# Create virtual environment (if not exists)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
cd backend/app
pip install -r requirements.txt

# Go back to project root
cd ../..

# Start backend server
uvicorn backend.app.main:app --reload --port 8000
```

**Backend will run on:** http://localhost:8000

## Step 2: Frontend Setup

### Open a NEW terminal window

### Windows (PowerShell)
```powershell
# Navigate to project root
cd C:\Users\Mayank Verma\OneDrive\Desktop\code\Agentic-Evaluation

# Navigate to frontend
cd frontend\react_app

# Install dependencies (first time only)
npm install

# Start frontend
npm start
```

### Linux/Mac
```bash
# Navigate to project root
cd /path/to/Agentic-Evaluation

# Navigate to frontend
cd frontend/react_app

# Install dependencies (first time only)
npm install

# Start frontend
npm start
```

**Frontend will run on:** http://localhost:3000

## Step 3: Access the Application

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health/ready

## Quick Test

### Test Backend (in a new terminal)
```bash
curl http://localhost:8000/health/ready
```

### Test Frontend
Open browser and go to: http://localhost:8000

## Environment Variables (Optional)

Create a `.env` file in the project root for LLM configuration:

```env
# LLM Provider (gemini, openai, anthropic)
LLM_PROVIDER=gemini

# For Gemini
GCP_PROJECT=your-project-id
GCP_LOCATION=us-central1
GEMINI_MODEL=gemini-1.5-flash

# For OpenAI (optional)
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4

# For Anthropic (optional)
ANTHROPIC_API_KEY=your-key
ANTHROPIC_MODEL=claude-3-opus-20240229
```

## Troubleshooting

### Backend won't start
- Check if port 8000 is already in use
- Verify Python virtual environment is activated
- Check if all dependencies are installed: `pip install -r backend/app/requirements.txt`

### Frontend won't start
- Check if port 3000 is already in use
- Verify Node.js is installed: `node --version`
- Reinstall dependencies: `cd frontend/react_app && npm install`

### Database issues
- SQLite database will be created automatically at `data/evaluations.db`
- Ensure `data/` directory exists and is writable

## Stopping the Servers

- **Backend**: Press `Ctrl+C` in the backend terminal
- **Frontend**: Press `Ctrl+C` in the frontend terminal

