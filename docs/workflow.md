┌─────────────────────────────────────────────────────────────┐
│                   React Frontend (Port 3000)                 │
│                    ┌──────────────────┐                      │
│                    │  Evaluation Form │                      │
│                    │ (Request, Prompt,│                      │
│                    │  Response, Ref)  │                      │
│                    └────────┬─────────┘                      │
│                             │                                │
│                      HTTP POST Request                       │
│                             │                                │
└─────────────────────────────┼────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│               FastAPI Backend (Port 8000)                    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          POST /api/evaluate Endpoint                 │  │
│  │                                                       │  │
│  │  1. Rule-Based Checks (Length, Punctuation, etc.)   │  │
│  │     ├─ Check response length                         │  │
│  │     ├─ Check for punctuation                         │  │
│  │     └─ Check keyword overlap with prompt             │  │
│  │                                                       │  │
│  │  2. LLM Evaluation (Gemini / Fallback)              │  │
│  │     ├─ Send prompt + response to Gemini API         │  │
│  │     ├─ Get JSON with 5 dimension scores             │  │
│  │     └─ If API fails → Use heuristic fallback        │  │
│  │                                                       │  │
│  │  3. Score Aggregation                               │  │
│  │     ├─ Combine rule-based + LLM scores             │  │
│  │     ├─ Weight and average them                       │  │
│  │     └─ Return final score (0-1)                      │  │
│  │                                                       │  │
│  │  4. Store Results                                    │  │
│  │     └─ Save to data/evaluations.json                 │  │
│  │                                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │     Batch Processing (For 1000s of responses)        │  │
│  │                                                       │  │
│  │  POST /api/batch                                     │  │
│  │    ├─ Submit batch of responses                      │  │
│  │    └─ Returns immediately with batch_id              │  │
│  │                                                       │  │
│  │  GET /api/batch/status/{batch_id}                    │  │
│  │    └─ Check progress (50% done, 100 responses)       │  │
│  │                                                       │  │
│  │  GET /api/batch/result/{batch_id}                    │  │
│  │    └─ Get final aggregated results                   │  │
│  │                                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         LLM Provider (Gemini via Google Cloud)       │  │
│  │                                                       │  │
│  │  • Uses Google Cloud Vertex AI                       │  │
│  │  • Sends evaluation prompt to Gemini                 │  │
│  │  • Parses JSON response with dimension scores        │  │
│  │  • Falls back to heuristics if API fails             │  │
│  │                                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Data Storage (JSON Files)                  │  │
│  │                                                       │  │
│  │  • evaluations.json → All submitted responses        │  │
│  │  • Results per ID with scores & reasons              │  │
│  │                                                       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