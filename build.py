import platform
import shutil
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw


def generate_icons(assets_dir: Path) -> dict[str, Path]:
    """Generates app icons for Windows (.ico), macOS (.icns), and Linux (.png)."""
    assets_dir.mkdir(parents=True, exist_ok=True)

    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # WCAG AAA deep blue rounded background (#1e3a8a)
    draw.rounded_rectangle([(12, 12), (size - 12, size - 12)], radius=52, fill="#1e3a8a")

    # Crisp white checkmark (#ffffff)
    checkmark_points = [(68, 134), (110, 176), (190, 84)]
    draw.line(checkmark_points, fill="#ffffff", width=26, joint="curve")

    ico_path = assets_dir / "icon.ico"
    icns_path = assets_dir / "icon.icns"
    png_path = assets_dir / "icon.png"

    img.save(
        ico_path,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    img.save(icns_path, format="ICNS")
    img.save(png_path, format="PNG")

    return {"windows": ico_path, "darwin": icns_path, "linux": png_path}


def main() -> None:
    root_dir = Path(__file__).resolve().parent
    entry_script = root_dir / "src" / "todolist" / "__main__.py"
    dist_root = root_dir / "dist"
    work_dir = root_dir / "build"
    assets_dir = root_dir / "assets"

    icons = generate_icons(assets_dir)

    for subfolder in ("windows", "macos", "linux"):
        (dist_root / subfolder).mkdir(parents=True, exist_ok=True)

    bat_file = dist_root / "build_windows.bat"
    bat_file.write_text(
        "@echo off\r\n"
        'cd /d "%~dp0.."\r\n'
        'if exist ".venv\\Scripts\\python.exe" (\r\n'
        '    ".venv\\Scripts\\python.exe" build.py\r\n'
        ") else (\r\n"
        "    python build.py\r\n"
        ")\r\n"
        "pause\r\n",
        encoding="utf-8",
    )

    system = platform.system().lower()
    if system == "windows":
        target_dir = dist_root / "windows"
    elif system == "darwin":
        target_dir = dist_root / "macos"
    elif system == "linux":
        target_dir = dist_root / "linux"
    else:
        raise RuntimeError(f"Unsupported operating system: {system}")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--onefile",
        "--name",
        "ToDoList",
        "--icon",
        str(icons[system]),
        "--collect-all",
        "customtkinter",
        "--distpath",
        str(target_dir),
        "--workpath",
        str(work_dir),
        "--specpath",
        str(work_dir),
        str(entry_script),
    ]

    print(f"Building ToDoList for {system} -> {target_dir} ...")
    subprocess.run(cmd, check=True)

    if work_dir.exists():
        shutil.rmtree(work_dir, ignore_errors=True)

    print(f"\nDone! Output saved in: {target_dir}")


if __name__ == "__main__":
    main()
