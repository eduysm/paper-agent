"""SQLite-backed persistence for UserProfile objects.

Uses only the Python standard library (sqlite3). The database file location is
controlled by the DB_PATH environment variable (default: /data/doctorate_reader.db).
"""
import json
import os
import sqlite3
import uuid
from pathlib import Path
from typing import Optional

from doctorate_reader.schemas import UserProfile


def _db_path() -> str:
    return os.getenv("DB_PATH", "/data/doctorate_reader.db")


def _get_conn() -> sqlite3.Connection:
    path = _db_path()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                id           TEXT PRIMARY KEY,
                interests    TEXT NOT NULL,
                research_line TEXT,
                example_docs TEXT
            )
            """
        )


def create_profile(profile: UserProfile) -> str:
    profile_id = str(uuid.uuid4())
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO profiles (id, interests, research_line, example_docs) VALUES (?, ?, ?, ?)",
            (
                profile_id,
                json.dumps(profile.interests),
                profile.research_line,
                json.dumps(profile.example_docs) if profile.example_docs else None,
            ),
        )
    return profile_id


def get_profile(profile_id: str) -> Optional[UserProfile]:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM profiles WHERE id = ?", (profile_id,)
        ).fetchone()
    if not row:
        return None
    return UserProfile(
        interests=json.loads(row["interests"]),
        research_line=row["research_line"],
        example_docs=json.loads(row["example_docs"]) if row["example_docs"] else None,
    )


def update_profile(profile_id: str, profile: UserProfile) -> bool:
    with _get_conn() as conn:
        cursor = conn.execute(
            "UPDATE profiles SET interests=?, research_line=?, example_docs=? WHERE id=?",
            (
                json.dumps(profile.interests),
                profile.research_line,
                json.dumps(profile.example_docs) if profile.example_docs else None,
                profile_id,
            ),
        )
    return cursor.rowcount > 0


def delete_profile(profile_id: str) -> bool:
    with _get_conn() as conn:
        cursor = conn.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
    return cursor.rowcount > 0
