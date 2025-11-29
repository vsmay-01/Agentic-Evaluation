import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / ".." / ".." / "data" / "evaluations.db"


def get_connection(path=None):
    path = path or str(DB_PATH)
    conn = sqlite3.connect(path)
    return conn
