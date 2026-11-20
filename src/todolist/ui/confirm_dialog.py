from typing import Callable
import customtkinter as ctk
from todolist.config import COLORS
from todolist.models import Task


class ConfirmDeleteDialog(ctk.CTkToplevel):
    """Modal confirmation dialog before permanently deleting a task."""

    def __init__(
        self,
        parent: ctk.CTk,
        task: Task,
        on_confirm: Callable[[int], None],
    ) -> None:
        super().__init__(parent, fg_color=COLORS["window_bg"])
        self.task = task
        self.on_confirm = on_confirm

        self.title("Confirm Delete")
        self.resizable(False, False)

        # Make modal: tie to parent, lock focus, and block parent clicks
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._center_over_parent(parent)

        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.bind("<Escape>", lambda _: self._cancel())
        self.bind("<Return>", lambda _: self._confirm())

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

        header = ctk.CTkLabel(
            container,
            text="Delete this task?",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLORS["text_active"],
            anchor="w",
        )
        header.pack(fill="x", pady=(0, 8))

        # Show truncated task title so user knows exactly what will be deleted
        preview_title = (
            f'"{self.task.title[:45]}..."'
            if len(self.task.title) > 45
            else f'"{self.task.title}"'
        )
        msg_lbl = ctk.CTkLabel(
            container,
            text=preview_title,
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_done"],
            anchor="w",
            wraplength=310,
            justify="left",
        )
        msg_lbl.pack(fill="x", pady=(0, 20))

        # Action buttons (Delete / Cancel)
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom")

        delete_btn = ctk.CTkButton(
            btn_frame,
            text="Delete",
            width=90,
            height=34,
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            text_color=COLORS["text_on_accent"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._confirm,
        )
        delete_btn.pack(side="right", padx=(8, 0))

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
        cancel_btn.focus_set()

    def _confirm(self) -> None:
        self.on_confirm(self.task.id)
        self.grab_release()
        self.destroy()

    def _cancel(self) -> None:
        self.grab_release()
        self.destroy()
