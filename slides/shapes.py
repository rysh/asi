"""Diagram geometry as pure data.

Each diagram is a tuple of ShapeSpec. Because the coordinates are computed
here rather than during rendering, layout itself is testable: validate.py
checks bounds and overlaps without ever touching python-pptx.

Rotation and connectors are avoided throughout — both are re-computed by
Keynote and Google Slides on import and drift out of place.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from slides.geometry import Rect, stack
from slides.model import Bullet, DiagramKind
from slides.theme import Theme, inches


class ShapeKind(Enum):
    ROUNDED_BOX = "rounded_box"
    BOX = "box"
    OVAL = "oval"
    RULE = "rule"          # thin filled rectangle used instead of a connector
    DASHED_RULE = "dashed_rule"
    LABEL = "label"        # plain textbox, no fill
    ARROW = "arrow"


@dataclass(frozen=True)
class ShapeSpec:
    kind: ShapeKind
    left: int
    top: int
    width: int
    height: int
    text: str = ""
    fill: str | None = None
    line: str | None = None
    text_color: str | None = None
    font_pt: int = 16
    bold: bool = False
    align: str = "left"       # left | center | right
    tag: str = ""
    collide: bool = True      # participates in the overlap check


# --------------------------------------------------------------------------
# Slide 8 — the four conditions, as an attainment ladder.
#
# A vertical stack beats a 2x2 grid here: the AGI and ASI thresholds become
# single horizontal lines, which is exactly the claim being made.
# --------------------------------------------------------------------------

FOUR_CONDITIONS = (
    ("SPEED", True, "Processing speed exceeds human cognition by orders of magnitude"),
    (
        "COLLECTIVE INTELLIGENCE",
        True,
        "Cross-domain knowledge integration is already achieved",
    ),
    (
        "SCIENTIFIC CREATIVITY",
        False,
        "Cannot generate or validate novel hypotheses",
    ),
    (
        "GENERAL WISDOM UNDER COMPLEXITY",
        False,
        "Judgment breaks down in complex situations",
    ),
)

# The dashed rule sits above the band at this index. Both unmet conditions
# fall below the single achieved/frontier line.
THRESHOLDS: dict[int, str] = {2: ""}


def four_conditions_spec(rect: Rect, theme: Theme) -> tuple[ShapeSpec, ...]:
    label_w = inches(1.85)
    ladder = Rect(rect.left, rect.top, rect.width - label_w - inches(0.16), rect.height)
    gap = inches(0.34)
    bands = tuple(
        Rect(b.left, b.top + inches(0.05), b.width, b.height - inches(0.1))
        for b in stack(ladder, len(FOUR_CONDITIONS), gap)
    )
    mark_w = inches(0.6)
    out: list[ShapeSpec] = []

    for i, ((name, met, gloss), band) in enumerate(zip(FOUR_CONDITIONS, bands)):
        fill = theme.achieved_fill if met else theme.frontier_fill
        line = theme.achieved_line if met else theme.frontier_line
        out.append(
            ShapeSpec(
                ShapeKind.ROUNDED_BOX,
                band.left,
                band.top,
                band.width,
                band.height,
                fill=fill,
                line=line,
                tag=f"box{i}",
            )
        )
        out.append(
            ShapeSpec(
                ShapeKind.LABEL,
                band.left + inches(0.22),
                band.top + inches(0.06),
                band.width - mark_w - inches(0.4),
                band.height - inches(0.12),
                text=f"{name}\n{gloss}",
                text_color=theme.text,
                font_pt=17,
                bold=True,
                tag=f"name{i}",
                collide=False,
            )
        )
        out.append(
            ShapeSpec(
                ShapeKind.LABEL,
                band.right - mark_w,
                band.top + inches(0.06),
                mark_w - inches(0.1),
                band.height - inches(0.12),
                text="✓" if met else "✗",
                text_color=theme.check if met else theme.cross,
                font_pt=26,
                bold=True,
                align="center",
                tag=f"mark{i}",
                collide=False,
            )
        )

    # Thresholds sit in the gaps between bands, never on top of a box.
    for idx, caption in THRESHOLDS.items():
        above = bands[idx - 1]
        rule_top = above.bottom + gap // 2 - inches(0.012)
        out.append(
            ShapeSpec(
                ShapeKind.DASHED_RULE,
                ladder.left,
                rule_top,
                ladder.width,
                inches(0.024),
                fill=theme.accent,
                tag=f"rule{idx}",
                collide=False,
            )
        )
        out.append(
            ShapeSpec(
                ShapeKind.LABEL,
                ladder.right + inches(0.16),
                rule_top - inches(0.13),
                label_w - inches(0.16),
                inches(0.3),
                text=caption,
                text_color=theme.accent,
                font_pt=theme.diagram_small_pt,
                bold=True,
                tag=f"thlabel{idx}",
                collide=False,
            )
        )

    out.append(
        ShapeSpec(
            ShapeKind.LABEL,
            ladder.right + inches(0.16),
            bands[0].top,
            label_w - inches(0.16),
            inches(0.3),
            text="ACHIEVED",
            text_color=theme.check,
            font_pt=theme.diagram_small_pt,
            bold=True,
            tag="achieved",
            collide=False,
        )
    )
    out.append(
        ShapeSpec(
            ShapeKind.LABEL,
            ladder.right + inches(0.16),
            bands[-1].bottom - inches(0.3),
            label_w - inches(0.16),
            inches(0.3),
            text="FRONTIER",
            text_color=theme.cross,
            font_pt=theme.diagram_small_pt,
            bold=True,
            tag="frontier",
            collide=False,
        )
    )
    return tuple(out)


# --------------------------------------------------------------------------
# Slide 5 — a ruler that fails at both ends.
# --------------------------------------------------------------------------

def ruler_spec(rect: Rect, theme: Theme) -> tuple[ShapeSpec, ...]:
    bar_h = inches(1.05)
    bar_top = rect.top + inches(1.0)
    seg_w = rect.width // 4
    segments = (
        ("measurable", "≤ ~130", theme.achieved_fill, theme.achieved_line, theme.text),
        ("noise-dominated", "~130–160", theme.caution_fill, theme.caution_line, theme.text),
        ("no measured values", "above ~160", theme.frontier_fill, theme.frontier_line, theme.cross),
        ("retroactive scores", "“185+”, “190”", theme.inert_fill, theme.inert_line,
         theme.muted),
    )
    out: list[ShapeSpec] = []
    for i, (label, band, fill, line, ink) in enumerate(segments):
        left = rect.left + i * seg_w
        out.append(
            ShapeSpec(
                ShapeKind.BOX, left, bar_top, seg_w - inches(0.06), bar_h,
                fill=fill, line=line, tag=f"seg{i}",
            )
        )
        out.append(
            ShapeSpec(
                ShapeKind.LABEL, left, bar_top + inches(0.1),
                seg_w - inches(0.06), inches(0.85),
                text=f"{band}\n{label}",
                text_color=ink, font_pt=theme.diagram_small_pt, bold=True,
                align="center", tag=f"seglabel{i}", collide=False,
            )
        )
    out.append(
        ShapeSpec(
            ShapeKind.LABEL, rect.left, rect.top,
            rect.width, inches(0.6),
            text="The gifted cluster near ~125 — not because ability stops, "
                 "but because the procedure penalises the cognitive style of high ability",
            text_color=theme.accent, font_pt=15, bold=True,
            tag="ruler_lead", collide=False,
        )
    )
    out.append(
        ShapeSpec(
            ShapeKind.LABEL, rect.left, bar_top + bar_h + inches(0.42),
            rect.width, inches(1.6),
            text="We overestimate past geniuses on a scale that does not reach them, "
                 "while underestimating present ones the same scale cannot measure.\n"
                 "73.5% of healthy adults show at least one index score deviating "
                 "significantly from their own mean — the “abnormal profile” is the statistical norm.\n"
                 "The baseline for “surpassing the best human minds” rests on a ruler "
                 "that breaks at both ends.",
            text_color=theme.text, font_pt=17,
            tag="ruler_conclusion", collide=False,
        )
    )
    return tuple(out)


# --------------------------------------------------------------------------
# Slide 12 — the human-AI research workflow actually in use.
# --------------------------------------------------------------------------

WORKFLOW_STEPS = (
    ("Human", "motivation\n& curiosity"),
    ("LLM", "survey the\nliterature"),
    ("Human", "abduction:\nnew hypothesis"),
    ("LLM", "novelty &\ncounter-evidence"),
    ("Human", "connect, judge,\nwrite"),
)


def workflow_spec(rect: Rect, theme: Theme) -> tuple[ShapeSpec, ...]:
    n = len(WORKFLOW_STEPS)
    gap = inches(0.16)
    box_w = (rect.width - gap * (n - 1)) // n
    box_h = inches(1.32)
    top = rect.top + inches(0.5)
    out: list[ShapeSpec] = []
    for i, (actor, what) in enumerate(WORKFLOW_STEPS):
        left = rect.left + i * (box_w + gap)
        human = actor == "Human"
        out.append(
            ShapeSpec(
                ShapeKind.ROUNDED_BOX, left, top, box_w, box_h,
                fill=theme.achieved_fill if human else theme.panel_fill,
                line=theme.achieved_line if human else theme.accent,
                tag=f"wf{i}",
            )
        )
        out.append(
            ShapeSpec(
                ShapeKind.LABEL, left, top + inches(0.1), box_w, inches(0.28),
                text=actor, text_color=theme.check if human else theme.accent,
                font_pt=theme.diagram_small_pt, bold=True, align="center",
                tag=f"wfactor{i}", collide=False,
            )
        )
        out.append(
            ShapeSpec(
                ShapeKind.LABEL, left, top + inches(0.44), box_w, inches(0.8),
                text=what, text_color=theme.text, font_pt=theme.diagram_small_pt, align="center",
                tag=f"wfwhat{i}", collide=False,
            )
        )
    out.append(
        ShapeSpec(
            ShapeKind.LABEL, rect.left, top + box_h + inches(0.2),
            rect.width, inches(0.34),
            text="Initiative and judgment are always human; the LLM is a survey instrument.",
            text_color=theme.accent, font_pt=16, bold=True, align="center",
            tag="wfnote", collide=False,
        )
    )
    out.append(
        ShapeSpec(
            ShapeKind.LABEL, rect.left, top + box_h + inches(0.68),
            rect.width, inches(0.9),
            text="Next: give the loop access to experiment and observation — automated labs, "
                 "experiment-as-a-service for agents — so that judgment is no longer confined "
                 "to the interior of the training data.",
            text_color=theme.text, font_pt=15, align="center",
            tag="wfnext", collide=False,
        )
    )
    return tuple(out)


# --------------------------------------------------------------------------
# Slide 16 — the scientific creativity loop.
# --------------------------------------------------------------------------

LOOP_STEPS = (
    "Observation",
    "Pattern\nrecognition",
    "Hypothesis\n(abduction)",
    "Experiment\ndesign",
    "Execution",
    "Evaluation",
    "Revision",
    "Law\nformulation",
)


def loop_spec(rect: Rect, theme: Theme) -> tuple[ShapeSpec, ...]:
    per_row = 4
    gap_x = inches(0.16)
    gap_y = inches(0.2)
    box_w = (rect.width - gap_x * (per_row - 1)) // per_row
    box_h = inches(0.86)
    top = rect.top + inches(0.36)
    out: list[ShapeSpec] = []
    for i, label in enumerate(LOOP_STEPS):
        row, col = divmod(i, per_row)
        # Serpentine: the second row reads right-to-left, closing the cycle.
        if row == 1:
            col = per_row - 1 - col
        left = rect.left + col * (box_w + gap_x)
        t = top + row * (box_h + gap_y)
        abductive = "abduction" in label
        out.append(
            ShapeSpec(
                ShapeKind.ROUNDED_BOX, left, t, box_w, box_h,
                fill=theme.highlight_fill if abductive else theme.panel_fill,
                line=theme.highlight_line if abductive else theme.panel_line,
                tag=f"loop{i}",
            )
        )
        out.append(
            ShapeSpec(
                ShapeKind.LABEL, left, t + inches(0.14), box_w, box_h - inches(0.2),
                text=label, text_color=theme.text, font_pt=14,
                bold=abductive, align="center",
                tag=f"looplabel{i}", collide=False,
            )
        )
    bottom = top + 2 * box_h + gap_y
    out.append(
        ShapeSpec(
            ShapeKind.LABEL, rect.left, bottom + inches(0.14),
            rect.width, inches(0.36),
            text="Each step is individually attackable as engineering. "
                 "What current systems cannot sustain is the loop.",
            text_color=theme.accent, font_pt=16, bold=True, align="center",
            tag="loopnote", collide=False,
        )
    )
    out.append(
        ShapeSpec(
            ShapeKind.LABEL, rect.left, bottom + inches(0.56),
            rect.width, inches(0.8),
            text="Authority gradients, not a control/freedom binary: more autonomy for routine "
                 "verification, less for accepting a novel claim. Humans receive, interpret, and direct.",
            text_color=theme.text, font_pt=15, align="center",
            tag="loopgrad", collide=False,
        )
    )
    return tuple(out)


def diagram_specs(
    kind: DiagramKind, rect: Rect, theme: Theme, lead: tuple[Bullet, ...] = ()
) -> tuple[ShapeSpec, ...]:
    """Dispatch to the diagram builder. `lead` bullets are rendered above the
    diagram by render.py, so the rect passed here is already reduced."""
    match kind:
        case DiagramKind.FOUR_CONDITIONS:
            return four_conditions_spec(rect, theme)
        case DiagramKind.RULER:
            return ruler_spec(rect, theme)
        case DiagramKind.WORKFLOW:
            return workflow_spec(rect, theme)
        case DiagramKind.LOOP:
            return loop_spec(rect, theme)
    raise ValueError(f"unknown diagram: {kind}")
