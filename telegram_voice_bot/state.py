from __future__ import annotations

import sqlite3
from pathlib import Path

PERSONA_OVERRIDE = "persona_override"
STANDING_TASK = "standing_task"
STORED_MESSAGES_PER_CHAT = 200


class State:
    """Local SQLite store for the standing task, persona override, and chat history."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = self._connect()
        try:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
                );
                CREATE INDEX IF NOT EXISTS idx_messages_chat ON messages(chat_id, id);
                """
            )
            conn.commit()
        finally:
            conn.close()

    def get_persona_override(self) -> str | None:
        return self._get(PERSONA_OVERRIDE)

    def set_persona_override(self, text: str) -> None:
        self._set(PERSONA_OVERRIDE, text.strip())

    def clear_persona_override(self) -> None:
        self._delete(PERSONA_OVERRIDE)

    def get_standing_task(self) -> str | None:
        return self._get(STANDING_TASK)

    def set_standing_task(self, text: str) -> None:
        self._set(STANDING_TASK, text.strip())

    def clear_standing_task(self) -> None:
        self._delete(STANDING_TASK)

    def add_message(self, chat_id: int, role: str, content: str) -> None:
        if role not in {"user", "assistant"}:
            raise ValueError(f"Unsupported role: {role}")
        text = content.strip()
        if not text:
            return
        conn = self._connect()
        try:
            conn.execute(
                "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
                (chat_id, role, text),
            )
            conn.execute(
                """
                DELETE FROM messages
                WHERE chat_id = ?
                  AND id NOT IN (
                      SELECT id FROM messages
                      WHERE chat_id = ?
                      ORDER BY id DESC
                      LIMIT ?
                  )
                """,
                (chat_id, chat_id, STORED_MESSAGES_PER_CHAT),
            )
            conn.commit()
        finally:
            conn.close()

    def recent_messages(self, chat_id: int, limit: int) -> list[dict[str, str]]:
        conn = self._connect()
        try:
            rows = conn.execute(
                """
                SELECT role, content FROM messages
                WHERE chat_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (chat_id, limit),
            ).fetchall()
        finally:
            conn.close()
        return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]

    def clear_history(self, chat_id: int) -> None:
        conn = self._connect()
        try:
            conn.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
            conn.commit()
        finally:
            conn.close()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _get(self, key: str) -> str | None:
        conn = self._connect()
        try:
            row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        finally:
            conn.close()
        if row is None:
            return None
        value = str(row["value"]).strip()
        return value or None

    def _set(self, key: str, value: str) -> None:
        conn = self._connect()
        try:
            conn.execute(
                """
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )
            conn.commit()
        finally:
            conn.close()

    def _delete(self, key: str) -> None:
        conn = self._connect()
        try:
            conn.execute("DELETE FROM settings WHERE key = ?", (key,))
            conn.commit()
        finally:
            conn.close()
