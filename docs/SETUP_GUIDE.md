# Setup Guide

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn
- (Optional) PostgreSQL for production database

## Backend Setup

### 1. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
cd backend/app
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# LLM Provider (gemini, openai, anthropic)
LLM_PROVIDER=gemini

# Google Cloud / Gemini Configuration
GCP_PROJECT=your-project-id
GCP_LOCATION=us-central1
GEMINI_MODEL=gemini-1.5-flash
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# OpenAI Configuration (optional)
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4

# Anthropic Configuration (optional)
ANTHROPIC_API_KEY=your-anthropic-key
ANTHROPIC_MODEL=claude-3-opus-20240229

# Database (SQLite by default, or PostgreSQL)
DATABASE_URL=sqlite:///../../data/evaluations.db
# For PostgreSQL: DATABASE_URL=postgresql://user:password@localhost/dbname

# Feature Flags
USE_LLM_EVALUATION=true
USE_HEURISTIC_FALLBACK=true
USE_WEIGHTED_SCORING=false

# Dimension Weights (if using weighted scoring)
DIMENSION_WEIGHTS={"instruction_following": 0.2, "hallucination_prevention": 0.25, "assumption_prevention": 0.15, "coherence": 0.15, "accuracy": 0.25}
```

### 4. Initialize Database

The database will be automatically created on first run. For SQLite, the database file will be created at `data/evaluations.db`.

### 5. Start Backend Server

```bash
# From project root
uvicorn backend.app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend/react_app
npm install
```

### 2. Configure API URL (Optional)

Create a `.env` file in `frontend/react_app/`:

```env
REACT_APP_API_URL=http://localhost:8000
```

### 3. Start Development Server

```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## Google Cloud Setup (for Gemini)

1. Create a Google Cloud Project
2. Enable Vertex AI API
3. Create a service account and download credentials JSON
4. Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable
5. Set `GCP_PROJECT` to your project ID

See `GCP_SETUP_GUIDE.md` for detailed instructions.

## OpenAI Setup (Optional)

1. Get API key from https://platform.openai.com/
2. Set `OPENAI_API_KEY` in `.env`
3. Set `LLM_PROVIDER=openai` in `.env`

## Anthropic Setup (Optional)

1. Get API key from https://console.anthropic.com/
2. Set `ANTHROPIC_API_KEY` in `.env`
3. Set `LLM_PROVIDER=anthropic` in `.env`

## Running Tests

```bash
# From project root
cd backend/app
pytest tests/
```

## Using Batch Runner Script

```bash
# Submit a batch from JSON file
python scripts/batch_runner.py data/sample_inputs/example_batch.json

# Don't wait for completion
python scripts/batch_runner.py data/sample_inputs/example_batch.json --no-wait

# Custom API URL
python scripts/batch_runner.py data/sample_inputs/example_batch.json --api-base http://localhost:8000
```

## Production Deployment

### Backend

1. Use a production WSGI server:
   ```bash
   gunicorn backend.app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. Set up reverse proxy (nginx/Apache)

3. Use PostgreSQL for database:
   ```env
   DATABASE_URL=postgresql://user:password@localhost/dbname
   ```

4. Set up environment variables securely

### Frontend

1. Build production bundle:
   ```bash
   cd frontend/react_app
   npm run build
   ```

2. Serve with nginx or similar:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           root /path/to/react_app/build;
           try_files $uri /index.html;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
       }
   }
   ```

## Troubleshooting

### Database Connection Issues

- Ensure database file/directory is writable
- Check PostgreSQL connection string format
- Verify database exists (for PostgreSQL)

### LLM Provider Issues

- Check API keys are set correctly
- Verify credentials file path (for Gemini)
- Check API quotas/limits
- System will fall back to heuristics if LLM fails

### Frontend Can't Connect to Backend

- Check CORS settings in `backend/app/main.py`
- Verify API URL in frontend `.env`
- Check backend is running on correct port

## Next Steps

- Review `docs/api_docs.md` for API usage
- Check `docs/project_report.md` for architecture details
- Explore the frontend UI at `http://localhost:3000`

