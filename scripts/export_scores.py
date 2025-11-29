import json
from pathlib import Path

if __name__ == '__main__':
    data_file = Path(__file__).resolve().parents[1] / 'data' / 'evaluations.json'
    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print('Found', len(data), 'evaluations')
    else:
        print('No evaluations found at', data_file)
