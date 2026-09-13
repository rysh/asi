"""The deck, as declarative data."""

from slides.content.part1_definition import PART1
from slides.content.part2_vision import PART2
from slides.model import Slide

SLIDES: tuple[Slide, ...] = PART1 + PART2

__all__ = ["SLIDES", "PART1", "PART2"]
