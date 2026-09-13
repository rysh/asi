"""What this deck must say, and must not say.

The spec is sic26_presentation_final.md and SPEC_final.md; these tests follow
those, not the implementation. Where a test pins a phrase, the phrase is one
the outline itself commits to — so a silent reword of an argument fails here.
"""

import re

import pytest

from slides.content import SLIDES
from slides.model import Bullets, Image, Slide, slide_texts
from slides.refs import PUBLISHED, REFS, UNDER_REVIEW
from slides.shapes import FOUR_CONDITIONS
from slides.validate import check_all

DECK_TEXT = " ".join(t for s in SLIDES for t in slide_texts(s))


def by_number(n: int) -> Slide:
    return next(s for s in SLIDES if s.number == n)


def by_title(fragment: str) -> Slide:
    matches = [s for s in SLIDES if fragment.lower() in s.title.lower()]
    assert len(matches) == 1, f"{fragment!r} matched {len(matches)} slides"
    return matches[0]


# --- structure ------------------------------------------------------------

def test_deck_has_twenty_nine_slides():
    assert len(SLIDES) == 29


def test_slide_numbers_are_contiguous():
    assert [s.number for s in SLIDES] == list(range(1, 30))


def test_the_agenda_names_every_section():
    """The agenda is the reader's map; a section missing from it is a section
    the audience cannot navigate to."""
    agenda = by_title("Where This Talk Goes")
    text = " ".join(slide_texts(agenda))
    for section in SECTIONS:
        # The agenda spaces the numeral for legibility ("1.  The Genius…").
        assert section.replace(". ", ".  ") in text, section


def test_the_preprint_note_sits_on_the_title_slide():
    title = by_number(1)
    text = " ".join(slide_texts(title))
    assert "All footnoted DOIs refer to preprints" in text


def test_the_author_list_is_one_slide():
    authored = [s for s in SLIDES if "About the Author" in s.title]
    assert len(authored) == 1
    assert authored[0].wide, "the full-title list needs the wide layout"


def test_every_slide_has_a_title():
    assert all(s.title.strip() for s in SLIDES)


def test_timing_budget_is_exactly_twenty_minutes():
    assert sum(s.budget_sec for s in SLIDES) == 20 * 60


def test_deck_renders_without_readability_violations():
    assert check_all(SLIDES) == ()


def test_every_reference_id_is_registered():
    for s in SLIDES:
        for r in s.refs:
            assert r in REFS, f"slide {s.number} cites unknown ref {r!r}"


# --- the seven sections appear as kickers, in order -----------------------

SECTIONS = (
    "1. The Genius Problem and IQ",
    "2. Critique of Existing Definitions",
    "3. Four Conditions and Discussion",
    "4. Defining ASI",
    "5. What Is AGI?",
    "6. The Path to Scientific Creativity",
    "7. Synthesis",
)


def test_sections_open_in_order():
    """The kicker also carries non-section context (slide 2's byline), so this
    checks the section markers specifically, in order and each used once."""
    kickers = [s.kicker for s in SLIDES if s.kicker in SECTIONS]
    assert kickers == list(SECTIONS)


# --- the arguments the outline commits to --------------------------------

def test_genius_iq_values_are_named_as_extrapolations():
    s = by_title("Mystification of Genius")
    text = " ".join(slide_texts(s))
    assert "Von Neumann ~190, Ramanujan ~185+" in text
    assert "not measured values" in text


def test_the_goal_does_not_exist():
    s = by_title("Goal That Does Not Exist")
    text = " ".join(slide_texts(s))
    assert "has no baseline — it is undefinable" in text
    assert "Human cognitive ability has no fixed upper bound" in text


def test_bostrom_speed_and_collective_are_already_achieved():
    s = by_title("Bostrom")
    assert any("Speed and Collective are already achieved" in t
               for t in slide_texts(s))


