from typing import Callable
import customtkinter as ctk
from todolist.config import APP_NAME, COLORS


class SetupDialog(ctk.CTkToplevel):
    """Modal setup dialog that blocks parent interaction until Save or Cancel."""

    def __init__(
        self,
        parent: ctk.CTk,
        current_header: str,
        current_theme: str,
        on_save: Callable[[str, str], None],
    ) -> None:
        super().__init__(parent, fg_color=COLORS["window_bg"])
        self.on_save = on_save
        self._current_header = current_header
        self._selected_theme = current_theme.capitalize()

        self.title("Setup")
        self.resizable(False, False)

        # Make modal: tie to parent, lock focus, and block parent clicks
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._center_over_parent(parent)

        # Ensure closing via window 'X' or Escape acts like Cancel
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.bind("<Escape>", lambda _: self._cancel())
        self.bind("<Return>", lambda _: self._save())

    def _center_over_parent(self, parent: ctk.CTk) -> None:
        self.update_idletasks()
        width, height = 340, 275
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")

    def _build_ui(self) -> None:
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=20)

        # Custom Header Text Section
        header_lbl = ctk.CTkLabel(
            container,
            text="List Header",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_active"],
            anchor="w",
        )
        header_lbl.pack(fill="x", pady=(0, 6))

        self.header_entry = ctk.CTkEntry(
            container,
            placeholder_text=APP_NAME,
            height=36,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["input_border"],
            text_color=COLORS["text_active"],
            placeholder_text_color=COLORS["text_done"],
            font=ctk.CTkFont(size=14),
        )
        self.header_entry.insert(0, self._current_header)
        self.header_entry.pack(fill="x", pady=(0, 16))

        # Appearance Theme Section
        theme_lbl = ctk.CTkLabel(
            container,
            text="Appearance Theme",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_active"],
            anchor="w",
        )
        theme_lbl.pack(fill="x", pady=(0, 6))

        self.theme_selector = ctk.CTkSegmentedButton(
            container,
            values=["Light", "Dark"],
            height=32,
            command=self._on_theme_select,
            fg_color=COLORS["row_bg"],
            selected_color=COLORS["primary"],
            selected_hover_color=COLORS["primary_hover"],
            unselected_color=COLORS["row_bg"],
            unselected_hover_color=COLORS["input_bg"],
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.theme_selector.set(self._selected_theme)
        self.theme_selector.pack(fill="x", pady=(0, 22))
        self._update_selector_contrast(self._selected_theme)

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

    def _on_theme_select(self, choice: str) -> None:
        self._selected_theme = choice
        self._update_selector_contrast(choice)

    def _update_selector_contrast(self, selected_choice: str) -> None:
        """Maintains >= 8.0:1 WCAG contrast on both active and inactive segments."""
        for value, button in self.theme_selector._buttons_dict.items():
            if value == selected_choice:
                button.configure(text_color=COLORS["text_on_accent"])
            else:
                button.configure(text_color=COLORS["text_active"])

    def _save(self) -> None:
        new_header = self.header_entry.get().strip() or APP_NAME
        self.on_save(new_header, self._selected_theme.lower())
        self.grab_release()
        self.destroy()

    def _cancel(self) -> None:
        self.grab_release()
        self.destroy()
