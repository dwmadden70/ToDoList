import tkinter as tk
from typing import Callable
import customtkinter as ctk
from todolist.config import APP_NAME, COLORS


class SetupDialog(ctk.CTkFrame):
    """In-window modal setup overlay locked inside parent with WCAG-compliant contrast."""

    def __init__(
        self,
        parent: ctk.CTk,
        current_header: str,
        current_theme: str,
        confirm_delete: bool,
        on_save: Callable[[str, str, bool], None],
    ) -> None:
        super().__init__(parent, fg_color=COLORS["window_bg"], corner_radius=0)
        self.parent = parent
        self.on_save = on_save
        self._current_header = current_header
        self._initial_theme = current_theme.capitalize()
        self._selected_theme = self._initial_theme
        self._confirm_delete = confirm_delete
        self._focus_index = 0
        self._closing = False

        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.lift()

        self._build_ui()
        self._guard_widget_focus(self)
        self._configure_keyboard_navigation()

        self._escape_bind_id = parent.bind("<Escape>", lambda _: self._cancel(), add="+")
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

        if hasattr(self, "_escape_bind_id"):
            try:
                self.parent.unbind("<Escape>", self._escape_bind_id)
            except Exception:
                pass
        for seq in ("<Tab>", "<Shift-Tab>", "<Left>", "<Right>", "<space>", "<Return>"):
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

        title_lbl = ctk.CTkLabel(
            container, text="Setup", font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_active"], anchor="w",
        )
        title_lbl.pack(fill="x", pady=(0, 12))

        header_lbl = ctk.CTkLabel(
            container, text="List Header", font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_active"], anchor="w",
        )
        header_lbl.pack(fill="x", pady=(0, 4))

        self.header_entry = ctk.CTkEntry(
            container, placeholder_text=APP_NAME, height=36, width=312,
            fg_color=COLORS["input_bg"], border_color=COLORS["input_border"],
            text_color=COLORS["text_active"], placeholder_text_color=COLORS["text_done"],
            font=ctk.CTkFont(size=14),
        )
        self.header_entry.insert(0, self._current_header)
        self.header_entry.pack(fill="x", pady=(0, 14))

        theme_lbl = ctk.CTkLabel(
            container, text="Appearance Theme", font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_active"], anchor="w",
        )
        theme_lbl.pack(fill="x", pady=(0, 4))

        self.theme_selector = ctk.CTkSegmentedButton(
            container, values=["Light", "Dark"], height=32, command=self._on_theme_select,
            fg_color=COLORS["row_bg"], selected_color=COLORS["primary"],
            selected_hover_color=COLORS["primary_hover"], unselected_color=COLORS["row_bg"],
            unselected_hover_color=COLORS["input_bg"], font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.theme_selector.set(self._selected_theme)
        self.theme_selector.pack(fill="x", pady=(0, 16))
        self._update_selector_contrast(self._selected_theme)

        self.confirm_var = ctk.BooleanVar(value=self._confirm_delete)
        self.confirm_switch = ctk.CTkSwitch(
            container, text="Confirm before deleting items", variable=self.confirm_var,
            onvalue=True, offvalue=False, command=self._update_switch_contrast,
            text_color=COLORS["text_active"], font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.confirm_switch.pack(fill="x", pady=(0, 20))
        self._update_switch_contrast()

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(4, 0))

        self.save_btn = ctk.CTkButton(
            btn_frame, text="Save", width=90, height=34, fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"], border_width=2, border_color=COLORS["primary"],
            text_color=COLORS["text_on_accent"], font=ctk.CTkFont(size=13, weight="bold"),
            command=self._save,
        )
        self.save_btn.pack(side="right", padx=(8, 0))

        self.cancel_btn = ctk.CTkButton(
            btn_frame, text="Cancel", width=90, height=34, fg_color=COLORS["row_bg"],
            hover_color=COLORS["input_bg"], border_width=2, border_color=COLORS["input_border"],
            text_color=COLORS["text_active"], font=ctk.CTkFont(size=13, weight="bold"),
            command=self._cancel,
        )
        self.cancel_btn.pack(side="right")

    def _update_switch_contrast(self) -> None:
        if self._initial_theme == "Light":
            self.confirm_switch.configure(
                fg_color=COLORS["row_bg"],
                progress_color=COLORS["row_bg"],
                border_color=COLORS["input_border"],
                border_width=2,
                button_color=COLORS["primary"],
                button_hover_color=COLORS["primary_hover"],
                text_color=COLORS["text_active"],
            )
        else:
            self.confirm_switch.configure(
                fg_color=COLORS["primary"],
                progress_color=COLORS["primary"],
                border_color=COLORS["primary"],
                border_width=2,
                button_color=COLORS["text_on_accent"],
                button_hover_color=COLORS["text_on_accent"],
                text_color=COLORS["text_active"],
            )

    def _configure_keyboard_navigation(self) -> None:
        entry_target = self.header_entry._entry
        self._focus_targets = [
            entry_target, self.theme_selector, self.confirm_switch, self.cancel_btn, self.save_btn
        ]
        for target in self._focus_targets:
            tk.Widget.configure(target, takefocus=True)

        self.parent.bind("<Tab>", lambda _: self._set_focus_index(self._focus_index + 1) or "break")
        self.parent.bind("<Shift-Tab>", lambda _: self._set_focus_index(self._focus_index - 1) or "break")

        entry_target.bind("<Button-1>", lambda _: self._set_focus_index(0), add="+")
        self.confirm_switch._canvas.bind("<Button-1>", lambda _: self._set_focus_index(2), add="+")
        self.cancel_btn._canvas.bind("<Button-1>", lambda _: self._set_focus_index(3), add="+")
        self.save_btn._canvas.bind("<Button-1>", lambda _: self._set_focus_index(4), add="+")

        self.parent.bind("<Left>", lambda _: self._set_theme("Light") if self._focus_index == 1 else None)
        self.parent.bind("<Right>", lambda _: self._set_theme("Dark") if self._focus_index == 1 else None)
        self.parent.bind("<space>", self._on_space_key)
        self.parent.bind("<Return>", self._on_return_key)

    def _set_focus_index(self, index: int) -> None:
        if self._closing or not self.winfo_exists():
            return
        self._focus_index = index % len(self._focus_targets)
        target = self._focus_targets[self._focus_index]
        if target.winfo_exists():
            target.focus_set()
        self._update_focus_visuals()

    def _update_focus_visuals(self) -> None:
        if self._closing or not self.winfo_exists():
            return
        self.header_entry.configure(border_color=COLORS["input_border"])
        self.theme_selector.configure(fg_color=COLORS["row_bg"])
        self.confirm_switch.configure(text_color=COLORS["text_active"])
        self.cancel_btn.configure(border_color=COLORS["input_border"])
        self.save_btn.configure(border_color=COLORS["primary"])

        if self._focus_index == 0:
            self.header_entry.configure(border_color=COLORS["text_active"])
        elif self._focus_index == 1:
            self.theme_selector.configure(fg_color=COLORS["input_border"])
        elif self._focus_index == 2:
            if self._initial_theme == "Light":
                self.confirm_switch.configure(text_color=COLORS["primary"])
            else:
                self.confirm_switch.configure(text_color=COLORS["text_active"])
        elif self._focus_index == 3:
            self.cancel_btn.configure(border_color=COLORS["text_active"])
        elif self._focus_index == 4:
            self.save_btn.configure(border_color=COLORS["text_active"])

    def _toggle_confirm_switch(self) -> None:
        self.confirm_var.set(not self.confirm_var.get())
        self._update_switch_contrast()

    def _on_space_key(self, _event=None) -> str | None:
        if self._focus_index == 0:
            return None
        if self._focus_index == 1:
            self._set_theme("Dark" if self._selected_theme == "Light" else "Light")
        elif self._focus_index == 2:
            self._toggle_confirm_switch()
        elif self._focus_index == 3:
            self._cancel()
        elif self._focus_index == 4:
            self._save()
        return "break"

    def _on_return_key(self, _event=None) -> str:
        if self._focus_index == 1:
            self._set_theme("Dark" if self._selected_theme == "Light" else "Light")
        elif self._focus_index == 2:
            self._toggle_confirm_switch()
        elif self._focus_index == 3:
            self._cancel()
        else:
            self._save()
        return "break"

    def _set_theme(self, choice: str) -> None:
        self.theme_selector.set(choice)
        self._on_theme_select(choice)

    def _on_theme_select(self, choice: str) -> None:
        self._selected_theme = choice
        self._update_selector_contrast(choice)

    def _update_selector_contrast(self, selected_choice: str) -> None:
        for value, button in self.theme_selector._buttons_dict.items():
            if value == selected_choice:
                button.configure(text_color=COLORS["text_on_accent"])
            else:
                button.configure(text_color=COLORS["text_active"])

    def _save(self) -> None:
        if self._closing:
            return
        new_header = self.header_entry.get().strip() or APP_NAME
        selected_theme = self._selected_theme.lower()
        confirm_delete = self.confirm_var.get()
        self._cleanup_and_close()
        self.on_save(new_header, selected_theme, confirm_delete)

    def _cancel(self) -> None:
        self._cleanup_and_close()
