import tkinter as tk
from pathlib import Path
import customtkinter as ctk
import pytest
from todolist.config import APP_NAME, MAX_HEADER_LENGTH, MAX_TASK_LENGTH
from todolist.database import TaskDatabase
from todolist.ui.app import TodoApp
from todolist.ui.confirm_dialog import ConfirmDeleteDialog
from todolist.ui.edit_dialog import EditTaskDialog
from todolist.ui.setup_dialog import SetupDialog


@pytest.fixture
def app(tmp_path: Path):
    """Creates a hidden TodoApp instance backed by a temporary SQLite database."""
    try:
        db = TaskDatabase(tmp_path / "ui_test.db")
        instance = TodoApp(db)
        instance.withdraw()
        instance.update_idletasks()
    except tk.TclError as exc:
        pytest.skip(f"Tk display unavailable in headless environment: {exc}")

    yield instance

    try:
        if instance.winfo_exists():
            instance._on_close()
    except tk.TclError:
        pass


def test_add_toggle_and_delete_task_without_confirmation(app: TodoApp) -> None:
    app.confirm_delete = False
    app.task_entry.insert(0, "Write UI tests")
    app.add_task()
    app.update_idletasks()

    tasks = app.db.get_all()
    assert len(tasks) == 1
    assert tasks[0].title == "Write UI tests"
    assert tasks[0].completed is False
    assert len(app.list_frame.winfo_children()) == 1

    # Toggle task completion
    app.toggle_task(tasks[0])
    app.update_idletasks()
    assert app.db.get_all()[0].completed is True

    # Delete immediately when confirm_delete is disabled
    app.delete_task(app.db.get_all()[0])
    app.update_idletasks()
    assert app.db.get_all() == []
    assert len(app.list_frame.winfo_children()) == 0


def test_task_length_enforced_in_ui(app: TodoApp) -> None:
    oversized = "x" * (MAX_TASK_LENGTH + 75)
    app.task_entry.insert(0, oversized)
    app.add_task()

    tasks = app.db.get_all()
    assert len(tasks) == 1
    assert len(tasks[0].title) == MAX_TASK_LENGTH


def test_setup_dialog_saves_header_theme_and_confirm_flag(app: TodoApp) -> None:
    saved_payload: list[tuple[str, str, bool]] = []

    def handle_save(header: str, theme: str, confirm: bool) -> None:
        saved_payload.append((header, theme, confirm))
        app._apply_settings(header, theme, confirm)

    dialog = SetupDialog(
        parent=app,
        current_header=app.header_text,
        current_theme="light",
        confirm_delete=True,
        on_save=handle_save,
    )
    app.update_idletasks()

    # Verify in-window modal attachment and initial Light-mode switch contrast
    assert dialog.master is app
    assert dialog.confirm_switch.cget("button_color") != ""

    # Update header, switch theme to Dark, and toggle confirm switch off
    dialog.header_entry.delete(0, "end")
    dialog.header_entry.insert(0, "  Work Sprint  ")
    dialog._set_theme("Dark")
    dialog._toggle_confirm_switch()
    dialog._save()
    app.update_idletasks()

    assert saved_payload == [("Work Sprint", "dark", False)]
    assert app.header_text == "Work Sprint"
    assert app.title_label.cget("text") == "Work Sprint"
    assert app.current_theme == "dark"
    assert app.confirm_delete is False
    assert app.db.get_setting("header_text", "") == "Work Sprint"
    assert app.db.get_setting("theme", "") == "dark"
    assert app.db.get_setting("confirm_delete", "") == "0"


def test_setup_dialog_cancel_discards_changes(app: TodoApp) -> None:
    dialog = SetupDialog(
        parent=app,
        current_header=APP_NAME,
        current_theme="light",
        confirm_delete=True,
        on_save=app._apply_settings,
    )
    app.update_idletasks()

    dialog.header_entry.delete(0, "end")
    dialog.header_entry.insert(0, "Temporary Title")
    dialog._set_theme("Dark")
    dialog._cancel()
    app.update_idletasks()

    assert app.header_text == APP_NAME
    assert app.current_theme == "light"


