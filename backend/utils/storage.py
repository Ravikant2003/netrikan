import json
import sqlite3
from pathlib import Path
from typing import Any

from config import settings


def _connect() -> sqlite3.Connection:
    db_path = Path(settings.DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                payload TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS guardians (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                contact TEXT NOT NULL
            )
            """
        )


def upsert_user(user: dict[str, Any]) -> None:
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO users (id, payload)
            VALUES (?, ?)
            ON CONFLICT(id) DO UPDATE SET payload = excluded.payload
            """,
            (user["id"], json.dumps(user)),
        )


def add_guardian(user_id: str, contact: str) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO guardians (user_id, contact) VALUES (?, ?)",
            (user_id, contact),
        )


def list_guardians(user_id: str) -> list[str]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT contact FROM guardians WHERE user_id = ?",
            (user_id,),
        ).fetchall()
    return [row[0] for row in rows]
