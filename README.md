# Redefining Artificial Superintelligence

Slides, speaker script, and the generator that builds them, prepared for a talk
accepted to the **Superintelligence Conference 2026 (SiC26)**, Day 1, Session 1
— *Defining and Evaluating Superintelligence* — 9 September 2026, University of
Exeter.

The argument itself is published; see the papers below.

* Programme: <https://www.superintelligenceconference.org/programme/2026>
* Paper: *Redefining Artificial Superintelligence: From Mystified Genius to
  Observable Conditions* (August 2026) —
  [10.5281/zenodo.21782594](https://doi.org/10.5281/zenodo.21782594)
* Follow-up: *Continuous Novel Discovery: Re-engineering Artificial
  Superintelligence Through Observable Conditions — Background: The Four
  Conditions* (September 2026) —
  [10.5281/zenodo.22683524](https://doi.org/10.5281/zenodo.22683524)
* OpenReview: <https://openreview.net/forum?id=lLWeptkTPH>

Author: Franny Philos Sophia, Elanare Institute
(ORCID [0009-0004-7089-5265](https://orcid.org/0009-0004-7089-5265))

## The argument

Existing definitions of superintelligence measure it against "the best human
minds" — a baseline that was never measured and cannot be. The IQ figures
attached to von Neumann (~190) and Ramanujan (185+) are retrospective estimates,
not measurements; von Neumann's measured score as a student was 125.

The talk relocates the boundary conditions from the human upper limit to the
current capability limits of AI, which yields four conditions. Speed and
collective intelligence are already achieved. Scientific creativity and general
wisdom under complexity are not — and they are independent axes, not points on
one scaling curve.

ASI is then defined as the ability to *continuously* make novel discoveries,
update knowledge, and go on surpassing humans — which requires both a cognitive
layer that can generate new meaning and a physical layer that constrains it.

## What is here

| Path | |
| --- | --- |
| `SiC26_Sophia.pptx` | The deck as delivered (hand-finished after generation) |
| `SiC26_Sophia.docx` | Speaker script — what to say, and the transition, per slide |
| `sic26_presentation_final.md` | The outline the deck is built from |
| `SPEC_final.md` | Deck specification and layout rules |
| `slides/` | Generator: content as data, rendered to pptx |
| `tests/` | 119 tests over content, references, layout and the rendered file |
| `assets/` | The five figures |

## Building

Requires [uv](https://docs.astral.sh/uv/).

```sh
uv run python build.py            # writes build/SiC26_Sophia.pptx
uv run python build.py --preview  # also rasterises each slide to PNG
uv run pytest                     # 119 tests
```

Nothing is written unless every readability check passes — a deck that overflows
its own boxes is worse than no deck at all. `build.py --preview` needs Keynote
(preferred) or LibreOffice to rasterise.

Note that `build.py` reproduces the *generated* deck, not the delivered one:
slide 21's diagram was added by hand in PowerPoint and lives only in
`SiC26_Sophia.pptx`.

## Notes on the generator

The deck is drawn element by element on a blank layout. Built-in placeholders
inherit fonts and sizes from the PowerPoint theme, which would defeat both the
font policy and the overflow checks.

Two decisions are worth knowing before editing:

* **Body text is scaled per slide** (`slides/validate.py:fitted_scale`) so a
  short slide fills its space instead of floating in the top third. Growth only
  — shrinking to fit would silently defeat the overflow checks — and capped
  below the title size so the hierarchy cannot invert.
* **The width estimator is deliberately pessimistic** (`AVG_CHAR_EM = 0.575`).
  On a column of long paper titles it over-predicts height by ~15%, which is why
  the publication slide's byline is positioned from a measurement of the render
  rather than from the estimate. It is accurate elsewhere, so the constant is
  left alone.

Content follows the outline verbatim, including its arrows, equals signs and
parentheticals. The outline's phrasing is the specification; `tests/` enforces
that, along with the no-hedging rule the outline states for itself.

## What is not here

Manuscripts under review are not in this repository. The deck cites every paper
by DOI; preprints are on Zenodo.

## Citing

```bibtex
@misc{sophia2026redefining,
  author = {Sophia, Franny Philos},
  title  = {Redefining Artificial Superintelligence: From Mystified Genius
            to Observable Conditions},
  year   = {2026},
  publisher = {Zenodo},
  doi    = {10.5281/zenodo.21782594},
  url    = {https://doi.org/10.5281/zenodo.21782594}
}
```

## License

Code — `slides/`, `tests/`, `build.py` — under the [MIT License](LICENSE).

Presentation content — slides, script, prose and figures — under
[CC BY 4.0](LICENSE-CONTENT).