def test_legg_hutter_is_rejected_as_incomputable():
    s = by_title("Legg & Hutter")
    text = " ".join(slide_texts(s))
    assert "Incomputable by the authors' own admission" in text
    assert "A definition that cannot be computed is not a definition" in text


def test_chollet_definition_was_reverse_engineered():
    s = by_title("Chollet")
    text = " ".join(slide_texts(s))
    assert "Spelke's Core Knowledge" in text
    assert "The definition was reverse-engineered to match the benchmark" in text


def test_goertzel_agi_and_asi_are_qualitatively_different():
    s = by_title("Goertzel")
    text = " ".join(slide_texts(s))
    assert "reframing (adaptation) vs. abduction (generation)" in text


def test_baseline_moves_to_the_ai_side():
    s = by_title("Calibrating the Definition")
    text = " ".join(slide_texts(s))
    assert "the current capability limits of AI" in text
    assert "This decomposition was impossible in 2014. It is possible now, in 2026" in text


def test_four_conditions_are_two_met_and_two_unmet():
    met = [c for c in FOUR_CONDITIONS if c[1]]
    unmet = [c for c in FOUR_CONDITIONS if not c[1]]
    assert len(met) == 2 and len(unmet) == 2
    names = {c[0] for c in FOUR_CONDITIONS}
    assert "SPEED" in names and "COLLECTIVE INTELLIGENCE" in names
    assert "SCIENTIFIC CREATIVITY" in {c[0] for c in unmet}


def test_abduction_is_the_only_inference_that_introduces_a_new_idea():
    s = by_title("No Abduction")
    text = " ".join(slide_texts(s))
    assert "deduction" in text and "induction" in text
    assert "Peirce" in text


def test_scaling_cannot_reach_conditions_three_and_four():
    s = by_title("Scaling Is Dead")
    assert "Scaling cannot achieve Condition 3 or Condition 4" in slide_texts(s)


def test_speed_and_accuracy_are_only_prerequisites():
    s = by_title("Only Prerequisites")
    text = " ".join(slide_texts(s))
    assert "AlphaFold, GraphCast, medical imaging" in text
    assert "But none produce new knowledge" in text


def test_asi_is_defined_as_continuous_novel_discovery():
    s = by_title("Continuous Novel Discovery")
    text = " ".join(slide_texts(s))
    assert "continuously make novel discoveries and inventions, update knowledge, and surpass humans" in text


def test_general_is_not_universal():
    s = by_title("General Does Not Mean Universal")
    text = " ".join(slide_texts(s))
    assert "That is execution, not adaptation" in text


def test_agi_reframes_and_asi_abducts():
    s = by_title("Distinction Between AGI and ASI")
    text = " ".join(slide_texts(s))
    assert "(reframing)" in text and "(abduction)" in text
    assert "Rearranging and generating are different" in text


def test_novelty_is_killed_by_the_systems_own_verification():
    s = by_title("Cannot Judge the Truth")
    assert "New ideas are killed by the system's own verification" in slide_texts(s)


def test_language_is_a_compression_of_the_world():
    s = by_title("In the Beginning Was the Word")
    text = " ".join(slide_texts(s))
    assert "Hermeticism" in text
    assert "Language is a compression of the world, not the world itself" in text


def test_godel_is_read_as_infinite_progression():
    s = by_title("Generation of New Meaning")
    text = " ".join(slide_texts(s))
    assert "infinite regression" in text, "the standard reading must be stated"
    assert "infinite progression" in text, "the author's reading must be stated"
    assert "Meaning has no conservation law" in text


def test_thanatos_frames_the_scaling_question_as_a_disjunction():
    s = by_title("Truth Found or Made")
    text = " ".join(slide_texts(s))
    assert "Mishima Yukio's seppuku (1970)" in text and "undead concept" in text
    assert "If the former is correct, scaling can reach ASI. If the latter, it is entirely impossible" in text


def test_both_layers_are_required_for_scientific_creativity():
    s = by_title("Going Outside Language")
    text = " ".join(slide_texts(s))
    assert "Observation is the only access" in text
    assert "both the cognitive and physical layers are in place" in text


