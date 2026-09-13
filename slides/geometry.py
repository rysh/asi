"""Layout arithmetic in EMU. Pure functions — the single source of truth
for every coordinate in the deck."""

from __future__ import annotations

from dataclasses import dataclass

from slides.theme import SLIDE_H, SLIDE_W, inches

MARGIN_X = inches(0.62)
MARGIN_TOP = inches(0.42)
MARGIN_BOTTOM = inches(0.34)
COL_GAP = inches(0.42)


@dataclass(frozen=True)
class Rect:
    left: int
    top: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height

    def inset(self, dx: int, dy: int) -> "Rect":
        return Rect(self.left + dx, self.top + dy, self.width - 2 * dx, self.height - 2 * dy)


SLIDE_RECT = Rect(0, 0, SLIDE_W, SLIDE_H)
CONTENT_W = SLIDE_W - 2 * MARGIN_X


def title_rect() -> Rect:
    return Rect(MARGIN_X, MARGIN_TOP, CONTENT_W, inches(0.82))


def kicker_rect() -> Rect:
    return Rect(MARGIN_X, MARGIN_TOP - inches(0.24), CONTENT_W, inches(0.26))


def footer_rect() -> Rect:
    h = inches(0.44)
    return Rect(MARGIN_X, SLIDE_H - MARGIN_BOTTOM - h, CONTENT_W - inches(0.7), h)


def caveat_rect(has_footer: bool, prominent: bool = False) -> Rect:
    """The band under the body. A prominent caveat is body-sized text, so it
    needs the room two of those lines take."""
    h = inches(0.78) if prominent else inches(0.52)
    lift = inches(0.46) if has_footer else 0
    return Rect(MARGIN_X, SLIDE_H - MARGIN_BOTTOM - h - lift, CONTENT_W, h)


def page_rect() -> Rect:
    w = inches(0.6)
    h = inches(0.26)
    return Rect(SLIDE_W - MARGIN_X - w, SLIDE_H - MARGIN_BOTTOM - h, w, h)


def body_rect(has_footer: bool = True, has_caveat: bool = False) -> Rect:
    top = title_rect().bottom + inches(0.14)
    bottom = SLIDE_H - MARGIN_BOTTOM
    if has_footer:
        bottom -= inches(0.46)
    if has_caveat:
        bottom -= inches(0.54)
    return Rect(MARGIN_X, top, CONTENT_W, bottom - top)


def two_columns(rect: Rect, gap: int = COL_GAP) -> tuple[Rect, Rect]:
    w = (rect.width - gap) // 2
    return (
        Rect(rect.left, rect.top, w, rect.height),
        Rect(rect.left + w + gap, rect.top, w, rect.height),
    )


# A reference slide is scanned, not read from the back row, so it is allowed
# to run wider than the body margin and to close up the gutter. Thirteen full
# titles with DOIs do not fit two columns otherwise.
WIDE_MARGIN_X = inches(0.38)
WIDE_COL_GAP = inches(0.2)


def wide_body_rect() -> Rect:
    r = body_rect(has_footer=False, has_caveat=False)
    return Rect(WIDE_MARGIN_X, r.top, SLIDE_W - 2 * WIDE_MARGIN_X, r.height)


def column_head_and_body(col: Rect) -> tuple[Rect, Rect]:
    head_h = inches(0.36)
    return (
        Rect(col.left, col.top, col.width, head_h),
        Rect(col.left, col.top + head_h + inches(0.08), col.width, col.height - head_h - inches(0.08)),
    )


def stack(rect: Rect, count: int, gap: int) -> tuple[Rect, ...]:
    """Split a rect into `count` equal horizontal bands separated by `gap`."""
    if count <= 0:
        return ()
    band = (rect.height - gap * (count - 1)) // count
    return tuple(
        Rect(rect.left, rect.top + i * (band + gap), rect.width, band)
        for i in range(count)
    )


def title_block_rects() -> tuple[Rect, Rect, Rect]:
    """Title slide: title, author block, meta block."""
    t = Rect(MARGIN_X, inches(1.72), CONTENT_W, inches(2.05))
    a = Rect(MARGIN_X, inches(4.05), CONTENT_W, inches(1.0))
    m = Rect(MARGIN_X, inches(5.25), CONTENT_W, inches(1.5))
    return t, a, m
