import json
import sqlite3
from datetime import datetime, timezone
from typing import Any

from app.settings import DATABASE_PATH


def init_db() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS release_assessments (
                release_id TEXT PRIMARY KEY,
                repository TEXT NOT NULL,
                organization TEXT NOT NULL,
                target_environment TEXT NOT NULL,
                risk_score INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                decision TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner TEXT NOT NULL,
                topic TEXT NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def save_assessment(payload: dict[str, Any]) -> None:
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO release_assessments
            (release_id, repository, organization, target_environment, risk_score, risk_level, decision, payload, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["releaseId"],
                payload["repository"],
                payload["organization"],
                payload["targetEnvironment"],
                payload["riskScore"],
                payload["riskLevel"],
                payload["decision"],
                json.dumps(payload),
                payload["createdAt"],
            ),
        )


def list_assessments() -> list[dict[str, Any]]:
    with sqlite3.connect(DATABASE_PATH) as conn:
        rows = conn.execute(
            """
            SELECT release_id, repository, organization, target_environment, risk_score, risk_level, decision, created_at
            FROM release_assessments
            ORDER BY created_at DESC
            LIMIT 50
            """
        ).fetchall()
    return [
        {
            "releaseId": row[0],
            "repository": row[1],
            "organization": row[2],
            "targetEnvironment": row[3],
            "riskScore": row[4],
            "riskLevel": row[5],
            "decision": row[6],
            "createdAt": row[7],
        }
        for row in rows
    ]


def get_assessment(release_id: str) -> dict[str, Any] | None:
    with sqlite3.connect(DATABASE_PATH) as conn:
        row = conn.execute(
            "SELECT payload FROM release_assessments WHERE release_id = ?",
            (release_id,),
        ).fetchone()
    return json.loads(row[0]) if row else None


def remember(owner: str, topic: str, body: str) -> None:
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute(
            "INSERT INTO agent_memories(owner, topic, body, created_at) VALUES (?, ?, ?, ?)",
            (owner, topic, body, datetime.now(timezone.utc).isoformat()),
        )
