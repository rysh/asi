"""The registry is the deck's factual anchor: these tests pin the DOIs and the
citation form that follows from each publication status.

Every under-review entry now carries its preprint DOI — the outline cites one
for all ten — so the old "no DOI until published" rule no longer holds.
"""

import re

import pytest

from slides.refs import (
    FOOTNOTED,
    PUBLISHED,
    REFS,
    UNDER_REVIEW,
    Ref,
    format_footer,
    format_listing,
    format_ref,
    format_ref_list,
)

VERIFIED_DOIS = {
    "control_imposs": "10.5281/zenodo.19943538",
    "exec_governance": "10.5281/zenodo.19429152",
    "seci": "10.5281/zenodo.21293879",
    "interoception": "10.5281/zenodo.19942221",
    "emergence_dichotomy": "10.5281/zenodo.21319707",
    "fugitive_cash": "10.5281/zenodo.21759090",
    "dynamic_emergence": "10.5281/zenodo.18074645",
    "lost_abduction": "10.5281/zenodo.20005937",
    "active_inference": "10.5281/zenodo.18017028",
    "manifold": "10.5281/zenodo.20642039",
    "processing_speed": "10.5281/zenodo.19105953",
    "who_are_we": "10.5281/zenodo.17745229",
    "intention": "10.5281/zenodo.19234682",
    "conservation": "10.5281/zenodo.21000863",
    "gen_contradiction": "10.5281/zenodo.21612954",
    "mishima": "10.5281/zenodo.20489614",
    "centaur": "10.5281/zenodo.18733027",
}


@pytest.mark.parametrize("key,doi", VERIFIED_DOIS.items())
def test_verified_dois_are_exact(key, doi):
    assert REFS[key].doi == doi


def test_zenodo_dois_are_well_formed():
    for key, ref in REFS.items():
        if ref.doi and ref.doi.startswith("10.5281"):
            assert re.fullmatch(r"10\.5281/zenodo\.\d+", ref.doi), key


def test_published_journal_dois_are_not_zenodo():
    """The two actually-published journal papers cite the publisher DOI."""
    assert REFS["logic_trap"].doi == "10.1007/s43681-026-01148-6"
    assert REFS["brachiation"].doi == "10.1016/j.jbmt.2026.03.008"


def test_every_ref_except_the_paper_link_has_a_doi():
    for key, ref in REFS.items():
        if ref.status == "url":
            assert ref.doi is None and ref.url, key
        else:
            assert ref.doi, key


def test_under_review_refs_render_the_venue_and_status():
    for key, ref in UNDER_REVIEW.items():
        rendered = format_ref(ref)
        assert f"({ref.venue}, under review)" in rendered, key
        assert "doi.org/" in rendered, key


def test_centaur_is_in_press():
    ref = REFS["centaur"]
    assert ref.status == "in_press"
    assert "(CACM, in press)" in format_ref(ref)


def test_registry_partitions_cleanly():
    assert len(REFS) == len(PUBLISHED) + len(UNDER_REVIEW) + len(FOOTNOTED)
    assert not (set(PUBLISHED) & set(UNDER_REVIEW))
    assert not (set(PUBLISHED) & set(FOOTNOTED))
    assert not (set(UNDER_REVIEW) & set(FOOTNOTED))


def test_openreview_url():
    assert REFS["main_paper"].url == "https://openreview.net/forum?id=lLWeptkTPH"


def test_format_ref_doi_form():
    assert format_ref(REFS["intention"]) == (
        "Intention Without Causation. doi.org/10.5281/zenodo.19234682"
    )


def test_format_footer_joins_with_separator():
    out = format_footer(("intention", "conservation"))
    assert out.count("·") == 1
    assert out.count("doi.org/") == 2


def test_format_listing_leads_with_the_venue_and_carries_the_doi():
    assert format_listing(REFS["manifold"]) == (
        "Neural Computation — When the Manifold Collapses: A Geometric Theory "
        "of Constraint Conflict in Large Language Models (zenodo.20642039)"
    )


def test_listing_shortens_only_the_shared_zenodo_prefix():
    """Non-Zenodo DOIs have no prefix to drop, so they stay resolvable."""
    assert "doi.org/10.1007/s43681-026-01148-6" in format_listing(REFS["logic_trap"])


def test_listings_are_never_abbreviated():
    """Titles are cited in full everywhere; no abbreviation mechanism exists."""
    assert not hasattr(REFS["emergence_dichotomy"], "short")
    for key, ref in REFS.items():
        if ref.status != "url":
            assert ref.title in format_listing(ref), key


def test_every_listed_paper_shows_its_doi():
    for key, ref in {**PUBLISHED, **UNDER_REVIEW}.items():
        record = ref.doi.rsplit(".", 1)[-1] if ref.doi else ""
        assert record and record in format_listing(ref), key


def test_footnotes_keep_the_resolvable_doi_form():
    """Shortening is a slide-listing concern only."""
    for key, ref in UNDER_REVIEW.items():
        assert f"doi.org/{ref.doi}" in format_ref(ref), key


def test_in_press_listing_marks_the_paper_as_in_press():
    assert "(in press; zenodo.18733027)" in format_listing(REFS["centaur"])


def test_brachiation_listing_keeps_its_pubmed_id():
    assert format_listing(REFS["brachiation"]).endswith(
        "(doi.org/10.1016/j.jbmt.2026.03.008; PubMed 42264802)"
    )


def test_footnotes_always_use_the_full_title():
    """A footnote cites the paper as Zenodo lists it, in full."""
    ref = REFS["lost_abduction"]
    assert ref.title in format_ref(ref)
    assert "Toward a Completion Model of Science Communication" in format_ref(ref)


def test_format_ref_list_covers_every_entry():
    assert len(format_ref_list()) == len(REFS)


def test_no_delta_problem_entry():
    """delta_problem.pdf is the anonymous earlier version of lost_abduction;
    citing both would double-count one work."""
    joined = " ".join(format_ref_list()).lower()
    assert "delta problem" not in joined


def test_unknown_status_rejected():
    with pytest.raises(ValueError):
        format_ref(Ref(title="x", venue="y", status="bogus"))  # type: ignore[arg-type]
