from typing import Callable
import customtkinter as ctk
from todolist.config import COLORS
from todolist.models import Task


class TaskRow(ctk.CTkFrame):
    """Represents a single WCAG-compliant task row with check and delete actions."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        task: Task,
        on_toggle: Callable[[Task], None],
        on_delete: Callable[[int], None],
    ) -> None:
        super().__init__(master, fg_color=COLORS["row_bg"], corner_radius=8)

        font_style = ctk.CTkFont(size=14, overstrike=task.completed)
        text_color = COLORS["text_done"] if task.completed else COLORS["text_active"]

        label = ctk.CTkLabel(
            self,
            text=task.title,
            font=font_style,
            text_color=text_color,
            anchor="w",
        )
        label.pack(side="left", fill="x", expand=True, padx=12, pady=10)

        del_btn = ctk.CTkButton(
            self,
            text="✕",
            width=32,
            height=32,
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            text_color=COLORS["text_on_accent"],
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: on_delete(task.id),
        )
        del_btn.pack(side="right", padx=(4, 10))

        check_color = COLORS["success_done"] if task.completed else COLORS["success"]
        check_btn = ctk.CTkButton(
            self,
            text="✓",
            width=32,
            height=32,
            fg_color=check_color,
            hover_color=COLORS["success_hover"],
            text_color=COLORS["text_on_accent"],
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: on_toggle(task),
        )
        check_btn.pack(side="right", padx=4)
