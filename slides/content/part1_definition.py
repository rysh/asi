"""Slides 1-16: from the mystification of genius to the definition of ASI.

Every bullet is the outline's own sentence, verbatim. Where the outline uses
an arrow, an equals sign or a parenthetical, that is kept — those are the
author's phrasing, not shorthand to be expanded, and rewriting them into
smoother prose is exactly what the outline forbids.
"""

from __future__ import annotations

from slides.model import (
    Bullet,
    Bullets,
    Diagram,
    DiagramKind,
    Image,
    Slide,
    TitleBlock,
    TwoColumn,
)
from slides.refs import PUBLISHED, UNDER_REVIEW, Ref, format_listing

B = Bullet


SLIDE_1 = Slide(
    number=1,
    title="Redefining Artificial Superintelligence",
    body=TitleBlock(
        title="Redefining Artificial Superintelligence",
        subtitle="From Mystified Genius to Observable Conditions",
        author="Franny Philos Sophia",
        affiliation="Elanare Institute",
        meta=(
            "ORCID 0009-0004-7089-5265  ·  franny.philos.sophia@elanare.jp",
            "SiC26  ·  Day 1, Session 1: Defining and Evaluating Superintelligence",
            "9 September 2026",
            "",
            "Preprints on Zenodo. All footnoted DOIs refer to preprints "
            "unless otherwise noted.",
        ),
    ),
    budget_sec=20,
)


SLIDE_2 = Slide(
    number=2,
    title="Where This Talk Goes",
    body=TwoColumn(
        left_head="The problem with the question",
        left=(
            B("1.  The Genius Problem and IQ", emphasis=True),
            B("The baseline we measure “super” against was never measured", 1),
            B("2.  Critique of Existing Definitions", emphasis=True),
            B("Bostrom, Legg & Hutter, Chollet, Goertzel — why each fails", 1),
            B("3.  Four Conditions and Discussion", emphasis=True),
            B("Two are already met. The other two are the actual frontier", 1),
            B("4.  Defining ASI", emphasis=True),
            B("Continuous novel discovery, not speed and not accuracy", 1),
        ),
        right_head="What the frontier requires",
        right=(
            B("5.  What Is AGI?", emphasis=True),
            B("General means reframing — and reframing costs controllability", 1),
            B("6.  The Path to Scientific Creativity", emphasis=True),
            B("Why a system cannot verify its own novelty from the inside", 1),
            B("7.  Synthesis", emphasis=True),
            B("One possible design, and what it needs from the physical world", 1),
        ),
    ),
    budget_sec=25,
    kicker="Agenda",
)


# Thirteen papers cited in full, with DOIs, do not fit the standard body
# margin, so this one slide runs wide (see wide_body_rect). Nothing is
# abbreviated except the shared Zenodo DOI prefix: the titles are the content.

def _halves(refs: tuple[Ref, ...]) -> tuple[tuple[Bullet, ...], tuple[Bullet, ...]]:
    """Split a reference list into two balanced columns, in reading order."""
    items = tuple(B(format_listing(r), 1) for r in refs)
    cut = (len(items) + 1) // 2
    return items[:cut], items[cut:]


_UNDER_REVIEW_SPLIT = 3
_REV = tuple(UNDER_REVIEW.values())


SLIDE_3 = Slide(
    number=3,
    title="About the Author",
    # Published on the left, under review split across the fold. The right
    # column head continues the left one rather than repeating it, so the
    # section label costs no body line.
    body=TwoColumn(
        left_head="Published (3)   ·   Under review (10), 1-3",
        left=(
            tuple(B(format_listing(r), 1) for r in PUBLISHED.values())
            + tuple(B(format_listing(r), 1) for r in _REV[:_UNDER_REVIEW_SPLIT])
        ),
        right_head="Under review (10), 4-10",
        right=tuple(B(format_listing(r), 1) for r in _REV[_UNDER_REVIEW_SPLIT:]),
    ),
    budget_sec=25,
    dense=True,
    wide=True,
    caveat="Independent researcher, Japanese, Software Engineer  ·  "
           "2E (Twice Exceptional) / ADHD / ASD  ·  ORCID 0009-0004-7089-5265",
    caveat_prominent=True,
)


# --- 1. The Genius Problem and IQ ----------------------------------------

