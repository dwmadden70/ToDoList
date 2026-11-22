from contextlib import closing
import os
from pathlib import Path
import sqlite3
from todolist.config import DEFAULT_THEME, MAX_HEADER_LENGTH, MAX_TASK_LENGTH, VALID_THEMES
from todolist.models import Task


class TaskDatabase:
    """Manages SQLite storage for tasks and user settings."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path, timeout=5.0)

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as conn:
            with conn:
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        completed INTEGER NOT NULL DEFAULT 0
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                """)
        try:
            os.chmod(self.db_path, 0o600)
        except OSError:
            pass

    def get_setting(self, key: str, default: str) -> str:
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            ).fetchone()
        if row is None:
            return default
        (value,) = row
        if key == "theme" and value.lower() not in VALID_THEMES:
            return DEFAULT_THEME
        if key == "header_text":
            return value[:MAX_HEADER_LENGTH]
        return value

    def set_setting(self, key: str, value: str) -> None:
        sanitized = value
        if key == "theme":
            normalized = value.strip().lower()
            sanitized = normalized if normalized in VALID_THEMES else DEFAULT_THEME
        elif key == "header_text":
            sanitized = value.strip()[:MAX_HEADER_LENGTH]

        with closing(self._connect()) as conn:
            with conn:
                conn.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                    (key, sanitized),
                )

    def get_all(self) -> list[Task]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT id, title, completed FROM tasks ORDER BY id ASC"
            ).fetchall()
        return [
            Task(id=task_id, title=title, completed=bool(completed))
            for task_id, title, completed in rows
        ]

    def add(self, title: str) -> None:
        sanitized = title.strip()[:MAX_TASK_LENGTH]
        if not sanitized:
            return
        with closing(self._connect()) as conn:
            with conn:
                conn.execute("INSERT INTO tasks (title) VALUES (?)", (sanitized,))

    def toggle(self, task_id: int, completed: bool) -> None:
        with closing(self._connect()) as conn:
            with conn:
                conn.execute(
                    "UPDATE tasks SET completed = ? WHERE id = ?",
                    (int(completed), task_id),
                )

    def update_title(self, task_id: int, new_title: str) -> None:
        sanitized = new_title.strip()[:MAX_TASK_LENGTH]
        if not sanitized:
            return
        with closing(self._connect()) as conn:
            with conn:
                conn.execute(
                    "UPDATE tasks SET title = ? WHERE id = ?",
                    (sanitized, task_id),
                )

    def delete(self, task_id: int) -> None:
        with closing(self._connect()) as conn:
            with conn:
                conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
