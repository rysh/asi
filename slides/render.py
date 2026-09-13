"""Slide -> pptx. The only module that imports python-pptx.

Every element is placed by hand on a blank layout. Built-in placeholders
inherit fonts and sizes from the PowerPoint theme, which defeats both the
font policy and the overflow checks in validate.py.
"""

from __future__ import annotations

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

from slides.geometry import (
    COL_GAP,
    Rect,
    WIDE_COL_GAP,
    wide_body_rect,
    body_rect,
    caveat_rect,
    column_head_and_body,
    footer_rect,
    kicker_rect,
    page_rect,
    title_block_rects,
    title_rect,
    two_columns,
)
from slides.images import placement
from slides.model import (
    Bullet,
    Bullets,
    ContactBlock,
    Diagram,
    Image,
    QuoteBlock,
    Slide,
    TitleBlock,
    TwoColumn,
)
from slides.refs import format_footer, format_ref_list
from slides.validate import (
    PT_PER_INCH,
    _image_area,
    block_height_pt,
    body_scale,
    image_caption_pt,
    quote_band_pt,
)
from slides.shapes import ShapeKind, ShapeSpec, diagram_specs
from slides.theme import SLIDE_H, SLIDE_W, THEME, Theme, body_pt, inches

ALIGN = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}
BULLET_INDENT = inches(0.3)
# Where a prominent caveat begins. Measured from the rendered deck: the
# shorter column of the publication list ends here, so the band below it is
# genuinely free even though the width estimator is too pessimistic to say so.
CAVEAT_PROMINENT_TOP_IN = 6.35


def _rgb(hex_str: str) -> RGBColor:
    return RGBColor.from_string(hex_str)


def _pt_to_emu(pt: float) -> int:
    return int(pt / PT_PER_INCH * inches(1))


