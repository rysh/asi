"""Slide content model. Pure data — no python-pptx dependency."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Mark(Enum):
    CHECK = "✓"
    CROSS = "✗"


class DiagramKind(Enum):
    FOUR_CONDITIONS = "four_conditions"
    RULER = "ruler"
    WORKFLOW = "workflow"
    LOOP = "loop"


@dataclass(frozen=True)
class Bullet:
    text: str
    level: int = 0
    emphasis: bool = False
    mark: Mark | None = None


@dataclass(frozen=True)
class TitleBlock:
    title: str
    subtitle: str
    author: str
    affiliation: str
    meta: tuple[str, ...] = ()


@dataclass(frozen=True)
class Bullets:
    items: tuple[Bullet, ...]


@dataclass(frozen=True)
class TwoColumn:
    left_head: str
    left: tuple[Bullet, ...]
    right_head: str
    right: tuple[Bullet, ...]


@dataclass(frozen=True)
class QuoteBlock:
    quote: str
    attribution: str
    lead: tuple[Bullet, ...] = ()
    follow: tuple[Bullet, ...] = ()


@dataclass(frozen=True)
class Diagram:
    kind: DiagramKind
    caption: str | None = None
    lead: tuple[Bullet, ...] = ()


@dataclass(frozen=True)
class Image:
    """A figure supplied as a file in assets/. Sized to fit at render time;
    the aspect ratio is read from the file itself so the check and the draw
    agree on where it lands."""
    key: str
    caption: str | None = None
    lead: tuple[Bullet, ...] = ()


@dataclass(frozen=True)
class ContactBlock:
    summary: str
    lines: tuple[tuple[str, str], ...]
    closing: str
    ref_ids: tuple[str, ...] = ()


Body = TitleBlock | Bullets | TwoColumn | QuoteBlock | Diagram | Image | ContactBlock


@dataclass(frozen=True)
class Slide:
    number: int
    title: str
    body: Body
    budget_sec: int
    kicker: str | None = None
    refs: tuple[str, ...] = ()
    caveat: str | None = None
    # Renders the caveat as a statement rather than fine print: body size,
    # bright, upright. For lines that are content, not disclaimers.
    caveat_prominent: bool = False
    dense: bool = False  # relaxes bullet-count limit (the publication list)
    wide: bool = False   # uses the full-bleed reference layout


def bullets_of(body: Body) -> tuple[Bullet, ...]:
    """Every Bullet contained in a body, in reading order."""
    match body:
        case Bullets(items):
            return items
        case TwoColumn(_, left, _, right):
            return left + right
        case QuoteBlock(_, _, lead, follow):
            return lead + follow
        case Diagram(_, _, lead):
            return lead
        case Image(_, _, lead):
            return lead
        case _:
            return ()


def texts_of(body: Body) -> tuple[str, ...]:
    """Every human-visible string in a body, for content assertions."""
    match body:
        case TitleBlock(title, subtitle, author, affiliation, meta):
            return (title, subtitle, author, affiliation) + meta
        case TwoColumn(lh, left, rh, right):
            return (lh, rh) + tuple(b.text for b in left + right)
        case QuoteBlock(quote, attribution, lead, follow):
            return (quote, attribution) + tuple(b.text for b in lead + follow)
        case Diagram(_, caption, lead) | Image(_, caption, lead):
            base = (caption,) if caption else ()
            return base + tuple(b.text for b in lead)
        case ContactBlock(summary, lines, closing, _):
            return (summary, closing) + tuple(
                part for pair in lines for part in pair
            )
        case _:
            return tuple(b.text for b in bullets_of(body))


def slide_texts(slide: Slide) -> tuple[str, ...]:
    """Every human-visible string on a slide, including title and caveat."""
    extra = tuple(x for x in (slide.kicker, slide.caveat) if x)
    return (slide.title,) + texts_of(slide.body) + extra
