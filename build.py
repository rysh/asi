#!/usr/bin/env python3
"""Build the SiC26 deck.

Nothing is written unless every readability check passes: a deck that
overflows its own boxes is worse than no deck at all.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from slides.content import SLIDES
from slides.render import render_deck
from slides.validate import check_all

BUILD = Path(__file__).parent / "build"
PPTX = BUILD / "SiC26_Sophia.pptx"
PREVIEW = BUILD / "preview"


def build() -> int:
    violations = check_all(SLIDES)
    if violations:
        for v in violations:
            print(f"slide {v.slide}: {v.rule}: {v.detail}", file=sys.stderr)
        print(f"\n{len(violations)} violation(s); nothing written.", file=sys.stderr)
        return 1

    BUILD.mkdir(exist_ok=True)
    render_deck(SLIDES).save(PPTX)
    total = sum(s.budget_sec for s in SLIDES)
    print(f"{PPTX}  ({len(SLIDES)} slides, {total // 60}:{total % 60:02d} budgeted)")
    return 0


SOFFICE = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")
KEYNOTE = Path("/Applications/Keynote.app")

KEYNOTE_SCRIPT = """
tell application "Keynote"
    set d to open POSIX file "{pptx}"
    export d to POSIX file "{pdf}" as PDF
    close d saving no
end tell
"""


def _export_pdf(pdf: Path) -> str | None:
    """Render the deck to PDF. Returns an error message, or None on success.

    Keynote is preferred despite needing the GUI: it resolves macOS fonts the
    way the talk will actually be shown, and it is the only path here that
    draws the Japanese in slide 14. This LibreOffice install sees no CJK face
    at all and silently drops those glyphs, so it is a fallback for layout
    checks only.
    """
    if KEYNOTE.exists():
        # Launching first makes the export script far less likely to stall
        # behind a first-run dialog.
        subprocess.run(["open", "-g", "-a", "Keynote"], capture_output=True)
        result = subprocess.run(
            ["osascript", "-e", KEYNOTE_SCRIPT.format(pptx=PPTX, pdf=pdf)],
            capture_output=True, text=True, timeout=300,
        )
        if pdf.exists():
            return None
        keynote_error = result.stderr.strip() or "no output"
    else:
        keynote_error = "Keynote not installed"

    if SOFFICE.exists():
        result = subprocess.run(
            [str(SOFFICE), "--headless", "--convert-to", "pdf",
             "--outdir", str(pdf.parent), str(PPTX)],
            capture_output=True, text=True, timeout=300,
        )
        produced = pdf.parent / f"{PPTX.stem}.pdf"
        if produced.exists():
            produced.replace(pdf)
            print(f"note: Keynote unavailable ({keynote_error}); used LibreOffice, "
                  "which does not render the Japanese on slide 14.", file=sys.stderr)
            return None
        return f"LibreOffice failed: {result.stderr.strip() or result.stdout.strip()}"

    return f"no converter available (Keynote: {keynote_error})"


def preview() -> int:
    """Rasterise each slide so the layout can be inspected."""
    if not PPTX.exists():
        print("build the deck first", file=sys.stderr)
        return 1

    PREVIEW.mkdir(parents=True, exist_ok=True)
    pdf = PREVIEW / "deck.pdf"
    if pdf.exists():
        pdf.unlink()

    error = _export_pdf(pdf)
    if error:
        print(error, file=sys.stderr)
        return 1

    import pymupdf

    doc = pymupdf.open(pdf)
    for old in PREVIEW.glob("slide-*.png"):
        old.unlink()
    for i, page in enumerate(doc, start=1):
        page.get_pixmap(dpi=110).save(PREVIEW / f"slide-{i:02d}.png")
    print(f"{doc.page_count} page(s) -> {PREVIEW}/slide-NN.png")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true",
                        help="also rasterise the deck via Keynote")
    args = parser.parse_args()
    code = build()
    if code or not args.preview:
        return code
    return preview()


if __name__ == "__main__":
    raise SystemExit(main())
