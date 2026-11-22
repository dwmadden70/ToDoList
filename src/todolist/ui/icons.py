import math
from typing import Callable
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk
from todolist.config import COLORS

_ICON_CACHE: dict[str, ctk.CTkImage] = {}


def _render_pil_image(size: int, draw_fn: Callable[[ImageDraw.ImageDraw, int], None]) -> Image.Image:
    """Renders a 4x supersampled RGBA PIL image and downscales with LANCZOS."""
    scale = 4
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_fn(draw, s)
    return img.resize((size, size), Image.Resampling.LANCZOS)


def get_app_icon_photo(size: int = 64) -> ImageTk.PhotoImage:
    """Generates the app titlebar icon in memory with zero file path lookups."""

    def draw_app_icon(draw: ImageDraw.ImageDraw, s: int) -> None:
        pad = int(s * 0.05)
        radius = int(s * 0.20)
        draw.rounded_rectangle([(pad, pad), (s - pad, s - pad)], radius=radius, fill="#1e3a8a")

        stroke = max(1, int(s * 0.10))
        points = [
            (int(s * 0.26), int(s * 0.52)),
            (int(s * 0.43), int(s * 0.69)),
            (int(s * 0.74), int(s * 0.33)),
        ]
        draw.line(points, fill="#ffffff", width=stroke, joint="curve")

        start, _, end = points
        r = stroke // 2
        for x, y in (start, end):
            draw.ellipse((x - r, y - r, x + r, y + r), fill="#ffffff")

    return ImageTk.PhotoImage(_render_pil_image(size, draw_app_icon))


def _render_icon(size: int, draw_fn: Callable[[ImageDraw.ImageDraw, int], None]) -> ctk.CTkImage:
    """Renders a theme-invariant icon at 4x resolution and wraps it in a CTkImage."""
    crisp_img = _render_pil_image(size, draw_fn)
    return ctk.CTkImage(light_image=crisp_img, dark_image=crisp_img, size=(size, size))


def _render_gear_image(size: int, fill_color: str) -> Image.Image:
    """Draws an 8-tooth vector gear at 4x supersampling with a transparent center hole."""

    def draw_gear(draw: ImageDraw.ImageDraw, s: int) -> None:
        cx = cy = s / 2
        outer_r = s * 0.44
        inner_r = s * 0.32
        hole_r = s * 0.14
        tooth_half_width = s * 0.065

        for i in range(8):
            angle = math.radians(i * 45)
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            perp_x, perp_y = -sin_a * tooth_half_width, cos_a * tooth_half_width

            r_start = inner_r * 0.85
            r_end = outer_r

            p1 = (cx + cos_a * r_start - perp_x, cy + sin_a * r_start - perp_y)
            p2 = (cx + cos_a * r_end - perp_x, cy + sin_a * r_end - perp_y)
            p3 = (cx + cos_a * r_end + perp_x, cy + sin_a * r_end + perp_y)
            p4 = (cx + cos_a * r_start + perp_x, cy + sin_a * r_start + perp_y)
            draw.polygon([p1, p2, p3, p4], fill=fill_color)

        draw.ellipse(
            (cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r),
            fill=fill_color,
        )
        draw.ellipse(
            (cx - hole_r, cy - hole_r, cx + hole_r, cy + hole_r),
            fill=(0, 0, 0, 0),
        )

    return _render_pil_image(size, draw_gear)


def get_gear_icon(size: int = 16) -> ctk.CTkImage:
    """Returns a crisp, theme-aware Gear CTkImage."""
    cache_key = f"gear_{size}"
    if cache_key not in _ICON_CACHE:
        active_color = COLORS["text_active"]
        if isinstance(active_color, (tuple, list)) and len(active_color) >= 2:
            light_color, dark_color = active_color[0], active_color[1]
        else:
            light_color = dark_color = str(active_color)

        light_img = _render_gear_image(size, light_color)
        dark_img = _render_gear_image(size, dark_color)
        _ICON_CACHE[cache_key] = ctk.CTkImage(
            light_image=light_img,
            dark_image=dark_img,
            size=(size, size),
        )
    return _ICON_CACHE[cache_key]


def get_pencil_icon(size: int = 16) -> ctk.CTkImage:
    """Returns a crisp, supersampled white pencil CTkImage."""
    cache_key = f"pencil_{size}"
    if cache_key not in _ICON_CACHE:

        def draw_pencil(draw: ImageDraw.ImageDraw, s: int) -> None:
            body = [
                (int(s * 0.22), int(s * 0.64)),
                (int(s * 0.64), int(s * 0.22)),
                (int(s * 0.78), int(s * 0.36)),
                (int(s * 0.36), int(s * 0.78)),
            ]
            draw.polygon(body, fill="#ffffff")

            eraser = [
                (int(s * 0.68), int(s * 0.18)),
                (int(s * 0.76), int(s * 0.10)),
                (int(s * 0.90), int(s * 0.24)),
                (int(s * 0.82), int(s * 0.32)),
            ]
            draw.polygon(eraser, fill="#ffffff")

            tip = [
                (int(s * 0.20), int(s * 0.68)),
                (int(s * 0.32), int(s * 0.80)),
                (int(s * 0.10), int(s * 0.90)),
            ]
            draw.polygon(tip, fill="#ffffff")

        _ICON_CACHE[cache_key] = _render_icon(size, draw_pencil)
    return _ICON_CACHE[cache_key]


def get_check_icon(size: int = 16) -> ctk.CTkImage:
    """Returns a crisp, supersampled white checkmark CTkImage."""
    cache_key = f"check_{size}"
    if cache_key not in _ICON_CACHE:

        def draw_check(draw: ImageDraw.ImageDraw, s: int) -> None:
            stroke = max(1, int(s * 0.14))
            points = [
                (int(s * 0.18), int(s * 0.52)),
                (int(s * 0.40), int(s * 0.74)),
                (int(s * 0.82), int(s * 0.26)),
            ]
            draw.line(points, fill="#ffffff", width=stroke, joint="curve")

            start, _, end = points
            r = stroke // 2
            for x, y in (start, end):
                draw.ellipse((x - r, y - r, x + r, y + r), fill="#ffffff")

        _ICON_CACHE[cache_key] = _render_icon(size, draw_check)
    return _ICON_CACHE[cache_key]


def get_close_icon(size: int = 16) -> ctk.CTkImage:
    """Returns a crisp, supersampled white X (delete) CTkImage."""
    cache_key = f"close_{size}"
    if cache_key not in _ICON_CACHE:

        def draw_close(draw: ImageDraw.ImageDraw, s: int) -> None:
            stroke = max(1, int(s * 0.14))
            pad = int(s * 0.24)
            end = s - pad
            p1, p2 = (pad, pad), (end, end)
            p3, p4 = (end, pad), (pad, end)

            draw.line([p1, p2], fill="#ffffff", width=stroke)
            draw.line([p3, p4], fill="#ffffff", width=stroke)

            r = stroke // 2
            for x, y in (p1, p2, p3, p4):
                draw.ellipse((x - r, y - r, x + r, y + r), fill="#ffffff")

        _ICON_CACHE[cache_key] = _render_icon(size, draw_close)
    return _ICON_CACHE[cache_key]
