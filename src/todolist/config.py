from pathlib import Path

APP_NAME = "To-Do List"
MIN_WIDTH = 440
MIN_HEIGHT = 560
MAX_WIDTH = 800
WINDOW_SIZE = f"{MIN_WIDTH}x{MIN_HEIGHT}"
DEFAULT_THEME = "light"
VALID_THEMES = ("light", "dark")

MAX_TASK_LENGTH = 500
MAX_HEADER_LENGTH = 100

# Cross-platform storage path in the user's home directory
DB_PATH = Path.home() / ".todolist.db"

# Strict High-Contrast Color Palette (Minimum 8.0:1 Contrast Ratio Across All States)
COLORS = {
    "window_bg": ("#ffffff", "#0f172a"),
    "row_bg": ("#e2e8f0", "#1e293b"),
    "input_bg": ("#f8fafc", "#1e293b"),
    "input_border": ("#334155", "#cbd5e1"),
    "text_active": ("#0f172a", "#f8fafc"),
    "text_done": ("#1e293b", "#cbd5e1"),
    "text_on_accent": ("#ffffff", "#ffffff"),
    "primary": ("#1e3a8a", "#1e3a8a"),
    "primary_hover": ("#172554", "#1e40af"),
    "success": ("#14532d", "#14532d"),
    "success_done": ("#052e16", "#052e16"),
    "success_hover": ("#052e16", "#155b32"),
    "danger": ("#7f1d1d", "#7f1d1d"),
    "danger_hover": ("#450a0a", "#991b1b"),
}
