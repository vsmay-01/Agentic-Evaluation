# API Documentation

## Base URL

- Development: `http://localhost:8000`
- Production: (configure as needed)

## Authentication

Currently, no authentication is required. For production, implement API keys or OAuth.

## Endpoints

### Health Checks

#### GET `/health/ready`
Check if the service is ready to accept requests.

**Response:**
```json
{
  "status": "ready"
}
```

#### GET `/health/live`
Liveness check.

**Response:**
```json
{
  "status": "alive"
}
```

---

### Single Evaluation

#### POST `/evaluate/`
Evaluate a single agent response.

**Request Body:**
```json
{
  "id": "eval-001",
  "model_name": "gpt-4",
  "inputs": [
    {
      "prompt": "What is machine learning?",
      "agent_response": "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
      "reference": "Machine learning is a subset of AI."
    }
  ]
}
```

**Note**: `agent_response` is required - this is the actual response from the agent that will be evaluated. `reference` is optional and used for accuracy comparison.

**Response:**
```json
{
  "id": "eval-001",
  "score": 0.85,
  "details": {
    "dimension_scores": {
      "instruction_following": 0.9,
      "hallucination_prevention": 0.8,
      "assumption_prevention": 0.85,
      "coherence": 0.9,
      "accuracy": 0.8
    },
    "individual_scores": {
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

---

### Batch Evaluation

#### POST `/api/batch`
Submit a batch of evaluations for processing.

**Request Body:**
```json
{
  "id": "batch-001",
  "model_name": "gpt-4",
  "inputs": [
    {
      "prompt": "What is AI?",
      "agent_response": "AI is artificial intelligence...",
      "reference": "Expected answer (optional)"
    },
    {
      "prompt": "What is machine learning?",
      "agent_response": "Machine learning is...",
      "reference": "Expected answer (optional)"
    }
  ]
}
```

**Note**: Each input must include `prompt` and `agent_response`. `reference` is optional.

**Response:**
```json
{
  "batch_id": "batch-001",
  "status": "queued",
  "total": 2,
  "message": "Batch batch-001 queued for processing. Check /batch/status/batch-001 for progress."
}
```

#### GET `/api/batch/status/{batch_id}`
Get the status of a batch evaluation.

**Response:**
```json
{
  "batch_id": "batch-001",
  "status": "processing",
  "total": 100,
  "processed": 45
}
```

**Status Values:**
- `queued`: Batch is queued for processing
- `processing`: Batch is being processed
- `completed`: Batch processing completed
- `failed`: Batch processing failed

#### GET `/api/batch/result/{batch_id}`
Get the final result of a completed batch.

**Response:**
```json
{
  "batch_id": "batch-001",
  "model_name": "gpt-4",
  "total_evaluated": 100,
  "average_score": 0.85,
  "dimension_averages": {
    "instruction_following": 0.87,
    "hallucination_prevention": 0.82,
    "assumption_prevention": 0.85,
    "coherence": 0.89,
    "accuracy": 0.84
  },
  "score_distribution": {
    "excellent": 35,
    "good": 45,
    "fair": 15,
    "poor": 5
  },
  "results": [...]
}
```

---

### Dashboard Analytics

#### GET `/api/dashboard/stats`
Get overall dashboard statistics.

**Response:**
```json
{
  "total_evaluations": 120,
  "average_score": 0.852,
  "models_evaluated": 4,
  "excellent_responses": 35
}
```

#### GET `/api/dashboard/dimension-stats`
Get average scores per dimension.

**Response:**
```json
[
  {
    "name": "Instruction Following",
    "score": 0.87
  },
  {
    "name": "Hallucination Prevention",
    "score": 0.82
  }
]
```

#### GET `/api/dashboard/model-comparison`
Get comparison statistics by model.

**Response:**
```json
[
  {
    "model": "gpt-4",
    "score": 0.89,
    "count": 45
  },
  {
    "model": "claude-3",
    "score": 0.86,
    "count": 32
  }
]
```

#### GET `/api/dashboard/score-distribution`
Get score distribution across categories.

**Response:**
```json
{
  "excellent": 35,
  "good": 45,
  "fair": 15,
  "poor": 5
}
```

#### GET `/api/dashboard/trend`
Get score trend over time.

**Query Parameters:**
- `days` (optional): Number of days to look back (default: 7)

**Response:**
```json
[
  {
    "date": "Jan 10",
    "score": 0.82
  },
  {
    "date": "Jan 11",
    "score": 0.84
  }
]
```

#### GET `/api/dashboard/recent`
Get recent evaluations.

**Query Parameters:**
- `limit` (optional): Number of results (default: 10)

**Response:**
```json
[
  {
    "id": "eval-001",
    "model": "gpt-4",
    "score": 0.92,
    "date": "2024-01-15"
  }
]
```

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
  "detail": "Error message here"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. For production, implement rate limiting based on your needs.

## Examples

### Python Example

```python
import requests

# Single evaluation
response = requests.post(
    "http://localhost:8000/evaluate/",
    json={
        "id": "test-001",
        "model_name": "gpt-4",
        "inputs": [
            {
                "prompt": "What is AI?",
                "agent_response": "AI is artificial intelligence that enables machines to perform tasks requiring human intelligence",
                "reference": "AI is artificial intelligence"  # Optional
            }
        ]
    }
)
print(response.json())
```

### cURL Example

```bash
curl -X POST http://localhost:8000/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-001",
    "model_name": "gpt-4",
    "inputs": [{
      "prompt": "What is AI?",
      "agent_response": "AI is artificial intelligence that enables machines to perform tasks requiring human intelligence",
      "reference": "AI is artificial intelligence"
    }]
  }'
```