def test_closing_slide_carries_contact_and_openreview():
    s = by_number(29)
    text = " ".join(slide_texts(s))
    assert "franny.philos.sophia@elanare.jp" in text
    assert "0009-0004-7089-5265" in text
    assert "openreview.net/forum?id=lLWeptkTPH" in text
    assert "counterexamples are especially welcome" in text


# --- figures --------------------------------------------------------------

FIGURE_KEYS = ("axes", "triangle", "loop6", "ecosystem", "compare")


def test_the_five_figures_are_placed():
    keys = [s.body.key for s in SLIDES if isinstance(s.body, Image)]
    assert keys == ["axes", "triangle", "loop6", "ecosystem", "compare"]


@pytest.mark.parametrize("key", FIGURE_KEYS)
def test_every_figure_file_exists(key):
    from slides.images import asset_path

    assert asset_path(key) is not None, f"assets/{key}.png is missing"


# --- the outline's stated principle ---------------------------------------

HEDGES = (
    "arguably", "perhaps", "it seems", "somewhat", "we believe",
    "may suggest", "might suggest", "to some extent", "it could be argued",
)


def test_no_hedging():
    """The outline forbids hedging and academic disclaimers outright."""
    lowered = DECK_TEXT.lower()
    found = [h for h in HEDGES if h in lowered]
    assert not found, f"hedging in the deck: {found}"


def test_bullets_are_not_isolated_words():
    """“No bullet-point lists of isolated words.”

    Kept deliberately crude: no heuristic short of parsing tells a claim from
    a noun phrase, and the outline's bullets range from “Incomputable by the
    authors' own admission” to full sentences. A length floor catches the
    failure this rule is actually about — a slide of one- and two-word stubs —
    without second-guessing the author's phrasing. The publication lists are
    exempt; those are titles.
    """
    from slides.model import bullets_of

    for s in SLIDES:
        if s.dense or not isinstance(s.body, Bullets):
            continue
        for b in bullets_of(s.body):
            assert len(b.text.split()) >= 4, (
                f"slide {s.number}: bullet is an isolated phrase: {b.text!r}"
            )


# --- publication list -----------------------------------------------------

def test_publication_counts_match_the_outline():
    assert len(PUBLISHED) == 3
    assert len(UNDER_REVIEW) == 10


def test_every_under_review_paper_carries_its_preprint_doi():
    for key, ref in UNDER_REVIEW.items():
        assert ref.doi and ref.doi.startswith("10.5281/zenodo."), key


ZENODO_FULL_TITLES = {
    "10.5281/zenodo.19942221":
        "Brain Interoception: The Missing Organ on the Interoceptive Map",
    "10.5281/zenodo.21319707":
        "Emergence Without the Dichotomy",
    "10.5281/zenodo.21759090":
        "From Fugitive Cash to Non-Fugitive Provisioning: The Mundellian "
        "Trilemma, External Debt Feedback, and the Design Space of "
        "Post-Employment Redistribution",
    "10.5281/zenodo.18074645":
        "Dynamic Emergence: A Unified Theory Based on the Stuart-Landau Equation",
    "10.5281/zenodo.20005937":
        "Lost Abduction and Epistemic Barriers: Toward a Completion Model of "
        "Science Communication",
    "10.5281/zenodo.18017028":
        "From Instability to Active Inference: A Unified Mathematical Framework "
        "for Biological Self-Organization across Scales",
    "10.5281/zenodo.20642039":
        "When the Manifold Collapses: A Geometric Theory of Constraint Conflict "
        "in Large Language Models",
}


@pytest.mark.parametrize("doi,title", sorted(ZENODO_FULL_TITLES.items()))
def test_titles_match_the_zenodo_landing_pages(doi, title):
    """Fetched from doi.org and pinned here so an abbreviation cannot creep back."""
    matches = [r for r in REFS.values() if r.doi == doi]
    assert len(matches) == 1, doi
    assert matches[0].title == title
