import tkinter as tk
import customtkinter as ctk
from todolist.config import (
    APP_NAME,
    COLORS,
    DEFAULT_THEME,
    MAX_WIDTH,
    MIN_HEIGHT,
    MIN_WIDTH,
    WINDOW_SIZE,
)
from todolist.database import TaskDatabase
from todolist.models import Task
from todolist.ui.components import TaskRow
from todolist.ui.confirm_dialog import ConfirmDeleteDialog
from todolist.ui.edit_dialog import EditTaskDialog
from todolist.ui.icons import get_app_icon_photo, get_gear_icon
from todolist.ui.setup_dialog import SetupDialog


class _Tooltip:
    """Lightweight hover tooltip bound to a widget and its internal children."""

    def __init__(self, widget: ctk.CTkBaseClass, text: str, delay_ms: int = 400) -> None:
        self.widget = widget
        self.text = text
        self.delay_ms = delay_ms
        self._after_id: str | None = None
        self._tip_win: tk.Toplevel | None = None

        self._bind_recursive(widget)

    def _bind_recursive(self, target: tk.Misc) -> None:
        target.bind("<Enter>", self._schedule, add="+")
        target.bind("<Leave>", self._hide, add="+")
        target.bind("<ButtonPress>", self._hide, add="+")
        for child in target.winfo_children():
            self._bind_recursive(child)

    def _schedule(self, _event=None) -> None:
        self._cancel()
        self._after_id = self.widget.after(self.delay_ms, self._show)

    def _cancel(self) -> None:
        if self._after_id is not None:
            try:
                self.widget.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None

    def _show(self) -> None:
        if self._tip_win is not None or not self.widget.winfo_exists():
            return
        is_dark = ctk.get_appearance_mode().lower() == "dark"
        bg = "#1f2937" if is_dark else "#111827"
        fg = "#f9fafb"
        border = "#374151" if is_dark else "#1f2937"

        x = self.widget.winfo_rootx() + (self.widget.winfo_width() // 2) - 36
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6

        self._tip_win = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_attributes("-topmost", True)
        tw.wm_geometry(f"+{max(0, x)}+{max(0, y)}")

        lbl = tk.Label(
            tw,
            text=self.text,
            background=bg,
            foreground=fg,
            relief="solid",
            borderwidth=1,
            highlightbackground=border,
            padx=8,
            pady=4,
            font=("Segoe UI", 9),
        )
        lbl.pack()

    def _hide(self, _event=None) -> None:
        self._cancel()
        if self._tip_win is not None:
            try:
                self._tip_win.destroy()
            except tk.TclError:
                pass
            self._tip_win = None


class TodoApp(ctk.CTk):
    """Main cross-platform application window with modal setup configuration."""

    def __init__(self, db: TaskDatabase) -> None:
        super().__init__(fg_color=COLORS["window_bg"])
        self.db = db

        self.header_text = self.db.get_setting("header_text", APP_NAME)
        self.current_theme = self.db.get_setting("theme", DEFAULT_THEME)
        self.confirm_delete = self.db.get_setting("confirm_delete", "1") == "1"
        self._setup_dialog: SetupDialog | None = None

        self.title(APP_NAME)
        self.geometry(WINDOW_SIZE)
        ctk.set_appearance_mode(self.current_theme)

        self._set_window_icon()
        self._configure_window_bounds()
        self._build_ui()
        self.refresh_list()

        self.bind_all("<Alt-s>", self._on_alt_setup)
        self.bind_all("<Alt-S>", self._on_alt_setup)

    def _set_window_icon(self) -> None:
        """Applies an in-memory rendered app icon across Windows, macOS, and Linux."""
        self._icon_photo = get_app_icon_photo(64)
        self.wm_iconphoto(True, self._icon_photo)

    def _configure_window_bounds(self) -> None:
        """Sets min size and caps width at 800px while allowing full usable OS height."""
        self.minsize(MIN_WIDTH, MIN_HEIGHT)
        screen_height = self.winfo_screenheight()
        usable_height = max(MIN_HEIGHT, screen_height - 80)
        self.maxsize(MAX_WIDTH, usable_height)

    def _build_ui(self) -> None:
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(16, 4))

        self.title_label = ctk.CTkLabel(
            header_frame,
            text=self.header_text,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_active"],
            anchor="w",
        )
        self.title_label.pack(side="left", fill="x", expand=True, padx=(0, 12))

        self.setup_btn = ctk.CTkButton(
            header_frame,
            text="",
            image=get_gear_icon(16),
            width=32,
            height=28,
            fg_color=COLORS["row_bg"],
            hover_color=COLORS["input_bg"],
            border_width=1,
            border_color=COLORS["input_border"],
            command=self._open_setup,
        )
        self.setup_btn.pack(side="right")
        self._setup_tooltip = _Tooltip(self.setup_btn, "Alt-s")

        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=(12, 10))

        self.task_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Add a task...",
            height=40,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["input_border"],
            text_color=COLORS["text_active"],
            placeholder_text_color=COLORS["text_done"],
            font=ctk.CTkFont(size=14),
        )
        self.task_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.task_entry.bind("<Return>", lambda _: self.add_task())

        add_btn = ctk.CTkButton(
            input_frame,
            text="Add",
            width=70,
            height=40,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color=COLORS["text_on_accent"],
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.add_task,
        )
        add_btn.pack(side="right")

        self.list_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self.list_frame._parent_canvas.grid_configure(padx=0)
        self.list_frame._parent_canvas.configure(highlightthickness=0)
        self.list_frame._parent_canvas.bind("<Configure>", self._on_list_resize)

    def _on_list_resize(self, event) -> None:
        """Forces inner task rows to stretch full width and updates scrollbar visibility."""
        if self.list_frame._parent_canvas.find_all():
            self.list_frame._parent_canvas.itemconfigure(
                self.list_frame._parent_canvas.find_all(),
                width=event.width,
            )
        self._update_scrollbar()

    def _update_scrollbar(self) -> None:
        """Shows the vertical scrollbar only when tasks overflow the visible area."""
        self.update_idletasks()
        y_top, y_bottom = self.list_frame._parent_canvas.yview()

        if y_top <= 0.0 and y_bottom >= 1.0:
            self.list_frame._scrollbar.grid_remove()
        else:
            self.list_frame._scrollbar.grid()

    def _is_setup_open(self) -> bool:
        return (
            self._setup_dialog is not None
            and self._setup_dialog.winfo_exists()
            and not getattr(self._setup_dialog, "_closing", False)
        )

    def _on_alt_setup(self, _event=None) -> str:
        if self._is_setup_open():
            return "break"
        self._open_setup()
        return "break"

    def _open_setup(self) -> None:
        if self._is_setup_open():
            return
        self._setup_tooltip._hide()
        self._setup_dialog = SetupDialog(
            parent=self,
            current_header=self.header_text,
            current_theme=self.current_theme,
            confirm_delete=self.confirm_delete,
            on_save=self._apply_settings,
        )
        self.wait_window(self._setup_dialog)
        self._setup_dialog = None

    def _apply_settings(
        self, new_header: str, new_theme: str, confirm_delete: bool
    ) -> None:
        self.header_text = new_header
        self.current_theme = new_theme
        self.confirm_delete = confirm_delete

        self.db.set_setting("header_text", new_header)
        self.db.set_setting("theme", new_theme)
        self.db.set_setting("confirm_delete", "1" if confirm_delete else "0")

        self.title_label.configure(text=new_header)
        ctk.set_appearance_mode(new_theme)

    def refresh_list(self) -> None:
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        for task in self.db.get_all():
            row = TaskRow(
                master=self.list_frame,
                task=task,
                on_toggle=self.toggle_task,
                on_edit=self.edit_task,
                on_delete=self.delete_task,
            )
            row.pack(fill="x", pady=4, padx=0)

        self.after(10, self._update_scrollbar)

    def add_task(self) -> None:
        text = self.task_entry.get().strip()
        if not text:
            return
        self.db.add(text)
        self.task_entry.delete(0, "end")
        self.refresh_list()

    def toggle_task(self, task: Task) -> None:
        self.db.toggle(task.id, not task.completed)
        self.refresh_list()

    def edit_task(self, task: Task) -> None:
        dialog = EditTaskDialog(
            parent=self,
            task=task,
            on_save=self._save_edited_task,
        )
        self.wait_window(dialog)

    def _save_edited_task(self, task_id: int, new_title: str) -> None:
        self.db.update_title(task_id, new_title)
        self.refresh_list()

    def delete_task(self, task: Task) -> None:
        if not self.confirm_delete:
            self._confirm_delete_task(task.id)
            return

        dialog = ConfirmDeleteDialog(
            parent=self,
            task=task,
            on_confirm=self._confirm_delete_task,
        )
        self.wait_window(dialog)

    def _confirm_delete_task(self, task_id: int) -> None:
        self.db.delete(task_id)
        self.refresh_list()