SLIDE_4 = Slide(
    number=4,
    title="The Mystification of Genius",
    kicker="1. The Genius Problem and IQ",
    body=Bullets(
        (
            B("IQ rankings have mystified genius"),
            B("Von Neumann ~190, Ramanujan ~185+ are extrapolations from "
              "biographical anecdote, not measured values"),
            B("Numbers that were never measured and cannot exist on the scale are "
              "assigned without evidence and take on a life of their own",
              emphasis=True),
        )
    ),
    budget_sec=45,
    refs=("processing_speed", "who_are_we"),
)


SLIDE_5 = Slide(
    number=5,
    title="Genius as Outlier",
    body=Bullets(
        (
            B("Genius has been elevated to authority, made taboo, and mystified",
              emphasis=True),
            B("Or excluded from research to protect the certainty of established "
              "findings"),
            B("Treated as an outlier that is not a research subject in the first "
              "place"),
            B("Von Neumann: could not analyze quantum phenomena without macroscopic "
              "analogies. Describable as constraint conditions when observed as-is",
              1),
            B("Ramanujan: abductive hypothesis generation + brute-force computation. "
              "Not mystery but a describable process", 1),
            B("Leibniz: systematic formalization of existing infinitesimal methods",
              1),
            B("Aristotle: categorical organization of observational data across "
              "domains", 1),
        )
    ),
    budget_sec=50,
)


SLIDE_6 = Slide(
    number=6,
    title="A Goal That Does Not Exist",
    body=Bullets(
        (
            B("Claiming to “surpass” something that has not been analyzed is a "
              "trivialization of reality"),
            B("“Surpassing the best human minds” has no baseline — it is "
              "undefinable"),
            B("Human cognitive ability has no fixed upper bound"),
            B("We are chasing a goal that does not exist", emphasis=True),
        )
    ),
    budget_sec=30,
)


# --- 2. Critique of Existing Definitions ---------------------------------

SLIDE_7 = Slide(
    number=7,
    title="Bostrom: Already Achieved Conditions and a Metaphor",
    kicker="2. Critique of Existing Definitions",
    body=Bullets(
        (
            B("Three categories: Speed / Collective / Quality"),
            B("Speed and Collective are already achieved (though Bostrom's "
              "definition conflates processing throughput with cognitive capability "
              "range. Isolate speed as pure throughput and it is already achieved)",
              emphasis=True),
            B("Quality is a metaphor (“the kind of superiority humans have over "
              "animals”), not a definition"),
            B("“Greatly exceeds human performance in virtually all domains” has no "
              "boundary conditions"),
        )
    ),
    budget_sec=50,
    refs=("main_paper",),
)


SLIDE_8 = Slide(
    number=8,
    title="Legg & Hutter: A Definition That Cannot Be Computed",
    body=Bullets(
        (
            B("Expected reward across all computable environments, weighted by "
              "algorithmic complexity"),
            B("Incomputable by the authors' own admission", emphasis=True),
            B("Ignores resources. A definition that cannot be computed is not a "
              "definition"),
        )
    ),
    budget_sec=35,
)


SLIDE_9 = Slide(
    number=9,
    title="Chollet: Calling Infant Learning Intelligence",
    body=Bullets(
        (
            B("Skill-acquisition efficiency = intelligence"),
            B("ARC benchmark is restricted to Spelke's Core Knowledge (the cognitive "
              "endowments of human infants)"),
            B("Equates infant-level pattern extraction with intelligence as such",
              emphasis=True),
            B("The definition was reverse-engineered to match the benchmark",
              emphasis=True),
        )
    ),
    budget_sec=40,
)


SLIDE_10 = Slide(
    number=10,
    title="Goertzel: AGI Does Not Scale Into ASI",
    body=Bullets(
        (
            B("A metaphysical discussion modeled on human intelligence "
              "(pre-LLM, 2007)"),
            B("Treats AGI → self-improvement → ASI as a continuum"),
            B("Treats capability as a scalar value — assumes ASI lies at the far end "
              "of quantitative improvement"),
            B("AGI and ASI are qualitatively different: reframing (adaptation) vs. "
              "abduction (generation)", emphasis=True),
            B("Acknowledges embodied learning and the symbol grounding problem, "
              "which deserves credit. But does not resolve it"),
        )
    ),
    budget_sec=45,
    refs=("intention", "conservation"),
)


