"""Readability checks. Pure functions: Slide -> tuple[Violation, ...].

Text metrics are approximated without font files. The approximation is
deliberately pessimistic (it over-estimates width), so a slide that passes
here has margin to spare when a real renderer lays it out.
"""

from __future__ import annotations

from dataclasses import dataclass

from slides.geometry import (
    COL_GAP,
    Rect,
    SLIDE_RECT,
    WIDE_COL_GAP,
    body_rect,
    column_head_and_body,
    two_columns,
    wide_body_rect,
)
from slides.images import asset_path, fit, pixel_size
from slides.model import (
    Bullet,
    Bullets,
    ContactBlock,
    Diagram,
    Image,
    QuoteBlock,
    Slide,
    TitleBlock,
    TwoColumn,
    bullets_of,
)
from slides.refs import format_footer
from slides.shapes import diagram_specs
from slides.theme import SLIDE_H, THEME, Theme, body_pt, inches

# Arial advance widths average ~0.50 em over mixed-case English text, but
# Keynote lays the same string out slightly wider than LibreOffice does.
# 0.575 covers that spread; measured against Keynote output, not theory.
AVG_CHAR_EM = 0.575
LINE_SPACING = 1.22
PARA_SPACING_EM = 0.42
PT_PER_INCH = 72


@dataclass(frozen=True)
class Violation:
    slide: int
    rule: str
    detail: str


def text_width_pt(text: str, font_pt: float) -> float:
    """Pessimistic advance width of a single line."""
    return len(text) * AVG_CHAR_EM * font_pt


