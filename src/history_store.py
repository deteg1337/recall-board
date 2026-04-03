import sqlite3
import time
from pathlib import Path

from gi.repository import GLib


class HistoryStore:
    def __init__(self, db_path=None):
        if db_path is None:
            data_dir = Path(GLib.get_user_data_dir()) / "recall-board"
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = data_dir / "history.db"
        self.db_path = db_path
        self.connection = sqlite3.connect(str(self.db_path))
        self._create_table()

    def _create_table(self):
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                content_type TEXT NOT NULL DEFAULT 'text',
                created_at REAL NOT NULL,
                pinned INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        self.connection.commit()

    def add(self, content, content_type="text"):
        if not content or not content.strip():
            return None

        existing = self.connection.execute(
            "SELECT id FROM entries WHERE content = ?", (content,)
        ).fetchone()

        if existing:
            self.connection.execute(
                "UPDATE entries SET created_at = ? WHERE id = ?",
                (time.time(), existing[0]),
            )
            self.connection.commit()
            return existing[0]

        cursor = self.connection.execute(
            "INSERT INTO entries (content, content_type, created_at) VALUES (?, ?, ?)",
            (content, content_type, time.time()),
        )
        self.connection.commit()
        return cursor.lastrowid

    def get_all(self, limit=50):
        rows = self.connection.execute(
            """
            SELECT id, content, content_type, created_at, pinned
            FROM entries
            ORDER BY pinned DESC, created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        return [
            {
                "id": row[0],
                "content": row[1],
                "content_type": row[2],
                "created_at": row[3],
                "pinned": bool(row[4]),
            }
            for row in rows
        ]

    def delete(self, entry_id):
        self.connection.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        self.connection.commit()

    def clear(self):
        self.connection.execute("DELETE FROM entries WHERE pinned = 0")
        self.connection.commit()

    def close(self):
        self.connection.close()