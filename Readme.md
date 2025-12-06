# Agentic Evaluation System

## Problem Statement (Problem 4: Agentic Evaluation)

When an agent is provided with a prompt and task and we get 100s of responses, how do we know the agent truly followed the prompt in the dimensions of:
- **Instruction Following**: Does the response adhere to the exact instructions?
- **Hallucination Prevention**: Are the facts accurate or made up?
- **Assumption Prevention**: Does it avoid unnecessary assumptions?
- **Response Coherence**: Is the response logically structured?
- **Response Accuracy**: Does it correctly answer the query?

This project builds a framework for evaluating agent inputs and responses in batch mode with a comprehensive scoring system.

## Workflow

### 1. **Agent Response Input**
- Submit 100s of agent prompts and responses through the React frontend or API
- Each request contains: `id`, `model_name`, and list of `inputs` (prompt + reference/expected response)

### 2. **Multi-Dimensional Evaluation**
The backend performs evaluation on 5 key dimensions:

| Dimension | Method | Checks |
|-----------|--------|--------|
| **Instruction Following** | Rule-based | Response length, coherence, keyword overlap |
| **Hallucination Prevention** | LLM heuristics | Speculative phrases ("maybe", "probably") |
| **Assumption Prevention** | LLM heuristics | Risky language patterns ("assuming", "if") |
| **Response Coherence** | Rule-based | Sentence structure, logical flow |
| **Response Accuracy** | Rule-based + LLM | Detail level, consistency with prompt |

### 3. **Scoring & Aggregation**
- Each dimension produces a score (0-1)
- Scores are aggregated using weighted average
- Final score ranges 0-1 (higher = better response)

### 4. **Results Storage & Analysis**
- Results saved to `data/evaluations.json`
- Dimension scores tracked for per-dimension analysis
- Batch processing supports 1000s of responses

## Architecture

```
backend/
├── app/
│   ├── main.py                 # FastAPI app
│   ├── api/
│   │   ├── evaluate.py         # POST /evaluate/ endpoint
│   │   └── health.py           # Health check endpoints
│   ├── services/
│   │   ├── llm_judge.py        # Hallucination & accuracy evaluation
│   │   ├── rule_based.py       # Instruction following & coherence
│   │   └── score_aggregator.py # Score combination
│   ├── storage/
│   │   └── save_results.py     # Persist results to JSON
│   └── models/
│       ├── request_model.py    # API request schema
│       └── response_model.py   # API response schema

frontend/
└── react_app/
    ├── src/
    │   ├── App.js              # Evaluation form component
    │   └── utils/api.js        # API client
    └── package.json            # React dependencies + proxy

data/
├── evaluations.json            # Results storage
└── sample_inputs/
    └── example_batch.json      # Sample batch input

scripts/
├── populate_sample_data.py     # Generate sample data
├── batch_runner.py             # Batch processing script
└── export_scores.py            # Export results
```

## Quick Start

### 1. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend/app
pip install -r requirements.txt

# Configure environment (create .env file in project root)
# See docs/SETUP_GUIDE.md for details

# Start backend
uvicorn backend.app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
# Install dependencies
cd frontend/react_app
npm install

# Start frontend
npm start
```

### 3. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs (Swagger UI)

For detailed setup instructions, see [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)

## Usage Examples

### Single Evaluation (API)

```bash
curl -X POST http://localhost:8000/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{
    "id": "eval-001",
    "model_name": "gpt-4",
    "inputs": [{
      "prompt": "What is machine learning?",
      "reference": "Machine learning is a subset of AI"
    }]
  }'
```

### Batch Processing (Script)

```bash
python scripts/batch_runner.py data/sample_inputs/example_batch.json
```

### Batch Processing (API)

```bash
# Submit batch
curl -X POST http://localhost:8000/api/batch \
  -H "Content-Type: application/json" \
  -d @data/sample_inputs/example_batch.json

# Check status
curl http://localhost:8000/api/batch/status/batch-001

# Get results
curl http://localhost:8000/api/batch/result/batch-001
```

See [docs/api_docs.md](docs/api_docs.md) for complete API documentation.

## Features

✅ **Multi-Provider LLM Support**
- Google Gemini (Vertex AI)
- OpenAI GPT-4
- Anthropic Claude
- Automatic heuristic fallback

✅ **Comprehensive Evaluation**
- 5-dimensional scoring system
- Rule-based and LLM-based checks
- Configurable weighted scoring

✅ **Batch Processing**
- Async processing for 1000s of responses
- Progress tracking
- Status polling API

✅ **Analytics Dashboard**
- Real-time statistics
- Interactive charts and visualizations
- Model comparison leaderboard
- Score distribution analysis
- Trend tracking

✅ **Database Integration**
- SQLite (default, no setup)
- PostgreSQL support
- Automatic schema creation

✅ **Modern Frontend**
- Beautiful, responsive UI
- Single evaluation form
- Batch upload with drag & drop
- Real-time dashboard updates

## Documentation

- [Setup Guide](docs/SETUP_GUIDE.md) - Installation and configuration
- [API Documentation](docs/api_docs.md) - Complete API reference
- [Project Report](docs/project_report.md) - Architecture and methodology

## Folders

- `backend/` - FastAPI backend with evaluation logic
- `frontend/` - React frontend for UI
- `data/` - Sample data and evaluation results
- `docs/` - Architecture and API documentation
- `scripts/` - Utility scripts for data processing
