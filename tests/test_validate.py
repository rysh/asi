"""Readability rules. These encode what a slide must satisfy to be legible
from the back of a lecture hall — not how the checker happens to work."""

import pytest

from slides.geometry import Rect, body_rect
from slides.model import (
    Bullet,
    Bullets,
    Diagram,
    DiagramKind,
    Slide,
    TwoColumn,
)
from slides.shapes import diagram_specs
from slides.theme import THEME
from slides.validate import check, text_width_pt, wrapped_lines


def rules(slide) -> set[str]:
    return {v.rule for v in check(slide)}


# --- metric sanity --------------------------------------------------------

def test_width_grows_with_text_length():
    assert text_width_pt("aaaa", 20) > text_width_pt("aa", 20)


def test_width_grows_with_font_size():
    assert text_width_pt("hello", 30) > text_width_pt("hello", 15)


def test_estimate_is_pessimistic_for_arial():
    """Arial averages ~0.50em; the estimate must not undershoot that."""
    assert text_width_pt("x" * 100, 10) >= 0.50 * 100 * 10


def test_wrapping_counts_more_lines_for_longer_text():
    w = body_rect().width
    assert wrapped_lines("word " * 200, 20, w) > wrapped_lines("word", 20, w)


# --- font floor -----------------------------------------------------------

def test_body_text_never_below_14pt():
    slide = Slide(1, "T", Bullets((Bullet("x", 2),)), 60)
    assert "MIN_FONT" not in rules(slide)  # l2 is exactly 14pt


def test_dense_slides_still_respect_the_floor():
    slide = Slide(2, "T", Bullets((Bullet("x", 1),)), 60, dense=True)
    assert "MIN_FONT" not in rules(slide)


# --- budgets --------------------------------------------------------------

def test_too_many_top_level_bullets_is_flagged():
    items = tuple(Bullet(f"item {i}") for i in range(9))
    assert "BULLET_COUNT" in rules(Slide(1, "T", Bullets(items), 60))


def test_dense_slides_are_exempt_from_the_bullet_count():
    items = tuple(Bullet(f"item {i}") for i in range(14))
    assert "BULLET_COUNT" not in rules(Slide(2, "T", Bullets(items), 60, dense=True))


def test_overlong_body_is_flagged():
    items = tuple(Bullet("a rather long line of text " * 6) for _ in range(12))
    assert "TEXT_OVERFLOW" in rules(Slide(1, "T", Bullets(items), 60))


def test_reasonable_body_passes():
    items = tuple(Bullet(f"a concise point number {i}") for i in range(5))
    assert check(Slide(1, "A short title", Bullets(items), 60)) == ()


def test_overlong_title_is_flagged():
    assert "TITLE_LINES" in rules(Slide(1, "Title " * 40, Bullets(()), 60))


def test_column_overflow_is_flagged():
    heavy = tuple(Bullet("long text " * 12) for _ in range(10))
    body = TwoColumn("L", heavy, "R", (Bullet("ok"),))
    assert "TEXT_OVERFLOW" in rules(Slide(1, "T", body, 60))


def test_footnote_longer_than_two_lines_is_flagged():
    slide = Slide(
        1, "T", Bullets((Bullet("x"),)), 60,
        refs=("control_imposs", "lost_abduction", "fugitive_cash",
              "gen_contradiction", "active_inference", "processing_speed"),
    )
    assert "FOOTER_LINES" in rules(slide)


# --- diagrams -------------------------------------------------------------

@pytest.mark.parametrize("kind", list(DiagramKind))
def test_every_diagram_stays_inside_the_slide(kind):
    slide = Slide(1, "T", Diagram(kind), 60, refs=("main_paper",))
    assert "SHAPE_BOUNDS" not in rules(slide)


@pytest.mark.parametrize("kind", list(DiagramKind))
def test_no_diagram_boxes_overlap(kind):
    slide = Slide(1, "T", Diagram(kind), 60, refs=("main_paper",))
    assert "SHAPE_OVERLAP" not in rules(slide)


def test_four_conditions_thresholds_do_not_sit_on_boxes():
    """The frontier rule must land in a gap, not across a condition box."""
    from slides.shapes import THRESHOLDS

    specs = diagram_specs(DiagramKind.FOUR_CONDITIONS, body_rect(True, True), THEME)
    boxes = [s for s in specs if s.tag.startswith("box")]
    rules_ = [s for s in specs if s.tag.startswith("rule")]
    assert len(rules_) == len(THRESHOLDS)
    for r in rules_:
        for b in boxes:
            overlap = min(r.top + r.height, b.top + b.height) - max(r.top, b.top)
            assert overlap <= 0, f"{r.tag} crosses {b.tag}"


# --- palette ---------------------------------------------------------------

def test_diagrams_take_every_colour_from_the_theme():
    """A hard-coded fill survives a palette change and turns white text
    invisible; every colour must come from the theme."""
    import ast
    from pathlib import Path

    src = Path(__file__).resolve().parent.parent / "slides" / "shapes.py"
    literals = [
        node.value
        for node in ast.walk(ast.parse(src.read_text()))
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]
    hex_like = [
        v for v in literals
        if len(v) == 6 and all(c in "0123456789ABCDEFabcdef" for c in v)
    ]
    assert hex_like == []


# --- per-slide body scaling ------------------------------------------------

def test_body_text_never_outgrows_the_title():
    """A body larger than its own heading inverts the visual hierarchy."""
    from slides.content import SLIDES
    from slides.model import bullets_of
    from slides.theme import body_pt
    from slides.validate import body_scale

    for s in SLIDES:
        scale = body_scale(s, THEME)
        for b in bullets_of(s.body):
            pt = body_pt(b.level, THEME, s.dense, scale)
            assert pt < THEME.title_pt, f"slide {s.number}: body {pt}pt"


def test_body_text_never_falls_below_the_floor():
    from slides.content import SLIDES
    from slides.model import bullets_of
    from slides.theme import body_pt
    from slides.validate import body_scale

    for s in SLIDES:
        scale = body_scale(s, THEME)
        for b in bullets_of(s.body):
            pt = body_pt(b.level, THEME, s.dense, scale)
            assert pt >= THEME.min_body_pt, f"slide {s.number}: body {pt}pt"


def test_scaling_only_grows_text():
    """The fit factor is a filler, not a shrinker — shrinking to fit would
    silently defeat the overflow checks."""
    from slides.content import SLIDES
    from slides.validate import body_scale

    for s in SLIDES:
        assert body_scale(s, THEME) >= 1.0, s.number


def test_sparse_slides_are_scaled_up():
    """The whole point: a three-bullet slide must not render at the base size."""
    from slides.content import SLIDES
    from slides.validate import body_scale

    legg = next(s for s in SLIDES if "Legg & Hutter" in s.title)
    assert body_scale(legg, THEME) > 1.2
