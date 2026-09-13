"""Visual constants. Pure data — no python-pptx dependency.

Fonts are chosen for cross-platform survival: the deck is exported to Keynote
and Google Slides, neither of which can rely on macOS-only faces. Arial exists
on macOS, Windows and Google Slides, so it is never substituted.
"""

from __future__ import annotations

from dataclasses import dataclass

EMU_PER_INCH = 914400


def inches(value: float) -> int:
    return int(round(value * EMU_PER_INCH))


@dataclass(frozen=True)
class Theme:
    # Fonts
    font_latin: str = "Arial"

    # Colors (RGB hex). Taken from the supplied template: a teal-to-navy
    # gradient carrying white text, with pale cyan as the accent.
    bg_from: str = "6DBAC2"     # top-left of the gradient
    bg_to: str = "355F84"       # bottom-right, darkened for text contrast
    bg: str = "4A87A5"          # flat fallback
    text: str = "EAF4F7"        # slightly softened, so emphasis can be pure white
    accent: str = "FFFFFF"      # emphasis reads as brighter, not merely bluer
    muted: str = "C9DCE6"
    check: str = "9BE8B4"
    cross: str = "FFB4A8"
    achieved_fill: str = "2E6E6B"
    achieved_line: str = "9BE8B4"
    frontier_fill: str = "2C4F6E"
    frontier_line: str = "FFB4A8"
    rule: str = "8FB6CC"
    # Diagram box fills, all keyed to the background so white text stays legible.
    panel_fill: str = "2E5F80"      # neutral step in a process diagram
    panel_line: str = "8FB6CC"
    highlight_fill: str = "6B5426"  # the step the argument turns on
    highlight_line: str = "F2C75C"
    caution_fill: str = "5A4A2A"    # the noisy middle of the ruler
    caution_line: str = "E0B860"
    inert_fill: str = "3D4E5C"      # values that are not measurements at all
    inert_line: str = "8A9AA6"

    # Font sizes (pt)
    title_pt: int = 30
    kicker_pt: int = 14
    l0_pt: int = 19
    l1_pt: int = 16
    l2_pt: int = 14
    quote_pt: int = 21
    head_pt: int = 17
    footnote_pt: int = 10
    caveat_pt: int = 10
    page_pt: int = 10
    meta_pt: int = 14        # title-slide metadata, quote attributions
    diagram_small_pt: int = 14
    figure_caption_pt: int = 15
    column_note_pt: int = 19
    dense_l0_pt: int = 16
    dense_l1_pt: int = 14

    # Body text is scaled per slide (see fitted_scale), so a short slide fills
    # its space instead of floating in the top third. The ceiling keeps body
    # text below the title size — a body that outgrows its own heading inverts
    # the hierarchy and reads as a mistake.
    max_body_scale: float = 2.0
    max_body_pt: int = 26
    target_fill: float = 0.92

    # Limits enforced by validate.py
    min_body_pt: int = 14
    max_l0_bullets: int = 7
    max_body_lines: int = 14
    max_title_lines: int = 2
    max_footer_lines: int = 2
    quote_gap_in: float = 0.34


THEME = Theme()

# Deck geometry: 16:9 at 13.333in x 7.5in
SLIDE_W = inches(13.333)
SLIDE_H = inches(7.5)


def body_pt(level: int, theme: Theme = THEME, dense: bool = False,
            scale: float = 1.0) -> int:
    """Font size for a bullet level. Dense slides use a smaller ramp.

    `scale` is the per-slide fit factor from fitted_scale(); at 1.0 this is the
    base ramp, unchanged.
    """
    if dense:
        base = {0: theme.dense_l0_pt, 1: theme.dense_l1_pt}.get(
            level, theme.dense_l1_pt
        )
    else:
        base = {0: theme.l0_pt, 1: theme.l1_pt}.get(level, theme.l2_pt)
    fitted = int(round(base * scale))
    ceiling = theme.max_body_pt if level == 0 else theme.max_body_pt - 3
    return max(theme.min_body_pt, min(ceiling, fitted))