def wrapped_lines(text: str, font_pt: float, width_emu: int) -> int:
    """How many lines `text` needs inside `width_emu`."""
    if not text:
        return 1
    avail_pt = width_emu / inches(1) * PT_PER_INCH
    if avail_pt <= 0:
        return 1
    return max(1, -(-int(text_width_pt(text, font_pt) * 100) // max(1, int(avail_pt * 100))))


def block_height_pt(
    items: tuple[Bullet, ...], width_emu: int, theme: Theme, dense: bool,
    indent_emu: int, scale: float = 1.0
) -> float:
    total = 0.0
    for b in items:
        pt = body_pt(b.level, theme, dense, scale)
        avail = max(1, width_emu - b.level * indent_emu)
        total += wrapped_lines(b.text, pt, avail) * pt * LINE_SPACING
        total += pt * PARA_SPACING_EM
    return total


def fitted_scale(
    items: tuple[Bullet, ...], width_emu: int, height_emu: int, theme: Theme,
    dense: bool, indent_emu: int
) -> float:
    """The largest scale at which `items` still fill no more than the target
    fraction of the box.

    Text does not scale linearly — a larger font rewraps into more lines — so
    this searches rather than dividing. Bisection over a monotonic fit gives a
    stable answer in a fixed number of steps.
    """
    if not items:
        return 1.0
    budget = _emu_to_pt(height_emu) * theme.target_fill

    def fits(scale: float) -> bool:
        return block_height_pt(
            items, width_emu, theme, dense, indent_emu, scale
        ) <= budget

    if not fits(1.0):
        return 1.0  # already tight; leave the base ramp and let checks report
    lo, hi = 1.0, theme.max_body_scale
    if fits(hi):
        return hi
    for _ in range(12):
        mid = (lo + hi) / 2
        if fits(mid):
            lo = mid
        else:
            hi = mid
    return lo


def _emu_to_pt(emu: int) -> float:
    return emu / inches(1) * PT_PER_INCH


def _rects_overlap(a: Rect, b: Rect) -> bool:
    return not (
        a.right <= b.left or b.right <= a.left or a.bottom <= b.top or b.bottom <= a.top
    )


def quote_band_pt(quote: str, width_emu: int, theme: Theme) -> float:
    """Height the quote and its attribution occupy. Shared with render.py so
    the drawn layout and the checked layout are the same layout."""
    lines = wrapped_lines(quote, theme.quote_pt, width_emu - inches(0.5))
    return lines * theme.quote_pt * LINE_SPACING + theme.meta_pt * 2.6


def image_caption_pt(caption: str | None, width_emu: int, theme: Theme) -> float:
    """Height the figure caption occupies below the image, including the gap
    that separates it from the figure."""
    if not caption:
        return 0.0
    pt = theme.figure_caption_pt
    n = wrapped_lines(caption, pt, width_emu)
    return n * pt * LINE_SPACING + pt * 1.4


def _image_area(
    area: Rect,
    lead: tuple[Bullet, ...],
    caption: str | None,
    theme: Theme,
    dense: bool,
    indent: int,
) -> Rect:
    """The band a figure gets, once its lead text and caption are taken out.
    Shared with render.py so the checked layout is the drawn layout."""
    lead_h = 0
    if lead:
        lead_h = int(
            block_height_pt(lead, area.width, theme, dense, indent)
            / PT_PER_INCH * inches(1)
        ) + inches(0.12)
    cap_h = int(
        image_caption_pt(caption, area.width, theme) / PT_PER_INCH * inches(1)
    )
    return Rect(
        area.left,
        area.top + lead_h,
        area.width,
        area.height - lead_h - cap_h,
    )


def body_scale(slide: Slide, theme: Theme = THEME) -> float:
    """The per-slide body text scale. Only plain bullet bodies are scaled —
    columns, quotes and figure leads share their box with something else."""
    if not isinstance(slide.body, Bullets) or slide.dense:
        return 1.0
    area = body_rect(bool(slide.refs), slide.caveat is not None)
    return fitted_scale(
        slide.body.items, area.width, area.height, theme, slide.dense,
        inches(0.3),
    )


def check(slide: Slide, theme: Theme = THEME) -> tuple[Violation, ...]:
    out: list[Violation] = []

    def add(rule: str, detail: str) -> None:
        out.append(Violation(slide.number, rule, detail))

    body = slide.body
    has_footer = bool(slide.refs)
    has_caveat = slide.caveat is not None
    area = wide_body_rect() if slide.wide else body_rect(has_footer, has_caveat)
    gutter = WIDE_COL_GAP if slide.wide else COL_GAP
    indent = inches(0.3)

    # --- font floor -------------------------------------------------------
    scale = body_scale(slide, theme)
    for b in bullets_of(body):
        pt = body_pt(b.level, theme, slide.dense, scale)
        if pt < theme.min_body_pt:
            add("MIN_FONT", f"level {b.level} renders at {pt}pt")

    # --- title ------------------------------------------------------------
    from slides.geometry import title_rect

    if wrapped_lines(slide.title, theme.title_pt, title_rect().width) > theme.max_title_lines:
        add("TITLE_LINES", f"title exceeds {theme.max_title_lines} lines: {slide.title!r}")

    # --- bullet budget ----------------------------------------------------
    if not slide.dense:
        l0 = sum(1 for b in bullets_of(body) if b.level == 0)
        if l0 > theme.max_l0_bullets:
            add("BULLET_COUNT", f"{l0} top-level bullets (max {theme.max_l0_bullets})")

    # --- vertical fit -----------------------------------------------------
    avail_pt = _emu_to_pt(area.height)
    match body:
        case Bullets(items):
            used = block_height_pt(items, area.width, theme, slide.dense, indent,
                                   scale)
            if used > avail_pt:
                add("TEXT_OVERFLOW", f"body needs {used:.0f}pt, has {avail_pt:.0f}pt")
        case TwoColumn(_, left, _, right):
            lcol, rcol = two_columns(area, gutter)
            for name, col, items in (("left", lcol, left), ("right", rcol, right)):
                _, cbody = column_head_and_body(col)
                used = block_height_pt(items, cbody.width, theme, slide.dense,
                                       indent, scale)
                col_pt = _emu_to_pt(cbody.height)
                if used > col_pt:
                    add(
                        "TEXT_OVERFLOW",
                        f"{name} column needs {used:.0f}pt, has {col_pt:.0f}pt",
                    )
        case QuoteBlock(quote, _, lead, follow):
            # Mirrors render.py: lead, then a fixed quote band, then follow.
            # Measuring the lead is what keeps it from colliding with the quote.
            lead_pt = block_height_pt(lead, area.width, theme, slide.dense, indent)
            band = quote_band_pt(quote, area.width, theme)
            follow_pt = block_height_pt(follow, area.width, theme, slide.dense, indent)
            gap = _emu_to_pt(inches(theme.quote_gap_in)) * 2
            used = lead_pt + gap + band + follow_pt
            if used > avail_pt:
                add("TEXT_OVERFLOW", f"quote block needs {used:.0f}pt, has {avail_pt:.0f}pt")
        case Diagram(kind, _, lead):
            lead_h = 0
            if lead:
                lead_h = int(
                    block_height_pt(lead, area.width, theme, slide.dense, indent)
                    / PT_PER_INCH * inches(1)
                ) + inches(0.12)
            diagram_area = Rect(
                area.left, area.top + lead_h, area.width, area.height - lead_h
            )
            specs = diagram_specs(kind, diagram_area, theme, lead)
            for s in specs:
                r = Rect(s.left, s.top, s.width, s.height)
                if (
                    r.left < SLIDE_RECT.left
                    or r.top < SLIDE_RECT.top
                    or r.right > SLIDE_RECT.right
                    or r.bottom > SLIDE_RECT.bottom
                ):
                    add("SHAPE_BOUNDS", f"{s.tag} escapes the slide")
            boxes = [s for s in specs if s.collide]
            for i, a in enumerate(boxes):
                for b2 in boxes[i + 1 :]:
                    ra = Rect(a.left, a.top, a.width, a.height)
                    rb = Rect(b2.left, b2.top, b2.width, b2.height)
                    if _rects_overlap(ra, rb):
                        add("SHAPE_OVERLAP", f"{a.tag} overlaps {b2.tag}")
        case Image(key, caption, lead):
            path = asset_path(key)
            if path is None:
                add("IMAGE_MISSING", f"no file in assets/ for {key!r}")
            else:
                area_img = _image_area(area, lead, caption, theme, slide.dense, indent)
                if area_img.height <= 0:
                    add("IMAGE_OVERFLOW", f"{key!r} has no room left after its text")
                else:
                    placed = fit(area_img, *pixel_size(path))
                    if (
                        placed.left < SLIDE_RECT.left
                        or placed.top < SLIDE_RECT.top
                        or placed.right > SLIDE_RECT.right
                        or placed.bottom > SLIDE_RECT.bottom
                    ):
                        add("SHAPE_BOUNDS", f"figure {key!r} escapes the slide")
        case TitleBlock() | ContactBlock():
            pass

    # --- footnote ---------------------------------------------------------
    if has_footer:
        from slides.geometry import footer_rect

        text = format_footer(slide.refs)
        n = wrapped_lines(text, theme.footnote_pt, footer_rect().width)
        if n > theme.max_footer_lines:
            add("FOOTER_LINES", f"footnote wraps to {n} lines")

    if slide.caveat is not None:
        from slides.geometry import caveat_rect

        if slide.caveat_prominent:
            from slides.render import CAVEAT_PROMINENT_TOP_IN

            pt = theme.column_note_pt
            width = area.width
            height = _emu_to_pt(
                SLIDE_H - inches(CAVEAT_PROMINENT_TOP_IN) - inches(0.3)
            )
        else:
            r = caveat_rect(has_footer)
            pt, width = theme.caveat_pt, r.width
            height = _emu_to_pt(r.height)
        n = wrapped_lines(slide.caveat, pt, width)
        if n * pt * LINE_SPACING > height:
            add("CAVEAT_OVERFLOW", f"caveat wraps to {n} lines at {pt}pt")

    return tuple(out)


def check_all(slides: tuple[Slide, ...], theme: Theme = THEME) -> tuple[Violation, ...]:
    return tuple(v for s in slides for v in check(s, theme))
