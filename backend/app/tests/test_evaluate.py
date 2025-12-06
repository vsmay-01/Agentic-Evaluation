"""
Unit tests for evaluation endpoints and services.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services import rule_based, score_aggregator, llm_judge

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health/ready")
    assert response.status_code == 200


def test_evaluate_endpoint_basic():
    """Test basic evaluation endpoint."""
    payload = {
        "id": "test-001",
        "model_name": "test-model",
        "inputs": [
            {
                "prompt": "What is machine learning?",
                "reference": "Machine learning is a subset of AI."
            }
        ]
    }
    response = client.post("/evaluate/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "score" in data
    assert 0 <= data["score"] <= 1
    assert "details" in data


def test_evaluate_endpoint_multiple_inputs():
    """Test evaluation with multiple inputs."""
    payload = {
        "id": "test-002",
        "model_name": "test-model",
        "inputs": [
            {"prompt": "Question 1", "reference": "Answer 1"},
            {"prompt": "Question 2", "reference": "Answer 2"},
        ]
    }
    response = client.post("/evaluate/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-002"


def test_rule_based_checks():
    """Test rule-based evaluation checks."""
    # Test empty response
    result = rule_based.apply_rule_checks("Test prompt", "")
    assert result["score"] < 1.0
    assert len(result["issues"]) > 0
    
    # Test good response
    result = rule_based.apply_rule_checks(
        "Test prompt about machine learning",
        "This is a good response about machine learning. It addresses the prompt."
    )
    assert result["score"] > 0.5
    assert len(result["issues"]) == 0


def test_score_aggregator():
    """Test score aggregation functions."""
    # Simple average
    scores = [0.8, 0.9, 0.7]
    result = score_aggregator.aggregate_scores(scores)
    assert result == pytest.approx(0.8, abs=0.01)
    
    # Weighted average
    scores_dict = {
        "instruction_following": 0.9,
        "accuracy": 0.8,
    }
    weights = {
        "instruction_following": 0.6,
        "accuracy": 0.4,
    }
    result = score_aggregator.aggregate_scores_weighted(scores_dict, weights)
    assert result == pytest.approx(0.86, abs=0.01)


def test_llm_judge_heuristics():
    """Test LLM judge with heuristics fallback."""
    prompt = "What is AI?"
    response = "AI is artificial intelligence. I think it's probably useful."
    
    result = llm_judge.judge_with_heuristics(prompt, response)
    assert "score" in result
    assert "reason" in result
    assert "dimension_scores" in result
    assert 0 <= result["score"] <= 1


def test_batch_endpoint():
    """Test batch submission endpoint."""
    payload = {
        "id": "batch-test-001",
        "model_name": "test-model",
        "inputs": [
            {"prompt": "Test 1", "reference": "Answer 1"},
            {"prompt": "Test 2", "reference": "Answer 2"},
        ]
    }
    response = client.post("/api/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "batch_id" in data
    assert data["batch_id"] == "batch-test-001"


def test_batch_status_endpoint():
    """Test batch status endpoint."""
    # First submit a batch
    payload = {
        "id": "batch-status-test",
        "model_name": "test-model",
        "inputs": [{"prompt": "Test", "reference": "Answer"}]
    }
    submit_response = client.post("/api/batch", json=payload)
    batch_id = submit_response.json()["batch_id"]
    
    # Check status
    status_response = client.get(f"/api/batch/status/{batch_id}")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert "status" in status_data
    assert "total" in status_data
