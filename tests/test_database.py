from pathlib import Path
from todolist.database import TaskDatabase


def test_task_lifecycle(tmp_path: Path) -> None:
    db = TaskDatabase(tmp_path / "test.db")

    # Add task
    db.add("Buy groceries")
    tasks = db.get_all()
    assert len(tasks) == 1
    assert tasks[0].title == "Buy groceries"
    assert tasks[0].completed is False

    # Toggle completion
    db.toggle(tasks[0].id, True)
    assert db.get_all()[0].completed is True

    # Delete task
    db.delete(tasks[0].id)
    assert db.get_all() == []
