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
        return row[0] if row else default

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
        return [Task(id=r[0], title=r[1], completed=bool(r[2])) for r in rows]

    def add(self, title: str) -> None:
        with self._connect() as conn:
            conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))

    def toggle(self, task_id: int, completed: bool) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE tasks SET completed = ? WHERE id = ?",
                (int(completed), task_id),
            )

    def delete(self, task_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
