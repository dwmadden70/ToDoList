import sqlite3
from pathlib import Path
from todolist.models import Task


class TaskDatabase:
    """Manages SQLite storage for tasks and user settings."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
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

    def get_setting(self, key: str, default: str) -> str:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            ).fetchone()
        if row is None:
            return default
        (value,) = row
        return value

    def set_setting(self, key: str, value: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value),
            )

    def get_all(self) -> list[Task]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, title, completed FROM tasks ORDER BY id ASC"
            ).fetchall()
        return [
            Task(id=task_id, title=title, completed=bool(completed))
            for task_id, title, completed in rows
        ]

    def add(self, title: str) -> None:
        with self._connect() as conn:
            conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))

    def toggle(self, task_id: int, completed: bool) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE tasks SET completed = ? WHERE id = ?",
                (int(completed), task_id),
            )

    def update_title(self, task_id: int, new_title: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE tasks SET title = ? WHERE id = ?",
                (new_title, task_id),
            )

    def delete(self, task_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