# --- 3. Four Conditions and Discussion -----------------------------------

SLIDE_11 = Slide(
    number=11,
    title="Calibrating the Definition",
    kicker="3. Four Conditions and Discussion",
    body=Bullets(
        (
            B("The human reference frame is not abandoned (“super” is a relational "
              "predicate)"),
            B("But “surpass the best of humanity” is undefinable and therefore "
              "unreachable"),
            B("Move the boundary conditions from the human upper limit to the "
              "current capability limits of AI"),
            B("Because Speed and Collective are already resolved, the remaining gaps "
              "become specifiable"),
            B("This decomposition was impossible in 2014. It is possible now, "
              "in 2026", emphasis=True),
        )
    ),
    budget_sec=50,
    refs=("main_paper",),
)


SLIDE_12 = Slide(
    number=12,
    title="The Four Conditions",
    body=Diagram(kind=DiagramKind.FOUR_CONDITIONS),
    budget_sec=70,
    refs=("main_paper",),
)


SLIDE_13 = Slide(
    number=13,
    title="No Abduction, No Creativity",
    body=Bullets(
        (
            B("Solving existing unsolved problems = deduction. Valuable, but not "
              "creativity"),
            B("Extracting patterns from large datasets = induction. Valuable, but "
              "not creativity"),
            B("Creativity = posing a question nobody has asked, from an observation "
              "nobody has framed"),
            B("Abduction (Peirce): the only inference that introduces a new idea",
              emphasis=True),
        )
    ),
    budget_sec=50,
    refs=("lost_abduction",),
)


SLIDE_14 = Slide(
    number=14,
    title="Scaling Is Dead",
    body=Bullets(
        (
            B("Scaling cannot achieve Condition 3 or Condition 4", emphasis=True),
            B("Parameter scaling hit a ceiling → inference-time scaling → "
              "chain-of-thought → increased reasoning steps per request"),
            B("Workflows, agents, tool calls — things users previously implemented "
              "via API — are now wrapped into the model's outer shell"),
            B("All mixed together, details undisclosed, benchmarks reported as "
              "improved"),
            B("Why this fails is explored later"),
        )
    ),
    budget_sec=45,
)


SLIDE_15 = Slide(
    number=15,
    title="Two Challenges, Solved Separately",
    body=Image(
        key="axes",
        lead=(
            B("Not connected by a straight line of scaling. Each requires its own "
              "design", emphasis=True),
        ),
        caption="After realization, each must be intentionally designed and improved "
                "as a separate capability or it will not grow. Computing reduces to "
                "four logical operations, but without CPU instruction set design and "
                "hardware-software coordination, today's performance would not "
                "exist. Individual challenges solved by individual design — that is "
                "what produced the performance we have.",
    ),
    budget_sec=40,
)


# --- 4. Defining ASI ------------------------------------------------------

SLIDE_16 = Slide(
    number=16,
    title="Speed and Accuracy Are Only Prerequisites",
    kicker="4. Defining ASI",
    body=Bullets(
        (
            B("Computers are already fast enough"),
            B("Not making mistakes is also not a condition for ASI"),
            B("AlphaFold, GraphCast, medical imaging, autonomous perception, genome "
              "analysis — all orders of magnitude faster and more accurate than "
              "humans. But none produce new knowledge"),
            B("Speed and accuracy are useful in practice but are not boundary "
              "conditions for ASI", emphasis=True),
        )
    ),
    budget_sec=40,
)


SLIDE_17 = Slide(
    number=17,
    title="ASI = Continuous Novel Discovery",
    body=Image(
        key="triangle",
        lead=(
            B("ASI = the ability to continuously make novel discoveries and "
              "inventions, update knowledge, and surpass humans", emphasis=True),
        ),
    ),
    budget_sec=40,
)



PART1: tuple[Slide, ...] = (
    SLIDE_1, SLIDE_2, SLIDE_3, SLIDE_4, SLIDE_5, SLIDE_6, SLIDE_7, SLIDE_8,
    SLIDE_9, SLIDE_10, SLIDE_11, SLIDE_12, SLIDE_13, SLIDE_14, SLIDE_15,
    SLIDE_16, SLIDE_17,
)
