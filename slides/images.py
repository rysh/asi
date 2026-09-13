"""Figure placement. Pure functions over the files in assets/.

The fit is computed here rather than in render.py so that validate.py can
check where a figure lands without importing python-pptx — the same rule the
diagrams follow.
"""

from __future__ import annotations

import struct
from pathlib import Path

from slides.geometry import Rect

ASSETS = Path(__file__).parent.parent / "assets"
SUFFIXES = (".png", ".jpg", ".jpeg")


def asset_path(key: str) -> Path | None:
    """The file backing `key`, or None if the figure has not been supplied."""
    for suffix in SUFFIXES:
        candidate = ASSETS / f"{key}{suffix}"
        if candidate.exists():
            return candidate
    return None


def pixel_size(path: Path) -> tuple[int, int]:
    """(width, height) in pixels, read from the file header.

    Only PNG and JPEG are read, and only far enough to find the dimensions —
    the deck needs the aspect ratio, not the image.
    """
    data = path.read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        width, height = struct.unpack(">II", data[16:24])
        return int(width), int(height)
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            # SOF0-SOF15, excluding the non-frame markers DHT/JPG/DAC.
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                height, width = struct.unpack(">HH", data[i + 5 : i + 9])
                return int(width), int(height)
            i += 2 + struct.unpack(">H", data[i + 2 : i + 4])[0]
        raise ValueError(f"no JPEG frame header in {path}")
    raise ValueError(f"unsupported image format: {path}")


def fit(rect: Rect, px_w: int, px_h: int) -> Rect:
    """The largest rect with the figure's aspect ratio that fits in `rect`,
    centred both ways."""
    if px_w <= 0 or px_h <= 0:
        raise ValueError(f"degenerate image size: {px_w}x{px_h}")
    scale = min(rect.width / px_w, rect.height / px_h)
    w = int(px_w * scale)
    h = int(px_h * scale)
    return Rect(
        rect.left + (rect.width - w) // 2,
        rect.top + (rect.height - h) // 2,
        w,
        h,
    )


def placement(key: str, rect: Rect) -> tuple[Path, Rect]:
    """Resolve a figure and where it goes. Raises if it has not been supplied."""
    path = asset_path(key)
    if path is None:
        raise FileNotFoundError(key)
    return path, fit(rect, *pixel_size(path))
