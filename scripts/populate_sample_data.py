import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / 'data' / 'sample_inputs'

if __name__ == '__main__':
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    sample = {
        "id": "example-1",
        "model_name": "gpt-example",
        "inputs": [
            {"prompt": "Write a short summary.", "reference": "A brief summary."}
        ]
    }
    out = DATA_DIR / 'example_batch.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump([sample], f, indent=2)
    print('Wrote', out)
