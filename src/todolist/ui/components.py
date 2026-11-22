import tkinter as tk
from typing import Callable
import customtkinter as ctk
from todolist.config import COLORS
from todolist.models import Task
from todolist.ui.icons import get_check_icon, get_close_icon, get_pencil_icon


class Tooltip:
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

    def _schedule(self, _event: tk.Event | None = None) -> None:
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

        self._tip_win = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_attributes("-topmost", True)

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
            font=("TkDefaultFont", 9),
        )
        lbl.pack()

        tw.update_idletasks()
        tip_width = tw.winfo_reqwidth()
        screen_width = self.widget.winfo_screenwidth()

        raw_x = self.widget.winfo_rootx() + (self.widget.winfo_width() // 2) - (tip_width // 2)
        clamped_x = max(4, min(raw_x, screen_width - tip_width - 4))
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        tw.wm_geometry(f"+{clamped_x}+{max(0, y)}")

    def hide(self, _event: tk.Event | None = None) -> None:
        self._cancel()
        if self._tip_win is not None:
            try:
                self._tip_win.destroy()
            except tk.TclError:
                pass
            self._tip_win = None

    _hide = hide


class TaskRow(ctk.CTkFrame):
    """Represents a single WCAG-compliant task row with edit, check, and delete actions."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        task: Task,
        on_toggle: Callable[[Task], None],
        on_edit: Callable[[Task], None],
        on_delete: Callable[[Task], None],
    ) -> None:
        super().__init__(master, fg_color=COLORS["row_bg"], corner_radius=8)

        font_style = ctk.CTkFont(size=14, overstrike=task.completed)
        text_color = COLORS["text_done"] if task.completed else COLORS["text_active"]

        self.label = ctk.CTkLabel(
            self,
            text=task.title,
            font=font_style,
            text_color=text_color,
            anchor="w",
            justify="left",
            wraplength=260,
        )
        self.label.pack(side="left", fill="x", expand=True, padx=12, pady=10)

        # 1. Delete button (Rightmost)
        del_btn = ctk.CTkButton(
            self,
            text="",
            image=get_close_icon(15),
            width=32,
            height=32,
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            command=lambda: on_delete(task),
        )
        del_btn.pack(side="right", padx=(4, 10))
        self._del_tip = Tooltip(del_btn, "Delete")

        # 2. Check button (Middle)
        check_color = COLORS["success_done"] if task.completed else COLORS["success"]
        check_btn = ctk.CTkButton(
            self,
            text="",
            image=get_check_icon(16),
            width=32,
            height=32,
            fg_color=check_color,
            hover_color=COLORS["success_hover"],
            command=lambda: on_toggle(task),
        )
        check_btn.pack(side="right", padx=4)
        self._check_tip = Tooltip(
            check_btn, "Mark incomplete" if task.completed else "Mark complete"
        )

        # 3. Edit button (Leftmost of the action icons)
        edit_btn = ctk.CTkButton(
            self,
            text="",
            image=get_pencil_icon(16),
            width=32,
            height=32,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=lambda: on_edit(task),
        )
        edit_btn.pack(side="right", padx=4)
        self._edit_tip = Tooltip(edit_btn, "Edit")

        self.bind("<Configure>", self._on_resize, add="+")

    def _on_resize(self, event: tk.Event) -> None:
        """Adjusts label wraplength dynamically so action buttons never clip off-screen."""
        available = max(120, event.width - 155)
        self.label.configure(wraplength=available)
