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

## Running the System

### Backend (FastAPI)
```powershell
# From project root, activate venv
& "venv/Scripts/Activate.ps1"

# Start the backend on port 8000
uvicorn backend.app.main:app --reload --port 8000
```

Backend endpoints:
- `POST /evaluate/` - Submit evaluation requests
- `GET /health/ready` - Readiness check
- `GET /health/live` - Liveness check

### Frontend (React)
```powershell
# From project root
cd frontend/react_app
npm install
npm start
```

React app runs on http://localhost:3000 with proxy to http://localhost:8000

## Example Evaluation Request

```json
{
  "id": "eval-001",
  "model_name": "gpt-4",
  "inputs": [
    {
      "prompt": "Summarize the key benefits of machine learning",
      "reference": "Expected summary or reference answer"
    }
  ]
}
```

## Example Response

```json
{
  "id": "eval-001",
  "score": 0.85,
  "details": {
    "dimension_scores": {
      "input_0_rule_score": 0.8,
      "input_0_llm_score": 0.9
    },
    "evaluation_details": {
      "input_0_rule_issues": [],
      "input_0_llm_reason": "Response meets evaluation criteria"
    },
    "model_name": "gpt-4"
  }
}
```

## Next Steps

- [ ] Integrate real LLM API (GPT-4, Claude) for better hallucination detection
- [ ] Add weighted scoring by dimension
- [ ] Implement batch API for 1000s of responses
- [ ] Add leaderboard/analytics dashboard
- [ ] Support custom evaluation rules
- [ ] Add database backend (PostgreSQL) for persistence

## Folders

- `backend/` - FastAPI backend with evaluation logic
- `frontend/` - React frontend for UI
- `data/` - Sample data and evaluation results
- `docs/` - Architecture and API documentation
- `scripts/` - Utility scripts for data processing
