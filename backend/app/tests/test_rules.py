"""
Unit tests for rule-based evaluation checks.
"""

import pytest
from backend.app.services import rule_based


def test_empty_response():
    """Test that empty response is flagged."""
    result = rule_based.apply_rule_checks("Test prompt", "")
    assert result["score"] < 0.5
    assert "empty" in " ".join(result["issues"]).lower()


def test_short_response():
    """Test that very short response is flagged."""
    result = rule_based.apply_rule_checks("Test prompt", "Hi")
    assert result["score"] < 1.0
    assert any("short" in issue.lower() for issue in result["issues"])


def test_no_sentence_structure():
    """Test that response without sentence structure is flagged."""
    result = rule_based.apply_rule_checks("Test prompt", "no punctuation here just words")
    assert result["score"] < 1.0
    assert any("sentence" in issue.lower() for issue in result["issues"])


def test_low_keyword_overlap():
    """Test that response with low keyword overlap is flagged."""
    result = rule_based.apply_rule_checks(
        "Tell me about machine learning and neural networks",
        "This is about something completely different"
    )
    assert result["score"] < 1.0
    assert any("overlap" in issue.lower() for issue in result["issues"])


def test_good_response():
    """Test that a good response gets high score."""
    result = rule_based.apply_rule_checks(
        "Explain machine learning",
        "Machine learning is a subset of artificial intelligence. It enables systems to learn from data."
    )
    assert result["score"] > 0.7
    assert len(result["issues"]) == 0


def test_score_normalization():
    """Test that scores are normalized to 0-1 range."""
    result = rule_based.apply_rule_checks("Test", "Test response")
    assert 0.0 <= result["score"] <= 1.0
