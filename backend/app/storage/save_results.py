from pathlib import Path
import json

DATA_FILE = Path(__file__).resolve().parents[2] / ".." / ".." / "data" / "evaluations.json"


def save_result(result: dict):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = []
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = []
    data.append(result)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
