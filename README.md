# To-Do List

A lightweight, accessible cross-platform desktop to-do list application built with Python, CustomTkinter, and SQLite.

## Features

- **Cross-Platform Desktop UI:** Runs natively on Windows, macOS, and Linux using CustomTkinter.
- **WCAG High-Contrast Palette:** Minimum 8.0:1 contrast ratios across Light and Dark appearance themes.
- **Full Keyboard Navigation:** Open settings with `Alt+S` and navigate modal dialogs with `Tab`, `Shift+Tab`, arrow keys, `Space`, `Enter`, and `Esc`.
- **In-Window Modal Overlays:** Setup, Edit, and Delete confirmation dialogs remain locked inside the main application window.
- **Persistent Local Storage:** Automatically saves tasks and preferences to `~/.todolist.db` using SQLite with WAL mode and restrictive user-only file permissions.
- **Standalone Packaging:** Includes `build.py` and GitHub Actions CI/CD workflows to build standalone executables for Windows, macOS, and Linux.

---

## Project Structure

```text
todolist/
├── .github/
│   └── workflows/
│       └── test.yml            # GitHub Actions CI tests & multi-OS release builds
├── build.py                    # Local & CI PyInstaller executable builder
├── pyproject.toml              # Package metadata and dependencies
├── README.md
├── src/
│   └── todolist/
│       ├── __init__.py
│       ├── __main__.py         # Application entry point
│       ├── config.py           # Window bounds, validation constants, and theme colors
│       ├── database.py         # SQLite persistence layer
│       ├── models.py           # Task data model
│       └── ui/
│           ├── __init__.py
│           ├── app.py          # Main window orchestration and global shortcuts
│           ├── components.py   # TaskRow widget and screen-clamped hover tooltips
│           ├── confirm_dialog.py
│           ├── edit_dialog.py
│           ├── icons.py        # Supersampled in-memory PIL/CTkImage icons
│           └── setup_dialog.py # In-window modal settings overlay
└── tests/
    ├── test_database.py        # Database unit & edge-case tests
    └── test_ui.py              # End-to-end UI & keyboard shortcut tests
```

---

## Installation & Running Locally

### Prerequisites
- **Python 3.10+**
- On Linux, ensure Tkinter is installed (`sudo apt-get install python3-tk`).

### Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd todolist

# Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install the package with development tools (pytest, pyinstaller)
pip install -e ".[dev]"
```

### Launch the App

```bash
todolist
```

Or run via module:

```bash
python -m todolist
```

---

## Keyboard Shortcuts

| Context | Shortcut | Action |
| :--- | :--- | :--- |
| **Main Window** | `Enter` (in task input) | Add a new task |
| **Main Window** | `Alt+S` | Open the Setup modal overlay |
| **Modal Overlays** | `Tab` / `Shift+Tab` | Move focus forward / backward between controls |
| **Setup Theme Selector** | `Left` / `Right` / `Space` | Switch between Light and Dark themes |
| **Confirm Switch** | `Space` / `Enter` | Toggle delete confirmation on or off |
| **Modal Overlays** | `Enter` | Save / Confirm action |
| **Modal Overlays** | `Esc` | Cancel and close overlay |

---

## Running Tests

Run the full test suite (`tests/test_database.py` and `tests/test_ui.py`) with `pytest`:

```bash
pytest -v
```

On headless Linux servers without an active display:

```bash
xvfb-run --auto-servernum --server-args="-screen 0 1280x800x24" pytest -v
```

---

## Building Standalone Executables

To generate platform icons and package a standalone executable locally using PyInstaller:

```bash
python build.py
```

Outputs are written to:
- **Windows:** `dist/windows/ToDoList.exe` (also generates `dist/build_windows.bat` for double-click rebuilds)
- **macOS:** `dist/macos/ToDoList.app`
- **Linux:** `dist/linux/ToDoList`

### Automated GitHub Releases

Pushing a semantic version tag triggers `.github/workflows/test.yml` to run all tests and publish Windows, macOS, and Linux binaries to a GitHub Release:

```bash
git tag v0.1.0
git push origin v0.1.0
```
