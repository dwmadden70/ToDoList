from pathlib import Path
from todolist.config import DEFAULT_THEME, MAX_HEADER_LENGTH, MAX_TASK_LENGTH
from todolist.database import TaskDatabase


def test_task_lifecycle(tmp_path: Path) -> None:
    db = TaskDatabase(tmp_path / "test.db")

    # Add task
    db.add("Buy groceries")
    tasks = db.get_all()
    assert len(tasks) == 1
    assert tasks[0].title == "Buy groceries"
    assert tasks[0].completed is False

    # Update task title
    db.update_title(tasks[0].id, "Buy organic groceries")
    assert db.get_all()[0].title == "Buy organic groceries"

    # Toggle completion
    db.toggle(tasks[0].id, True)
    assert db.get_all()[0].completed is True

    # Delete task
    db.delete(tasks[0].id)
    assert db.get_all() == []


def test_task_sanitization_and_edge_cases(tmp_path: Path) -> None:
    db = TaskDatabase(tmp_path / "edge.db")

    # Blank / whitespace-only tasks are ignored
    db.add("   ")
    assert db.get_all() == []

    # Oversized task title is truncated safely
    long_title = "A" * (MAX_TASK_LENGTH + 50)
    db.add(long_title)
    tasks = db.get_all()
    assert len(tasks) == 1
    assert len(tasks[0].title) == MAX_TASK_LENGTH

    # Empty update does not overwrite existing title
    db.update_title(tasks[0].id, "   ")
    assert len(db.get_all()[0].title) == MAX_TASK_LENGTH

    # Special characters (quotes, SQL syntax) are stored safely
    special = "'; DROP TABLE tasks; --"
    db.update_title(tasks[0].id, special)
    assert db.get_all()[0].title == special

    # Operations on non-existent task IDs do not raise errors
    db.toggle(9999, True)
    db.update_title(9999, "Ghost task")
    db.delete(9999)


def test_settings_persistence_and_validation(tmp_path: Path) -> None:
    db = TaskDatabase(tmp_path / "settings.db")

    # Default fallback when key is unset
    assert db.get_setting("header_text", "Default Header") == "Default Header"

    # Set and overwrite settings
    db.set_setting("header_text", "Work Tasks")
    assert db.get_setting("header_text", "Default Header") == "Work Tasks"

    db.set_setting("header_text", "Personal Tasks")
    assert db.get_setting("header_text", "Default Header") == "Personal Tasks"

    # Header length cap
    db.set_setting("header_text", "H" * (MAX_HEADER_LENGTH + 25))
    assert len(db.get_setting("header_text", "Default")) == MAX_HEADER_LENGTH

    # Theme validation falls back to DEFAULT_THEME on invalid values
    db.set_setting("theme", "dark")
    assert db.get_setting("theme", DEFAULT_THEME) == "dark"

    db.set_setting("theme", "invalid_theme")
    assert db.get_setting("theme", DEFAULT_THEME) == DEFAULT_THEME