def test_setup_dialog_keyboard_navigation_and_alt_s_guard(app: TodoApp) -> None:
    opened_count = 0

    def fake_open_setup() -> None:
        nonlocal opened_count
        opened_count += 1
        app._setup_dialog = SetupDialog(
            parent=app,
            current_header=app.header_text,
            current_theme=app.current_theme,
            confirm_delete=app.confirm_delete,
            on_save=app._apply_settings,
        )

    app._open_setup = fake_open_setup  # type: ignore[method-assign]

    # First Alt-s opens setup overlay; second Alt-s is ignored while open
    app._on_alt_setup()
    app.update_idletasks()
    assert opened_count == 1
    assert app._is_setup_open() is True

    app._on_alt_setup()
    assert opened_count == 1

    dialog = app._setup_dialog
    assert dialog is not None

    # Cycle focus targets via Tab / Shift-Tab
    dialog._set_focus_index(0)
    assert dialog._focus_index == 0
    dialog._set_focus_index(dialog._focus_index + 1)
    assert dialog._focus_index == 1  # Theme selector

    # Space toggles Light <-> Dark when theme selector has focus
    dialog._on_space_key()
    assert dialog._selected_theme == "Dark"

    # Advance to confirm switch and toggle with Space
    dialog._set_focus_index(2)
    initial_confirm = dialog.confirm_var.get()
    dialog._on_space_key()
    assert dialog.confirm_var.get() is (not initial_confirm)

    dialog._cancel()
    app.update_idletasks()


def test_edit_task_dialog_updates_title_and_enforces_max_length(app: TodoApp) -> None:
    app.db.add("Initial title")
    task = app.db.get_all()[0]

    dialog = EditTaskDialog(
        parent=app,
        task=task,
        on_save=app._save_edited_task,
    )
    app.update_idletasks()

    dialog.task_entry.delete(0, "end")
    dialog.task_entry.insert(0, "Updated title " + ("z" * MAX_TASK_LENGTH))
    dialog._save()
    app.update_idletasks()

    updated = app.db.get_all()[0]
    assert updated.title.startswith("Updated title ")
    assert len(updated.title) == MAX_TASK_LENGTH


def test_confirm_delete_dialog_confirms_and_cancels(app: TodoApp) -> None:
    app.db.add("Task to keep")
    app.db.add("Task to remove")
    keep_task, remove_task = app.db.get_all()

    # Cancel deletion
    cancel_dialog = ConfirmDeleteDialog(
        parent=app,
        task=keep_task,
        on_confirm=app._confirm_delete_task,
    )
    app.update_idletasks()
    cancel_dialog._cancel()
    app.update_idletasks()
    assert len(app.db.get_all()) == 2

    # Confirm deletion
    confirm_dialog = ConfirmDeleteDialog(
        parent=app,
        task=remove_task,
        on_confirm=app._confirm_delete_task,
    )
    app.update_idletasks()
    confirm_dialog._confirm()
    app.update_idletasks()

    remaining = app.db.get_all()
    assert len(remaining) == 1
    assert remaining[0].id == keep_task.id


def test_header_truncation_in_setup_dialog(app: TodoApp) -> None:
    dialog = SetupDialog(
        parent=app,
        current_header=APP_NAME,
        current_theme="light",
        confirm_delete=True,
        on_save=app._apply_settings,
    )
    app.update_idletasks()

    dialog.header_entry.delete(0, "end")
    dialog.header_entry.insert(0, "H" * (MAX_HEADER_LENGTH + 25))
    dialog._save()
    app.update_idletasks()

    assert len(app.header_text) == MAX_HEADER_LENGTH
