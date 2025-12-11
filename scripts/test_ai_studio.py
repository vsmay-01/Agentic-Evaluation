"""Quick tester for AI Studio / Gemini REST endpoint.

Reads `AI_STUDIO_API_KEY` and `AI_STUDIO_ENDPOINT` from environment (or .env) and makes
one predict call with a tiny prompt to verify connectivity and parsing.

Usage:
    python scripts/test_ai_studio.py

This script is minimal and intended for debugging connectivity (not for production use).
"""
import os
import json
import requests

from pathlib import Path

# Try to load .env if present
try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
except Exception:
    pass

API_KEY = os.getenv("AI_STUDIO_API_KEY")
ENDPOINT = os.getenv("AI_STUDIO_ENDPOINT")
MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

if not API_KEY:
    print("AI_STUDIO_API_KEY not set. Please set it in your environment or .env file.")
    raise SystemExit(1)

if not ENDPOINT:
    # Try to construct a default endpoint if project id is present
    # If you set `PROJECT_ID` (or `AI_STUDIO_PROJECT`) we can attempt to construct a default endpoint,
    # but it's recommended to copy the full REST/Invoke URL from AI Studio and set `AI_STUDIO_ENDPOINT`.
    PROJECT = os.getenv("PROJECT_ID") or os.getenv("AI_STUDIO_PROJECT")
    LOCATION = os.getenv("AI_STUDIO_LOCATION") or "us-central1"
    if PROJECT:
        ENDPOINT = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/{LOCATION}/models/{MODEL}:predict"
        print(f"No AI_STUDIO_ENDPOINT set; constructed endpoint: {ENDPOINT}")
    else:
        print("AI_STUDIO_ENDPOINT not set. Set AI_STUDIO_ENDPOINT in .env with the model's REST invoke URL.")
        raise SystemExit(1)

prompt = "Evaluate this short response. Return JSON with fields instruction_following, hallucination_prevention, assumption_prevention, coherence, accuracy, reason.\nPrompt: say hello. Response: Hello world."

payload = {"instances": [{"content": prompt}]}
headers = {"Content-Type": "application/json"}
params = {"key": API_KEY}

print("Sending test request to AI Studio endpoint...")
try:
    resp = requests.post(ENDPOINT, params=params, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    j = resp.json()
    print("Raw response:")
    print(json.dumps(j, indent=2)[:4000])
except Exception as e:
    print("Request failed:", str(e))
    raise

# Attempt to extract text
text = None
if isinstance(j, dict):
    if "predictions" in j and isinstance(j["predictions"], list) and j["predictions"]:
        first = j["predictions"][0]
        if isinstance(first, dict):
            for k in ("content", "text", "output", "generated_text", "completion"):
                if k in first:
                    text = first[k]
                    break
        elif isinstance(first, str):
            text = first

if text is None:
    # try other shapes
    for candidate_key in ("candidates", "outputs", "response", "data"):
        if candidate_key in j:
            val = j[candidate_key]
            if isinstance(val, list) and val:
                item = val[0]
                if isinstance(item, dict) and "content" in item:
                    text = item["content"]
                    break
                elif isinstance(item, str):
                    text = item
                    break

if text is None:
    print("Could not extract textual output from response; printing full JSON")
    print(json.dumps(j, indent=2)[:4000])
else:
    print("Extracted text:")
    print(text)
    # Try to find JSON inside
    import re
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            parsed = json.loads(m.group(0))
            print("Parsed JSON from text:")
            print(json.dumps(parsed, indent=2))
        except Exception:
            print("Failed to parse JSON substring:")
            print(m.group(0))
    else:
        print("No JSON object found inside the model's text output.")