def _set_font(run, theme: Theme, pt: int, color: str, bold: bool = False,
              italic: bool = False) -> None:
    """Pin the run font explicitly.

    python-pptx writes only `a:latin`; the complementary faces are set here so
    no renderer falls back to its own theme default.
    """
    run.font.size = Pt(pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = theme.font_latin
    run.font.color.rgb = _rgb(color)

    rpr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        existing = rpr.find(qn(tag))
        if existing is not None:
            rpr.remove(existing)
        rpr.append(rpr.makeelement(qn(tag), {"typeface": theme.font_latin}))


def _textbox(slide, rect: Rect, *, anchor=MSO_ANCHOR.TOP, wrap: bool = True):
    box = slide.shapes.add_textbox(
        Emu(rect.left), Emu(rect.top), Emu(rect.width), Emu(rect.height)
    )
    tf = box.text_frame
    tf.word_wrap = wrap
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return box, tf


def _write(tf, lines, theme: Theme, *, pt: int, color: str, bold: bool = False,
           italic: bool = False, align: str = "left", space_after: int = 0) -> None:
    """Fill a text frame with (text, pt, color, bold, italic, indent) tuples."""
    first = True
    for spec in lines:
        text, l_pt, l_color, l_bold, l_italic, indent = spec
        para = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        para.alignment = ALIGN[align]
        para.space_after = Pt(space_after)
        if indent:
            # python-pptx exposes no indent API; the default level indent is
            # far deeper than this layout wants.
            ppr = para._p.get_or_add_pPr()
            ppr.set("marL", str(BULLET_INDENT * indent))
            ppr.set("indent", "0")
        run = para.add_run()
        run.text = text
        _set_font(run, theme, l_pt, l_color, l_bold, l_italic)


def _simple(tf, text: str, theme: Theme, *, pt: int, color: str, bold: bool = False,
            italic: bool = False, align: str = "left") -> None:
    _write(tf, [(text, pt, color, bold, italic, 0)], theme, pt=pt, color=color,
           align=align)


def _bullet_lines(items: tuple[Bullet, ...], theme: Theme, dense: bool,
                  scale: float = 1.0):
    for b in items:
        pt = body_pt(b.level, theme, dense, scale)
        color = theme.accent if b.emphasis else theme.text
        prefix = "" if b.level == 0 else "— "
        yield (prefix + b.text, pt, color, b.emphasis, False, b.level)


def _draw_bullets(slide, rect: Rect, items: tuple[Bullet, ...], theme: Theme,
                  dense: bool, anchor=MSO_ANCHOR.TOP, scale: float = 1.0) -> None:
    if not items:
        return
    _, tf = _textbox(slide, rect, anchor=anchor)
    _write(tf, list(_bullet_lines(items, theme, dense, scale)), theme,
           pt=theme.l0_pt, color=theme.text,
           space_after=int(round(7 * scale)))


def _draw_shape(slide, spec: ShapeSpec, theme: Theme) -> None:
    if spec.kind is ShapeKind.LABEL:
        _, tf = _textbox(slide, Rect(spec.left, spec.top, spec.width, spec.height),
                         anchor=MSO_ANCHOR.MIDDLE)
        lines = [
            (line, spec.font_pt, spec.text_color or theme.text, spec.bold, False, 0)
            for line in spec.text.split("\n")
        ]
        _write(tf, lines, theme, pt=spec.font_pt,
               color=spec.text_color or theme.text, align=spec.align, space_after=1)
        return

    auto = {
        ShapeKind.ROUNDED_BOX: MSO_SHAPE.ROUNDED_RECTANGLE,
        ShapeKind.BOX: MSO_SHAPE.RECTANGLE,
        ShapeKind.OVAL: MSO_SHAPE.OVAL,
        ShapeKind.RULE: MSO_SHAPE.RECTANGLE,
        ShapeKind.DASHED_RULE: MSO_SHAPE.RECTANGLE,
        ShapeKind.ARROW: MSO_SHAPE.RIGHT_ARROW,
    }[spec.kind]

    shape = slide.shapes.add_shape(
        auto, Emu(spec.left), Emu(spec.top), Emu(spec.width), Emu(spec.height)
    )
    shape.shadow.inherit = False
    if spec.kind is ShapeKind.ROUNDED_BOX:
        shape.adjustments[0] = 0.08

    if spec.fill:
        shape.fill.solid()
        shape.fill.fore_color.rgb = _rgb(spec.fill)
    else:
        shape.fill.background()

    if spec.kind is ShapeKind.DASHED_RULE:
        # Drawn as a dashed outline rather than a filled bar, so it reads as a
        # threshold rather than another box edge.
        shape.fill.background()
        shape.line.color.rgb = _rgb(spec.fill or theme.accent)
        shape.line.width = Pt(1.5)
        shape.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    elif spec.line:
        shape.line.color.rgb = _rgb(spec.line)
        shape.line.width = Pt(1.25)
    else:
        shape.line.fill.background()

    if spec.text:
        tf = shape.text_frame
        tf.word_wrap = True
        tf.auto_size = MSO_AUTO_SIZE.NONE
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        _simple(tf, spec.text, theme, pt=spec.font_pt,
                color=spec.text_color or theme.text, bold=spec.bold,
                align=spec.align)
    else:
        # A shape with no text still carries an empty run; strip its default font.
        shape.text_frame.paragraphs[0].alignment = ALIGN[spec.align]


# --- body renderers -------------------------------------------------------

def _render_title_block(slide, body: TitleBlock, theme: Theme) -> None:
    t_rect, a_rect, m_rect = title_block_rects()

    _, tf = _textbox(slide, t_rect)
    _write(
        tf,
        [
            (body.title, 40, theme.text, True, False, 0),
            (body.subtitle, 24, theme.accent, False, True, 0),
        ],
        theme, pt=40, color=theme.text, space_after=10,
    )

    _, tf = _textbox(slide, a_rect)
    _write(
        tf,
        [
            (body.author, 22, theme.text, True, False, 0),
            (body.affiliation, 18, theme.muted, False, False, 0),
        ],
        theme, pt=22, color=theme.text, space_after=4,
    )

    _, tf = _textbox(slide, m_rect)
    _write(
        tf,
        [(line, theme.meta_pt, theme.muted, False, False, 0) for line in body.meta],
        theme, pt=theme.meta_pt, color=theme.muted, space_after=5,
    )


def _render_two_column(slide, body: TwoColumn, rect: Rect, theme: Theme,
                       dense: bool, gap: int = COL_GAP) -> None:
    left_col, right_col = two_columns(rect, gap)
    for col, head, items in (
        (left_col, body.left_head, body.left),
        (right_col, body.right_head, body.right),
    ):
        head_rect, body_r = column_head_and_body(col)
        _, tf = _textbox(slide, head_rect)
        _simple(tf, head, theme, pt=theme.head_pt, color=theme.accent, bold=True)
        _draw_bullets(slide, body_r, items, theme, dense)



def _render_quote(slide, body: QuoteBlock, rect: Rect, theme: Theme,
                  dense: bool) -> None:
    cursor = rect.top

    if body.lead:
        # Measure the lead rather than assuming a fixed height: a two-line
        # lead and a five-line one must both clear the quote below.
        h = _pt_to_emu(
            block_height_pt(body.lead, rect.width, theme, dense, BULLET_INDENT)
        )
        _draw_bullets(slide, Rect(rect.left, cursor, rect.width, h), body.lead,
                      theme, dense)
        cursor += h + _pt_to_emu(
            block_height_pt((), rect.width, theme, dense, BULLET_INDENT)
        ) + inches(theme.quote_gap_in)

    quote_h = _pt_to_emu(quote_band_pt(body.quote, rect.width, theme))
    bar = ShapeSpec(
        ShapeKind.BOX, rect.left, cursor, inches(0.05), quote_h,
        fill=theme.accent, tag="quotebar",
    )
    _draw_shape(slide, bar, theme)

    inner = Rect(rect.left + inches(0.26), cursor, rect.width - inches(0.26), quote_h)
    _, tf = _textbox(slide, inner, anchor=MSO_ANCHOR.MIDDLE)
    _write(
        tf,
        [
            (f"“{body.quote}”", theme.quote_pt, theme.text, False, True, 0),
            (f"— {body.attribution}", theme.meta_pt, theme.muted, False, False, 0),
        ],
        theme, pt=theme.quote_pt, color=theme.text, space_after=8,
    )
    cursor += quote_h + inches(theme.quote_gap_in)

    if body.follow:
        _draw_bullets(slide, Rect(rect.left, cursor, rect.width, rect.bottom - cursor),
                      body.follow, theme, dense)


def _render_diagram(slide, body: Diagram, rect: Rect, theme: Theme,
                    dense: bool) -> None:
    area = rect
    if body.lead:
        h = _pt_to_emu(
            block_height_pt(body.lead, rect.width, theme, dense, BULLET_INDENT)
        ) + inches(0.12)
        _draw_bullets(slide, Rect(rect.left, rect.top, rect.width, h), body.lead,
                      theme, dense)
        area = Rect(rect.left, rect.top + h, rect.width, rect.height - h)

    for spec in diagram_specs(body.kind, area, theme, body.lead):
        _draw_shape(slide, spec, theme)

    if body.caption:
        cap = Rect(area.left, area.bottom - inches(0.34), area.width, inches(0.34))
        _, tf = _textbox(slide, cap)
        _simple(tf, body.caption, theme, pt=theme.meta_pt, color=theme.muted,
                align="center")


def _render_image(slide, body: Image, rect: Rect, theme: Theme,
                  dense: bool) -> None:
    """Lead text, then the figure at its natural aspect ratio, then the caption."""
    if body.lead:
        lead_h = int(
            block_height_pt(body.lead, rect.width, theme, dense, BULLET_INDENT)
            / PT_PER_INCH * inches(1)
        )
        _draw_bullets(
            slide, Rect(rect.left, rect.top, rect.width, lead_h),
            body.lead, theme, dense,
        )

    area = _image_area(rect, body.lead, body.caption, theme, dense, BULLET_INDENT)
    path, box = placement(body.key, area)
    slide.shapes.add_picture(
        str(path), Emu(box.left), Emu(box.top), Emu(box.width), Emu(box.height)
    )

    if body.caption:
        cap_h = int(
            image_caption_pt(body.caption, rect.width, theme)
            / PT_PER_INCH * inches(1)
        )
        _, tf = _textbox(
            slide, Rect(rect.left, rect.bottom - cap_h, rect.width, cap_h),
            anchor=MSO_ANCHOR.BOTTOM,
        )
        _simple(tf, body.caption, theme, pt=theme.figure_caption_pt,
                color=theme.text)


def _render_contact(slide, body: ContactBlock, rect: Rect, theme: Theme) -> None:
    _, tf = _textbox(slide, Rect(rect.left, rect.top, rect.width, inches(1.1)))
    _simple(tf, body.summary, theme, pt=18, color=theme.text)

    top = rect.top + inches(1.3)
    left_w = rect.width * 46 // 100
    _, tf = _textbox(slide, Rect(rect.left, top, left_w, inches(1.9)))
    _write(
        tf,
        [
            (f"{label}    {value}", 16, theme.text, False, False, 0)
            for label, value in body.lines
        ],
        theme, pt=16, color=theme.text, space_after=9,
    )

    if body.ref_ids:
        ref_left = rect.left + left_w + inches(0.3)
        ref_rect = Rect(ref_left, top, rect.right - ref_left, inches(2.9))
        _, tf = _textbox(slide, ref_rect)
        _write(
            tf,
            [("Referenced in this talk", theme.footnote_pt, theme.accent,
              True, False, 0)]
            + [
                (line, theme.footnote_pt, theme.muted, False, False, 0)
                for line in format_ref_list(body.ref_ids)
            ],
            theme, pt=theme.footnote_pt, color=theme.muted, space_after=3,
        )

    closing = Rect(rect.left, rect.bottom - inches(0.6), rect.width, inches(0.5))
    _, tf = _textbox(slide, closing)
    _simple(tf, body.closing, theme, pt=18, color=theme.accent, bold=True)


# --- deck -----------------------------------------------------------------

def _paint_background(slide, theme: Theme) -> None:
    """Fill the slide with the template's diagonal teal-to-navy gradient.

    Drawn into the slide background rather than as a shape, so nothing sits in
    front of it and z-order stays free for the content.
    """
    bg = slide.background
    fill = bg.fill
    fill.gradient()
    fill.gradient_angle = 315.0
    stops = fill.gradient_stops
    stops[0].color.rgb = _rgb(theme.bg_from)
    stops[0].position = 0.0
    stops[1].color.rgb = _rgb(theme.bg_to)
    stops[1].position = 1.0


def _render_slide(prs, s: Slide, theme: Theme) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    _paint_background(slide, theme)
    has_footer = bool(s.refs)
    has_caveat = s.caveat is not None
    area = wide_body_rect() if s.wide else body_rect(has_footer, has_caveat)

    if not isinstance(s.body, TitleBlock):
        if s.kicker:
            _, tf = _textbox(slide, kicker_rect())
            _simple(tf, s.kicker, theme, pt=theme.kicker_pt, color=theme.muted)

        _, tf = _textbox(slide, title_rect())
        _simple(tf, s.title, theme, pt=theme.title_pt, color=theme.text, bold=True)

        rule = title_rect()
        _draw_shape(
            slide,
            ShapeSpec(ShapeKind.RULE, rule.left, rule.top + inches(0.56),
                      inches(1.1), inches(0.035), fill=theme.accent, tag="titlerule"),
            theme,
        )

    match s.body:
        case TitleBlock() as b:
            _render_title_block(slide, b, theme)
        case Bullets(items):
            _draw_bullets(slide, area, items, theme, s.dense,
                          scale=body_scale(s, theme))
        case TwoColumn() as b:
            _render_two_column(slide, b, area, theme, s.dense,
                               WIDE_COL_GAP if s.wide else COL_GAP)
        case QuoteBlock() as b:
            _render_quote(slide, b, area, theme, s.dense)
        case Diagram() as b:
            _render_diagram(slide, b, area, theme, s.dense)
        case Image() as b:
            _render_image(slide, b, area, theme, s.dense)
        case ContactBlock() as b:
            _render_contact(slide, b, area, theme)

    if has_caveat:
        assert s.caveat is not None
        if s.caveat_prominent:
            # Stands at the foot of the slide, under the shorter column, at
            # body weight. The columns are not shortened for it: it occupies
            # space the lists leave, which is why it is only offered where a
            # column actually ends high (see CAVEAT_PROMINENT_TOP_IN).
            band = Rect(
                area.left,
                inches(CAVEAT_PROMINENT_TOP_IN),
                area.width,
                SLIDE_H - inches(CAVEAT_PROMINENT_TOP_IN) - inches(0.3),
            )
            _, tf = _textbox(slide, band, anchor=MSO_ANCHOR.BOTTOM)
            _simple(tf, s.caveat, theme, pt=theme.column_note_pt,
                    color=theme.accent, bold=True)
        else:
            _, tf = _textbox(slide, caveat_rect(has_footer),
                             anchor=MSO_ANCHOR.BOTTOM)
            _simple(tf, s.caveat, theme, pt=theme.caveat_pt, color=theme.muted,
                    italic=True)

    if has_footer:
        _, tf = _textbox(slide, footer_rect(), anchor=MSO_ANCHOR.BOTTOM)
        _simple(tf, format_footer(s.refs), theme, pt=theme.footnote_pt,
                color=theme.muted)

    if s.number > 1:
        _, tf = _textbox(slide, page_rect(), anchor=MSO_ANCHOR.BOTTOM)
        _simple(tf, str(s.number), theme, pt=theme.page_pt, color=theme.muted,
                align="right")


def render_deck(slides: tuple[Slide, ...], theme: Theme = THEME) -> Presentation:
    prs = Presentation()
    prs.slide_width = Emu(SLIDE_W)
    prs.slide_height = Emu(SLIDE_H)
    for s in slides:
        _render_slide(prs, s, theme)
    return prs
