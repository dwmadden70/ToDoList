from typing import Callable
import customtkinter as ctk
from todolist.config import COLORS
from todolist.models import Task


class EditTaskDialog(ctk.CTkToplevel):
    """Modal dialog for editing an existing task's text."""

    def __init__(
        self,
        parent: ctk.CTk,
        task: Task,
        on_save: Callable[[int, str], None],
    ) -> None:
        super().__init__(parent, fg_color=COLORS["window_bg"])
        self.task = task
        self.on_save = on_save

        self.title("Edit Task")
        self.resizable(False, False)

        # Make modal: tie to parent, lock focus, and block parent clicks
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._center_over_parent(parent)

        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.bind("<Escape>", lambda _: self._cancel())
        self.bind("<Return>", lambda _: self._save())

    def _center_over_parent(self, parent: ctk.CTk) -> None:
        self.update_idletasks()
        width, height = 360, 185
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")

    def _build_ui(self) -> None:
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=20)

        lbl = ctk.CTkLabel(
            container,
            text="Task Description",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_active"],
            anchor="w",
        )
        lbl.pack(fill="x", pady=(0, 8))

        self.task_entry = ctk.CTkEntry(
            container,
            height=38,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["input_border"],
            text_color=COLORS["text_active"],
            font=ctk.CTkFont(size=14),
        )
        self.task_entry.insert(0, self.task.title)
        self.task_entry.pack(fill="x", pady=(0, 20))
        self.task_entry.focus_set()
        self.task_entry.select_range(0, "end")

        # Action buttons (Save / Cancel)
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom")

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save",
            width=90,
            height=34,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color=COLORS["text_on_accent"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._save,
        )
        save_btn.pack(side="right", padx=(8, 0))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            width=90,
            height=34,
            fg_color=COLORS["row_bg"],
            hover_color=COLORS["input_bg"],
            border_width=1,
            border_color=COLORS["input_border"],
            text_color=COLORS["text_active"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._cancel,
        )
        cancel_btn.pack(side="right")

    def _save(self) -> None:
        updated_text = self.task_entry.get().strip()
        if not updated_text:
            return
        self.on_save(self.task.id, updated_text)
        self.grab_release()
        self.destroy()

    def _cancel(self) -> None:
        self.grab_release()
        self.destroy()
