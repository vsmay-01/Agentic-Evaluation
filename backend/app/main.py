try:
    # Ensure .env is loaded before other imports so settings pick up values
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
except Exception:
    # If python-dotenv is not installed, proceed; environment vars may be set externally
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import health, evaluate, batch

app = FastAPI(title="LLM Evaluation Backend")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health")
app.include_router(evaluate.router, prefix="/evaluate")
app.include_router(batch.router, prefix="/api")

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "llm-evaluation-backend",
        "endpoints": {
            "single": "POST /evaluate/",
            "batch": "POST /api/batch",
            "batch_status": "GET /api/batch/status/{batch_id}",
            "batch_result": "GET /api/batch/result/{batch_id}",
            "health": "GET /health/ready"
        }
    }

