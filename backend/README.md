Backend (FastAPI)

This folder contains the FastAPI application for evaluating agent LLM outputs on multiple dimensions.

## Problem Statement

Evaluate agent responses across 5 key dimensions:
1. **Instruction Following** - Does the response follow the prompt exactly?
2. **Hallucination Prevention** - Are facts accurate or made-up?
3. **Assumption Prevention** - Are unnecessary assumptions avoided?
4. **Response Coherence** - Is the response logically structured?
5. **Response Accuracy** - Does it answer the query correctly?

## Evaluation Pipeline

```
1. Agent Prompt + Response
         ↓
2. Rule-Based Checks (Instruction Following, Coherence)
         ↓
3. LLM Heuristics (Hallucination, Assumptions, Accuracy)
         ↓
4. Score Aggregation (weighted average)
         ↓
5. Result Storage (JSON)
```

## API Endpoints

### POST /evaluate/
Submit a batch of agent responses for evaluation.

**Request:**
```json
{
  "id": "unique-request-id",
  "model_name": "gpt-4",
  "inputs": [
    {
      "prompt": "User prompt/instruction",
      "reference": "Expected response or reference"
    }
  ]
}
```

**Response:**
```json
{
  "id": "unique-request-id",
  "score": 0.85,
  "details": {
    "dimension_scores": {
      "input_0_rule_score": 0.8,
      "input_0_llm_score": 0.9
    },
    "evaluation_details": {...},
    "model_name": "gpt-4"
  }
}
```

### GET /health/ready
Check if the service is ready.

### GET /health/live
Check if the service is alive.

## Running

```powershell
# Activate virtual environment
& "venv/Scripts/Activate.ps1"

# Install dependencies
pip install -r backend/app/requirements.txt

# Run with uvicorn
uvicorn backend.app.main:app --reload --port 8000
```

API will be available at http://localhost:8000
