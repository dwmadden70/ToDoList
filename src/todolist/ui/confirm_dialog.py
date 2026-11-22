import tkinter as tk
from typing import Callable
import customtkinter as ctk
from todolist.config import COLORS
from todolist.models import Task


class ConfirmDeleteDialog(ctk.CTkFrame):
    """In-window modal confirmation overlay locked inside parent."""

    def __init__(
        self,
        parent: ctk.CTk,
        task: Task,
        on_confirm: Callable[[int], None],
    ) -> None:
        super().__init__(parent, fg_color=COLORS["window_bg"], corner_radius=0)
        self.parent = parent
        self.task = task
        self.on_confirm = on_confirm
        self._focus_index = 0
        self._closing = False

        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.lift()

        self._build_ui()
        self._guard_widget_focus(self)
        self._configure_keyboard_navigation()

        self.grab_set()
        self.after(10, lambda: self._set_focus_index(0))

    def _guard_widget_focus(self, widget: tk.Misc) -> None:
        """Prevents CustomTkinter delayed focus_set callbacks from failing after destroy."""
        orig_focus_set = widget.focus_set

        def safe_focus_set() -> None:
            if self._closing:
                return
            try:
                if widget.winfo_exists():
                    orig_focus_set()
            except tk.TclError:
                pass

        widget.focus_set = safe_focus_set  # type: ignore[method-assign]
        for child in widget.winfo_children():
            self._guard_widget_focus(child)

    def _cleanup_and_close(self) -> None:
        if self._closing:
            return
        self._closing = True

        for seq in ("<Escape>", "<Tab>", "<Shift-Tab>", "<Left>", "<Right>", "<space>", "<Return>"):
            try:
                self.parent.unbind(seq)
            except Exception:
                pass
        try:
            self.grab_release()
        except Exception:
            pass

        self.place_forget()
        self.after(200, self._finalize_destroy)

    def _finalize_destroy(self) -> None:
        try:
            if self.winfo_exists():
                self.destroy()
        except tk.TclError:
            pass
        try:
            if self.parent.winfo_exists():
                self.parent.focus_force()
        except tk.TclError:
            pass

    def _build_ui(self) -> None:
        card = ctk.CTkFrame(
            self,
            width=360,
            fg_color=COLORS["window_bg"],
            border_width=2,
            border_color=COLORS["input_border"],
            corner_radius=12,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        container = ctk.CTkFrame(card, fg_color="transparent", width=312)
        container.pack(fill="both", expand=True, padx=24, pady=20)

        header = ctk.CTkLabel(
            container,
            text="Delete this task?",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_active"],
            anchor="w",
        )
        header.pack(fill="x", pady=(0, 8))

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

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x")

        self.delete_btn = ctk.CTkButton(
            btn_frame,
            text="Delete",
            width=90,
            height=34,
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            border_width=2,
            border_color=COLORS["danger"],
            text_color=COLORS["text_on_accent"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._confirm,
        )
        self.delete_btn.pack(side="right", padx=(8, 0))

        self.cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            width=90,
            height=34,
            fg_color=COLORS["row_bg"],
            hover_color=COLORS["input_bg"],
            border_width=2,
            border_color=COLORS["input_border"],
            text_color=COLORS["text_active"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._cancel,
        )
        self.cancel_btn.pack(side="right")

    def _configure_keyboard_navigation(self) -> None:
        self._focus_targets = [self.cancel_btn, self.delete_btn]
        for target in self._focus_targets:
            tk.Widget.configure(target, takefocus=True)

        self.parent.bind("<Escape>", lambda _: self._cancel())
        self.parent.bind("<Tab>", lambda _: self._set_focus_index(self._focus_index + 1) or "break")
        self.parent.bind("<Shift-Tab>", lambda _: self._set_focus_index(self._focus_index - 1) or "break")
        self.parent.bind("<Left>", lambda _: self._set_focus_index(0))
        self.parent.bind("<Right>", lambda _: self._set_focus_index(1))
        self.parent.bind("<space>", self._on_activate_key)
        self.parent.bind("<Return>", self._on_activate_key)

    def _set_focus_index(self, index: int) -> None:
        if self._closing or not self.winfo_exists():
            return
        self._focus_index = index % len(self._focus_targets)
        target = self._focus_targets[self._focus_index]
        if target.winfo_exists():
            target.focus_set()
        self.cancel_btn.configure(
            border_color=COLORS["text_active"] if self._focus_index == 0 else COLORS["input_border"]
        )
        self.delete_btn.configure(
            border_color=COLORS["text_active"] if self._focus_index == 1 else COLORS["danger"]
        )

    def _on_activate_key(self, _event: tk.Event | None = None) -> str:
        if self._focus_index == 1:
            self._confirm()
        else:
            self._cancel()
        return "break"

    def _confirm(self) -> None:
        if self._closing:
            return
        task_id = self.task.id
        self._cleanup_and_close()
        self.on_confirm(task_id)

    def _cancel(self) -> None:
        self._cleanup_and_close()
