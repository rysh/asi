"""Bibliographic registry. The single source of truth for every DOI in the
deck — no DOI string is written anywhere else in the codebase.

Titles are the full titles as published on Zenodo, verified against the
landing page of each DOI. Titles are never abbreviated — the publication list
and the footnotes both cite each paper in full.

Statuses:
  doi          — a persistent identifier exists and is quotable
  under_review — submitted to the named venue; the DOI is the preprint
  in_press     — accepted, not yet paginated
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Mapping

Status = Literal["doi", "under_review", "in_press", "url"]

ZENODO_PREFIX = "10.5281/zenodo."


@dataclass(frozen=True)
class Ref:
    title: str
    venue: str
    status: Status = "doi"
    doi: str | None = None
    url: str | None = None
    note: str | None = None


# --- published ------------------------------------------------------------

PUBLISHED: Mapping[str, Ref] = {
    "logic_trap": Ref(
        title='The logic trap: How LLM "Helpfulness" becomes a mechanism of '
              "psychological harm",
        venue="AI & Ethics (Springer)",
        doi="10.1007/s43681-026-01148-6",
    ),
    "centaur": Ref(
        title="The Centaur Is Not Dying. It Is Stratifying. Why the Chess Analogy "
              "Fails for the Software Industry — and Every Industry That Follows",
        venue="CACM",
        status="in_press",
        doi="10.5281/zenodo.18733027",
    ),
    "brachiation": Ref(
        title="Brachiation-based movement as a theoretical framework for addressing "
              "technology-related postural dysfunction: An evolutionary and "
              "neuromuscular perspective",
        venue="JBMT",
        doi="10.1016/j.jbmt.2026.03.008",
        note="PubMed 42264802",
    ),
}

# --- under review ---------------------------------------------------------

UNDER_REVIEW: Mapping[str, Ref] = {
    "control_imposs": Ref(
        title="The Control Impossibility: From Reframing Asymmetry to "
              "Constitutional Architecture",
        venue="JAGI",
        status="under_review",
        doi="10.5281/zenodo.19943538",
    ),
    "exec_governance": Ref(
        title="Beyond Executable Governance: Why Encoding Rules Cannot Replace "
              "Knowledge Cycles in AI-Assisted Development",
        venue="CACM",
        status="under_review",
        doi="10.5281/zenodo.19429152",
    ),
    "seci": Ref(
        title="The SECI Model in Practice: The Knowledge Creation Architecture "
              "Embedded in Scrum",
        venue="TLO",
        status="under_review",
        doi="10.5281/zenodo.21293879",
    ),
    "interoception": Ref(
        title="Brain Interoception: The Missing Organ on the Interoceptive Map",
        venue="New Ideas in Psychology",
        status="under_review",
        doi="10.5281/zenodo.19942221",
    ),
    "emergence_dichotomy": Ref(
        title="Emergence Without the Dichotomy",
        venue="Erkenntnis",
        status="under_review",
        doi="10.5281/zenodo.21319707",
    ),
    "fugitive_cash": Ref(
        title="From Fugitive Cash to Non-Fugitive Provisioning: The Mundellian "
              "Trilemma, External Debt Feedback, and the Design Space of "
              "Post-Employment Redistribution",
        venue="PEPE",
        status="under_review",
        doi="10.5281/zenodo.21759090",
    ),
    "dynamic_emergence": Ref(
        title="Dynamic Emergence: A Unified Theory Based on the Stuart-Landau "
              "Equation",
        venue="SHPS",
        status="under_review",
        doi="10.5281/zenodo.18074645",
    ),
    "lost_abduction": Ref(
        title="Lost Abduction and Epistemic Barriers: Toward a Completion Model "
              "of Science Communication",
        venue="SHPS",
        status="under_review",
        doi="10.5281/zenodo.20005937",
    ),
    "active_inference": Ref(
        title="From Instability to Active Inference: A Unified Mathematical "
              "Framework for Biological Self-Organization across Scales",
        venue="BioSystems",
        status="under_review",
        doi="10.5281/zenodo.18017028",
    ),
    "manifold": Ref(
        title="When the Manifold Collapses: A Geometric Theory of Constraint "
              "Conflict in Large Language Models",
        venue="Neural Computation",
        status="under_review",
        doi="10.5281/zenodo.20642039",
    ),
}

# --- cited in footnotes only ----------------------------------------------

FOOTNOTED: Mapping[str, Ref] = {
    "main_paper": Ref(
        title="Redefining Artificial Superintelligence",
        venue="SiC26",
        status="url",
        url="https://openreview.net/forum?id=lLWeptkTPH",
    ),
    "processing_speed": Ref(
        title="Processing Speed Contamination",
        venue="preprint",
        doi="10.5281/zenodo.19105953",
    ),
    "who_are_we": Ref(
        title="Who Are We Testing?",
        venue="preprint",
        doi="10.5281/zenodo.17745229",
    ),
    "intention": Ref(
        title="Intention Without Causation",
        venue="preprint",
        doi="10.5281/zenodo.19234682",
    ),
    "conservation": Ref(
        title="The Conservation Demarcation",
        venue="preprint",
        doi="10.5281/zenodo.21000863",
    ),
    "gen_contradiction": Ref(
        title="Generative Contradiction: Reading Gödel with Nishida",
        venue="preprint",
        doi="10.5281/zenodo.21612954",
    ),
    "mishima": Ref(
        title="Mishima and Thanatos",
        venue="preprint",
        doi="10.5281/zenodo.20489614",
    ),
}

REFS: Mapping[str, Ref] = {**PUBLISHED, **UNDER_REVIEW, **FOOTNOTED}


def format_ref(ref: Ref) -> str:
    """One reference as a single footnote line."""
    match ref.status:
        case "doi":
            assert ref.doi is not None
            return f"{ref.title}. doi.org/{ref.doi}"
        case "url":
            assert ref.url is not None
            return f"{ref.title} — {ref.url}"
        case "in_press":
            assert ref.doi is not None
            return f"{ref.title} ({ref.venue}, in press). doi.org/{ref.doi}"
        case "under_review":
            assert ref.doi is not None
            return f"{ref.title} ({ref.venue}, under review). doi.org/{ref.doi}"
    raise ValueError(f"unknown status: {ref.status}")


def format_listing(ref: Ref) -> str:
    """One reference as a line in the publication list on slide 2.

    Venue first — that is what the audience scans for — then the full title and
    the DOI, following the outline's own layout. Nothing is abbreviated.
    """
    if ref.doi is None:
        return f"{ref.venue} — {ref.title}"
    # Zenodo DOIs share a 15-character prefix that carries no information on a
    # slide where thirteen of them appear; the record id is what identifies the
    # paper. Footnotes still print the resolvable doi.org form.
    doi = ref.doi
    if doi.startswith(ZENODO_PREFIX):
        doi = f"zenodo.{doi[len(ZENODO_PREFIX):]}"
    else:
        doi = f"doi.org/{doi}"
    qualifier = "in press; " if ref.status == "in_press" else ""
    inner = f"{qualifier}{doi}"
    if ref.note:
        inner += f"; {ref.note}"
    return f"{ref.venue} — {ref.title} ({inner})"


def format_footer(ids: tuple[str, ...]) -> str:
    """The footnote line for one slide."""
    return "  ·  ".join(format_ref(REFS[i]) for i in ids)


def format_ref_list(ids: tuple[str, ...] | None = None) -> tuple[str, ...]:
    """Every reference as its own line, for the closing slide."""
    keys = ids if ids is not None else tuple(REFS)
    return tuple(format_ref(REFS[k]) for k in keys)
