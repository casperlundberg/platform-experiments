"""Markdown in, PDF out: the layout half of a brief.

A brief is ordinary Markdown with a YAML header, plus three kinds of fenced
block that draw on the reports instead of restating them:

    ```chart        a figure from a report's runs (charts.py)
    ```table        a table lifted from a section of a report.md
    ```provenance   the builds behind every report the brief used

briefs/README.md is the reference for writing one. The output is deterministic:
the same brief at the same commits renders to the same bytes, because nothing
in it reads the clock and reportlab is run in its invariant mode.
"""

import os
import re
import tempfile
import unicodedata
from xml.sax.saxutils import escape

import matplotlib
import yaml
from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (BaseDocTemplate, Frame, HRFlowable, Image, KeepTogether, ListFlowable, ListItem,
                                PageBreak, PageTemplate, Paragraph, Preformatted, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

import charts
from sources import ROOT, BriefError, Reports, load_yaml, relative, resolve, stamp

INK = colors.HexColor("#0b0b0b")
SECONDARY = colors.HexColor("#52514e")
MUTED = colors.HexColor("#898781")
RULE = colors.HexColor("#c3c2b7")
HAIRLINE = colors.HexColor("#e1e0d9")
TINT = colors.HexColor("#f4f3ef")
ACCENT = colors.HexColor("#2a78d6")

PAGE = A4
MARGIN = 22 * mm

# From matplotlib's own data rather than the system, so a machine without them
# installed renders the same document. STIX carries the typography a report
# quotes (−, ×, ±, →, ≈, Greek); DejaVu Mono carries code.
FONTS = os.path.join(matplotlib.get_data_path(), "fonts", "ttf")
FAMILIES = {
    "Serif": ("STIXGeneral", "STIXGeneralBol", "STIXGeneralItalic", "STIXGeneralBolIta"),
    "Sans": ("DejaVuSans", "DejaVuSans-Bold", "DejaVuSans-Oblique", "DejaVuSans-BoldOblique"),
    "Mono": ("DejaVuSansMono", "DejaVuSansMono-Bold", "DejaVuSansMono-Oblique", "DejaVuSansMono-BoldOblique"),
}
DIRECTIVES = ("chart", "table", "provenance")
TABLE_KEYS = {"from", "section", "rows", "columns", "rename", "caption"}


def register_fonts():
    registered = set(pdfmetrics.getRegisteredFontNames())
    for family, files in FAMILIES.items():
        names = [family, family + "-Bold", family + "-Italic", family + "-BoldItalic"]
        for name, file in zip(names, files):
            if name not in registered:
                pdfmetrics.registerFont(TTFont(name, os.path.join(FONTS, file + ".ttf")))
        pdfmetrics.registerFontFamily(family, normal=names[0], bold=names[1], italic=names[2], boldItalic=names[3])


def style(name, **kw):
    base = dict(fontName="Serif", fontSize=10.5, leading=14.5, textColor=INK, spaceAfter=6)
    base.update(kw)
    return ParagraphStyle(name, **base)


STYLES = {
    "body": style("body"),
    "item": style("item", spaceAfter=2.5),
    "quote": style("quote", fontSize=10, leading=13.8, spaceAfter=4),
    "h1": style("h1", fontName="Sans-Bold", fontSize=14, leading=18, spaceBefore=16, spaceAfter=7, keepWithNext=1),
    "h2": style("h2", fontName="Sans-Bold", fontSize=11.2, leading=14.5, spaceBefore=12, spaceAfter=5,
                keepWithNext=1),
    "h3": style("h3", fontName="Serif-Bold", fontSize=10.5, leading=14, spaceBefore=8, spaceAfter=3, keepWithNext=1),
    "title": style("title", fontName="Sans-Bold", fontSize=21, leading=26, spaceAfter=8),
    "subtitle": style("subtitle", fontSize=13, leading=17, textColor=SECONDARY, spaceAfter=14),
    "meta": style("meta", fontSize=10.5, leading=14, textColor=SECONDARY, spaceAfter=2),
    "stamp": style("stamp", fontSize=8.5, leading=11, textColor=MUTED, spaceAfter=10),
    "caption": style("caption", fontSize=9, leading=11.8, textColor=SECONDARY, spaceBefore=3, spaceAfter=12),
    "tablecaption": style("tablecaption", fontSize=9, leading=11.8, textColor=SECONDARY, spaceBefore=4,
                          spaceAfter=4, keepWithNext=1),
    "code": style("code", fontName="Mono", fontSize=7.8, leading=10, spaceAfter=0),
    "contents": style("contents", fontName="Sans-Bold", fontSize=11.2, leading=14.5, spaceBefore=4, spaceAfter=6),
    "toc1": style("toc1", fontSize=10.5, leading=15, spaceAfter=0),
    "toc2": style("toc2", fontSize=9.5, leading=12.5, leftIndent=16, textColor=SECONDARY, spaceAfter=0),
}


class Glyphs:
    """Every run of text, checked against the face it is set in.

    A character a font lacks prints as a blank, silently. A report that drops
    a minus sign reverses a result, so a missing glyph fails the render and
    says where."""

    def __init__(self):
        self.missing = {}

    def check(self, text, face, where):
        cmap = pdfmetrics.getFont(face).face.charToGlyph
        for ch in text:
            if ord(ch) >= 32 and ord(ch) not in cmap:
                self.missing.setdefault(ch, (face, where))

    def verify(self):
        if not self.missing:
            return
        lines = [f"U+{ord(ch):04X} {unicodedata.name(ch, 'unnamed')} is not in {face}; first at {where}"
                 for ch, (face, where) in self.missing.items()]
        raise BriefError("characters that would print as blanks:\n  " + "\n  ".join(lines))


def minus(text):
    """A hyphen before a number, as the reports print it, set as a minus sign.

    In a column of changes −24 % and +24 % must be told apart at a glance; a
    hyphen is half the width of the plus beside it and easy to miss."""
    return re.sub(r"(?<![\w.#&;])-(?=\d)", "\u2212", text)


def plain(node):
    """A node's text as a reader sees it, with a line break for <br>."""
    if node.type in ("text", "code_inline"):
        return node.content
    if node.type in ("softbreak", "hardbreak"):
        return " "
    if node.type == "html_inline":
        return "\n" if node.content.lower().startswith("<br") else ""
    return "".join(plain(child) for child in node.children)


class Builder:
    """Walks a brief's Markdown tree and produces reportlab flowables."""

    def __init__(self, md, meta, reports, workdir, brief, line_offset):
        self.md, self.meta, self.reports, self.workdir = md, meta, reports, workdir
        self.brief, self.line_offset = brief, line_offset
        self.glyphs = Glyphs()
        self.width = PAGE[0] - 2 * MARGIN
        self.sections = [0, 0]
        self.figures = self.tables = self.anchors = 0
        self.numbered = meta.get("numbered", True)

    def where(self, node):
        line = (node.map[0] if node and node.map else 0) + self.line_offset + 1
        return f"{relative(self.brief)}:{line}"

    # -------------------------------------------------------------- inline

    def inline(self, node, where, face="Serif", size=10.5):
        out = []
        for child in node.children:
            kind = child.type
            if kind == "text":
                self.glyphs.check(child.content, face, where)
                out.append(escape(child.content))
            elif kind == "softbreak":
                out.append(" ")
            elif kind == "hardbreak":
                out.append("<br/>")
            elif kind == "strong":
                out.append("<b>" + self.inline(child, where, face, size) + "</b>")
            elif kind == "em":
                out.append("<i>" + self.inline(child, where, face, size) + "</i>")
            elif kind == "s":
                out.append("<strike>" + self.inline(child, where, face, size) + "</strike>")
            elif kind == "code_inline":
                self.glyphs.check(child.content, "Mono", where)
                out.append(f'<font face="Mono" size="{size * 0.86:.2f}">{escape(child.content)}</font>')
            elif kind == "link":
                inner = self.inline(child, where, face, size)
                href = child.attrs.get("href", "")
                # A relative link points into a repository the reader of a PDF
                # does not have open; its text is kept, its target dropped.
                if re.match(r"^(https?:|mailto:)", href):
                    out.append(f'<a href="{escape(href)}" color="{ACCENT.hexval()}">{inner}</a>')
                else:
                    out.append(inner)
            elif kind == "html_inline":
                out.append(self.html_inline(child.content, size))
            elif kind == "image":
                raise BriefError(f"{where}: an image must stand alone in its paragraph, where it becomes a figure")
            else:
                out.append(self.inline(child, where, face, size))
        return "".join(out)

    @staticmethod
    def html_inline(tag, size):
        tag = tag.strip().lower().replace(" ", "")
        if tag in ("<br>", "<br/>"):
            return "<br/>"
        if tag == "<sub>":
            # Reports print a range across seeds under each mean as <sub>; it is
            # a quieter second line, not a chemical subscript.
            return f'<font size="{size * 0.8:.2f}" color="{MUTED.hexval()}">'
        if tag in ("</sub>",):
            return "</font>"
        if tag in ("<sup>", "</sup>"):
            return tag.replace("sup", "super")
        return ""

    def inline_text(self, text, where, face="Serif", size=10.5):
        tokens = self.md.parseInline(str(text))
        tree = SyntaxTreeNode(tokens)
        return "".join(self.inline(child, where, face, size) for child in tree.children)

    # -------------------------------------------------------------- blocks

    def blocks(self, nodes, paragraph="body"):
        out = []
        nodes = list(nodes)
        i = 0
        while i < len(nodes):
            node = nodes[i]
            kind = node.type
            if kind == "heading":
                out.append(self.heading(node))
            elif kind == "paragraph":
                if self.is_caption(node) and i + 1 < len(nodes) and nodes[i + 1].type == "table":
                    out.extend(self.table_node(nodes[i + 1], caption=node))
                    i += 1
                elif self.is_figure(node):
                    out.append(self.image(node))
                else:
                    style = STYLES[paragraph]
                    out.append(Paragraph(self.inline(node.children[0], self.where(node), size=style.fontSize), style))
            elif kind == "table":
                caption = None
                if i + 1 < len(nodes) and nodes[i + 1].type == "paragraph" and self.is_caption(nodes[i + 1]):
                    caption = nodes[i + 1]
                    i += 1
                out.extend(self.table_node(node, caption))
            elif kind in ("bullet_list", "ordered_list"):
                out.append(self.list(node))
            elif kind == "blockquote":
                out.append(self.callout(node))
            elif kind == "fence":
                out.extend(self.fence(node))
            elif kind == "code_block":
                out.append(self.code(node.content, self.where(node)))
            elif kind == "hr":
                out.append(HRFlowable(width="100%", thickness=0.5, color=HAIRLINE, spaceBefore=6, spaceAfter=8))
            elif kind == "html_block":
                if "pagebreak" in node.content.lower():
                    out.append(PageBreak())
            else:
                raise BriefError(f"{self.where(node)}: no layout for Markdown '{kind}'")
            i += 1
        return out

    def heading(self, node):
        level = int(node.tag[1])
        where = self.where(node)
        markup = self.inline(node.children[0], where, face="Sans" if level < 3 else "Serif")
        text = plain(node).strip()
        numbered = self.numbered and level <= 2 and not text.endswith("{-}")
        if text.endswith("{-}"):
            text = text[:-3].rstrip()
            markup = re.sub(r"\s*\{-\}\s*$", "", markup)
        if numbered:
            if level == 1:
                self.sections = [self.sections[0] + 1, 0]
                number = f"{self.sections[0]}"
            else:
                self.sections[1] += 1
                number = f"{self.sections[0]}.{self.sections[1]}"
            markup = f"{number} {markup}"
            text = f"{number} {text}"
        paragraph = Paragraph(markup, STYLES[f"h{min(level, 3)}"])
        if level <= 2:
            self.anchors += 1
            paragraph.toc = (level - 1, text, f"section-{self.anchors}")
        return paragraph

    @staticmethod
    def is_caption(node):
        return plain(node).startswith("Table:")

    @staticmethod
    def is_figure(node):
        children = [c for c in node.children[0].children if not (c.type == "text" and not c.content.strip())]
        return len(children) == 1 and children[0].type == "image"

    def image(self, node):
        where = self.where(node)
        img = next(c for c in node.children[0].children if c.type == "image")
        path = os.path.join(os.path.dirname(os.path.abspath(self.brief)), img.attrs.get("src", ""))
        if not os.path.exists(path):
            raise BriefError(f"{where}: image {img.attrs.get('src')} does not exist (paths are relative to the brief)")
        with PILImage.open(path) as picture:
            w, h = picture.size
        height = self.width * h / w
        return self.figure(Image(path, width=self.width, height=height), plain(img), where)

    def figure(self, flowable, caption, where):
        self.figures += 1
        text = f"<b>Figure {self.figures}.</b> " + self.inline_text(caption, where, size=9) if caption else ""
        parts = [Spacer(1, 4), flowable]
        if text:
            parts.append(Paragraph(text, STYLES["caption"]))
        return KeepTogether(parts)

    def list(self, node):
        ordered = node.type == "ordered_list"
        items = []
        for item in node.children:
            items.append(ListItem(self.blocks(item.children, paragraph="item"), leftIndent=15))
        options = dict(bulletFontName="Serif", bulletFontSize=10.5, leftIndent=15, spaceBefore=0, spaceAfter=5)
        if ordered:
            return ListFlowable(items, bulletType="1", start=int(node.attrs.get("start", 1)), bulletFormat="%s.",
                                **options)
        return ListFlowable(items, bulletType="bullet", start="•", **options)

    def callout(self, node):
        inner = self.blocks(node.children, paragraph="quote")
        box = Table([[inner]], colWidths=[self.width])
        box.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), TINT),
            ("LINEBEFORE", (0, 0), (0, -1), 2.2, ACCENT),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        return KeepTogether([Spacer(1, 2), box, Spacer(1, 8)])

    def code(self, text, where):
        size = STYLES["code"].fontSize
        per_line = max(20, int((self.width - 18) / stringWidth("0", "Mono", size)))
        lines = []
        for line in text.rstrip("\n").split("\n"):
            while len(line) > per_line:
                cut = line.rfind(" ", per_line // 2, per_line)
                cut = cut if cut > 0 else per_line
                lines.append(line[:cut].rstrip())
                line = "    " + line[cut:].lstrip()
            lines.append(line)
        body = "\n".join(lines)
        self.glyphs.check(body, "Mono", where)
        box = Table([[Preformatted(body, STYLES["code"])]], colWidths=[self.width])
        box.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), TINT),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        return KeepTogether([box, Spacer(1, 8)])

    # -------------------------------------------------------------- tables

    def cells(self, row, where, bold=False):
        out = []
        for cell in row.children:
            align = "left"
            match = re.search(r"text-align:\s*(left|right|center)", cell.attrs.get("style", "") or "")
            if match:
                align = match.group(1)
            inline = cell.children[0] if cell.children else None
            markup = minus(self.inline(inline, where)) if inline else ""
            out.append({"markup": markup, "plain": minus(plain(inline)) if inline else "", "align": align,
                        "bold": bold})
        return out

    def parse_table(self, node, where):
        head = next(c for c in node.children if c.type == "thead")
        body = next((c for c in node.children if c.type == "tbody"), None)
        header = self.cells(head.children[0], where, bold=True)
        rows = [self.cells(tr, where) for tr in body.children] if body else []
        return header, rows

    def table_node(self, node, caption=None):
        where = self.where(node)
        header, rows = self.parse_table(node, where)
        text = None
        if caption is not None:
            text = self.inline(caption.children[0], self.where(caption), size=9)
            text = re.sub(r"^Table:\s*", "", text)
        return self.table(header, rows, text)

    def table(self, header, rows, caption=None):
        ncols = len(header)
        headless = all(not c["plain"].strip() for c in header)
        columns = [[(c["plain"], c["bold"], c.get("width"))
                    for c in ([] if headless else [header[j]]) + [r[j] for r in rows if j < len(r)]]
                   for j in range(ncols)]
        size = 9 if ncols <= 4 else 8.5 if ncols <= 6 else 8 if ncols <= 8 else 7
        widths, fits = self.column_widths(columns, size)
        while not fits and size > 6.5:
            size -= 0.5
            widths, fits = self.column_widths(columns, size)
        styles = {}

        def cell_style(align, bold):
            key = (align, bold)
            if key not in styles:
                styles[key] = ParagraphStyle(
                    f"cell-{align}-{bold}", fontName="Serif-Bold" if bold else "Serif", fontSize=size,
                    leading=size * 1.22, textColor=INK,
                    alignment={"left": TA_LEFT, "right": TA_RIGHT, "center": TA_CENTER}[align])
            return styles[key]

        aligns = [c["align"] for c in header]
        data = [] if headless else [[Paragraph(c["markup"], cell_style(c["align"], True)) for c in header]]
        for row in rows:
            data.append([Paragraph(c["markup"], cell_style(aligns[j] if j < len(aligns) else "left", False))
                         for j, c in enumerate(row)])
        table = Table(data, colWidths=widths, repeatRows=0 if headless else 1, hAlign="CENTER")
        commands = [
            ("LINEABOVE", (0, 0), (-1, 0), 0.8, INK),
            ("LINEBELOW", (0, -1), (-1, -1), 0.8, INK),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]
        if not headless:
            commands += [("LINEBELOW", (0, 0), (-1, 0), 0.5, INK), ("VALIGN", (0, 0), (-1, 0), "BOTTOM")]
        first = 0 if headless else 1
        commands += [
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 2.6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2),
        ]
        if len(data) > first + 1:
            commands.append(("LINEBELOW", (0, first), (-1, -2), 0.25, HAIRLINE))
        table.setStyle(TableStyle(commands))
        out = []
        if caption:
            self.tables += 1
            out.append(Paragraph(f"<b>Table {self.tables}.</b> {caption}", STYLES["tablecaption"]))
        out += [table, Spacer(1, 10)]
        return out

    def column_widths(self, columns, size):
        """Natural widths when they fit; otherwise every column gets its longest
        word and the rest is shared by how much more each would like. Also says
        whether even the longest words fit, so the caller can try a smaller face."""
        pad = 8.6
        natural, minimum = [], []
        for cells in columns:
            nat = least = 0.0
            for text, bold, width in cells:
                if width is not None:
                    # A cell set in another face measures itself; it is never broken.
                    nat, least = max(nat, width), max(least, width)
                    continue
                font = "Serif-Bold" if bold else "Serif"
                for line in text.split("\n"):
                    nat = max(nat, stringWidth(line, font, size))
                    for word in line.split():
                        least = max(least, stringWidth(word, font, size))
            natural.append(nat + pad)
            minimum.append(least + pad)
        total = sum(natural)
        if total <= self.width:
            return (natural if total < 0.62 * self.width else [w * self.width / total for w in natural]), True
        spare = self.width - sum(minimum)
        if spare <= 0:
            return [w * self.width / sum(minimum) for w in minimum], False
        want = [n - m for n, m in zip(natural, minimum)]
        return [m + spare * w / sum(want) for m, w in zip(minimum, want)], True

    # -------------------------------------------------------------- directives

    def fence(self, node):
        info = (node.info or "").strip().split()
        kind = info[0] if info else ""
        if kind not in DIRECTIVES:
            return [self.code(node.content, self.where(node))]
        where = self.where(node)
        spec = directive_spec(node, where)
        try:
            if kind == "chart":
                return [self.chart(spec, where)]
            if kind == "table":
                return self.report_table(spec, where)
            return self.provenance()
        except BriefError as err:
            raise BriefError(f"{where}: {err}") from None

    def chart(self, spec, where):
        path = os.path.join(self.workdir, f"figure-{self.figures + 1}.png")
        height = charts.draw(spec, self.reports, path, self.width / 72)
        return self.figure(Image(path, width=self.width, height=height * 72), spec.get("caption", ""), where)

    def report_table(self, spec, where):
        unknown = set(spec) - TABLE_KEYS
        if unknown:
            raise BriefError(f"table: unknown key {', '.join(sorted(unknown))} (known: {', '.join(sorted(TABLE_KEYS))})")
        for key in ("from", "section"):
            if key not in spec:
                raise BriefError(f"table: needs '{key}'")
        source = resolve(spec["from"])
        if os.path.isdir(source):
            report = self.reports.get(spec["from"])
            text, label = report.text(), report.path + "/report.md"
        elif os.path.exists(source):
            with open(source) as f:
                text, label = f.read(), relative(source)
        else:
            raise BriefError(f"table: {spec['from']} does not exist")

        tree = SyntaxTreeNode(self.md.parse(text))
        nodes = list(tree.children)
        headings = [plain(n).strip() for n in nodes if n.type == "heading"]
        start = next((i for i, n in enumerate(nodes) if n.type == "heading" and plain(n).strip() == spec["section"]),
                     None)
        if start is None:
            raise BriefError(f"{label} has no section '{spec['section']}' (its sections: {'; '.join(headings)})")
        found = None
        for n in nodes[start + 1:]:
            if n.type == "heading":
                break
            if n.type == "table":
                found = n
                break
        if found is None:
            raise BriefError(f"{label}: section '{spec['section']}' has no table")
        header, rows = self.parse_table(found, where)

        if "columns" in spec:
            names = [c["plain"] for c in header]
            keep = []
            for column in spec["columns"]:
                if column not in names:
                    raise BriefError(f"{label}, '{spec['section']}': no column '{column}' (columns: {', '.join(names)})")
                keep.append(names.index(column))
            header = [header[j] for j in keep]
            rows = [[row[j] for j in keep] for row in rows]
        if "rows" in spec:
            by_name = {row[0]["plain"]: row for row in rows}
            missing = [r for r in spec["rows"] if r not in by_name]
            if missing:
                raise BriefError(f"{label}, '{spec['section']}': no row '{missing[0]}' (rows: {'; '.join(by_name)})")
            rows = [by_name[r] for r in spec["rows"]]
        for old, new in (spec.get("rename") or {}).items():
            for row in rows:
                if row[0]["plain"] == old:
                    self.glyphs.check(str(new), "Serif", where)
                    row[0] = {**row[0], "markup": escape(str(new)), "plain": str(new)}
        caption = self.inline_text(spec["caption"], where, size=9) if spec.get("caption") else None
        return self.table(header, rows, caption)

    def provenance(self):
        def mono(text):
            return (f'<font face="Mono" size="6.8">{escape(text)}</font>', stringWidth(text, "Mono", 6.8) + 8.6)

        def build(b):
            if not b:
                return ("unknown", None)
            version = b.get("version") or "unversioned"
            flag = ", modified" if b.get("modified") else ""
            commit, width = mono(b["commit"][:12])
            return (f"{escape(version)} {commit}{flag}", width + stringWidth(f"{version} {flag}", "Serif", 8.5))

        header = [{"markup": h, "plain": h, "align": a, "bold": True} for h, a in (
            ("Report", "left"), ("Runs", "right"), ("autoscaler", "left"), ("simlab-api", "left"),
            ("Measured by", "left"), ("runs.csv SHA-256", "left"))]
        rows = []
        for report in self.reports.opened.values():
            p = report.provenance
            runs = str(p.get("runs", len(report.rows)))
            values = [mono(report.name), (runs, None), build(p.get("autoscaler")), build(p.get("simlab_api")),
                      mono((p.get("platform_experiments") or {}).get("commit", "")[:12]),
                      mono(p.get("runs_csv_sha256", "")[:12] + "…")]
            rows.append([{"markup": m, "plain": re.sub(r"<[^>]+>", "", m), "width": w, "align": header[j]["align"],
                          "bold": False} for j, (m, w) in enumerate(values)])
        if not rows:
            raise BriefError("provenance: the brief draws on no report, so there is nothing to list")
        return self.table(header, rows)

    # -------------------------------------------------------------- front

    def front(self, st):
        meta, where = self.meta, relative(self.brief) + ":1"
        out = [Paragraph(self.inline_text(meta["title"], where, face="Sans", size=21), STYLES["title"])]
        if meta.get("subtitle"):
            out.append(Paragraph(self.inline_text(meta["subtitle"], where), STYLES["subtitle"]))
        byline = " · ".join(str(meta[k]) for k in ("author", "date") if meta.get(k))
        if byline:
            out.append(Paragraph(self.inline_text(byline, where), STYLES["meta"]))
        out.append(Paragraph(escape(stamp_sentence(st)), STYLES["stamp"]))
        out.append(HRFlowable(width="100%", thickness=0.5, color=RULE, spaceBefore=2, spaceAfter=10))
        if meta.get("toc"):
            toc = TableOfContents(levelStyles=[STYLES["toc1"], STYLES["toc2"]], dotsMinLevel=0)
            out += [Paragraph("Contents", STYLES["contents"]), toc, PageBreak()]
        return out


def directive_spec(node, where):
    try:
        spec = load_yaml(node.content) if node.content.strip() else {}
    except yaml.YAMLError as err:
        raise BriefError(f"{where}: the {node.info.strip()} block is not valid YAML: {err}") from None
    if not isinstance(spec, dict):
        raise BriefError(f"{where}: the {node.info.strip()} block must be a YAML mapping of keys to values")
    return spec


def stamp_sentence(st):
    if not st["commit"]:
        return "Rendered outside a git checkout, so no commit ties this document to its inputs."
    head = f"Rendered from platform-experiments {st['commit'][:12]}"
    if st["modified"]:
        return f"{head}, with uncommitted changes to its inputs: {', '.join(st['modified'])}."
    return f"{head}; its brief, the reports it draws on and the renderer are all committed there."


def front_matter(source, path):
    if not source.startswith("---\n"):
        raise BriefError(f"{relative(path)}: a brief starts with a YAML header between --- lines, "
                         f"with at least a title")
    end = source.find("\n---\n", 4)
    if end < 0:
        raise BriefError(f"{relative(path)}: the YAML header is never closed with a --- line")
    meta = load_yaml(source[4:end]) or {}
    if not isinstance(meta, dict) or not meta.get("title"):
        raise BriefError(f"{relative(path)}: the header needs a title")
    meta = {k: (str(v) if k == "date" else v) for k, v in meta.items()}
    body = source[end + 5:]
    return meta, body, source[:end + 5].count("\n")


def prescan(tree, reports, brief, line_offset):
    """Opens every report and finds every image before anything is laid out, so
    the provenance table is complete wherever it sits and a bad digest fails
    before a minute of rendering."""
    images = []

    def visit(node):
        if node.type == "fence" and (node.info or "").strip().split()[:1] in (["chart"], ["table"]):
            line = (node.map[0] if node.map else 0) + line_offset + 1
            spec = directive_spec(node, f"{relative(brief)}:{line}")
            source = spec.get("source") or spec.get("from")
            try:
                if source and os.path.isdir(resolve(source)):
                    reports.get(source)
            except BriefError as err:
                raise BriefError(f"{relative(brief)}:{line}: {err}") from None
        if node.type == "image":
            images.append(os.path.join(os.path.dirname(os.path.abspath(brief)), node.attrs.get("src", "")))
        for child in node.children:
            visit(child)

    visit(tree)
    return images


def canvas_class(header, footer):
    """A canvas that holds every page until the end, so each can say 'n / total'."""

    class Paged(Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._held = []

        def showPage(self):
            self._held.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total = len(self._held)
            for state in self._held:
                self.__dict__.update(state)
                self.decorate(total)
                Canvas.showPage(self)
            Canvas.save(self)

        def decorate(self, total):
            width, height = PAGE
            self.saveState()
            self.setFont("Sans", 7)
            self.setFillColor(MUTED)
            if self._pageNumber > 1:
                self.drawString(MARGIN, height - 14 * mm, header[0])
                self.drawRightString(width - MARGIN, height - 14 * mm, header[1])
                self.setStrokeColor(HAIRLINE)
                self.setLineWidth(0.5)
                self.line(MARGIN, height - 15.6 * mm, width - MARGIN, height - 15.6 * mm)
            self.drawString(MARGIN, 11 * mm, footer)
            self.drawRightString(width - MARGIN, 11 * mm, f"{self._pageNumber} / {total}")
            self.restoreState()

    return Paged


class Document(BaseDocTemplate):
    def __init__(self, path, meta, st):
        super().__init__(
            path, pagesize=PAGE, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=24 * mm, bottomMargin=20 * mm,
            title=str(meta["title"]), author=str(meta.get("author", "")), subject=str(meta.get("subtitle", "")),
            creator="platform-experiments lib/pdf", keywords=f"platform-experiments {st['commit'][:12]}",
            invariant=1)
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="body",
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates([PageTemplate(id="page", frames=[frame])])

    def afterFlowable(self, flowable):
        entry = getattr(flowable, "toc", None)
        if entry:
            level, text, key = entry
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text, key, level=level, closed=level > 0)
            self.notify("TOCEntry", (level, escape(text), self.page, key))


def render(brief, out):
    """Renders a brief to a PDF at out; returns the number of pages."""
    register_fonts()
    with open(brief) as f:
        source = f.read()
    meta, body, line_offset = front_matter(source, brief)
    md = MarkdownIt("commonmark", {"html": True}).enable("table").enable("strikethrough")
    tree = SyntaxTreeNode(md.parse(body))
    reports = Reports()
    images = prescan(tree, reports, brief, line_offset)

    here = os.path.dirname(os.path.abspath(__file__))
    inputs = [brief, here, os.path.join(ROOT, "lib", "sweep.py")] + [r.dir for r in reports.opened.values()] + images
    st = stamp(inputs)

    header = (str(meta.get("header") or meta["title"]), str(meta.get("date", "")))
    footer = f"platform-experiments {st['commit'][:12]}" + (" · modified" if st["modified"] else "") \
        if st["commit"] else "not in a git checkout"

    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with tempfile.TemporaryDirectory() as workdir:
        builder = Builder(md, meta, reports, workdir, brief, line_offset)
        story = builder.front(st) + builder.blocks(tree.children)
        for text in (*header, footer):
            builder.glyphs.check(text, "Sans", "the running header and footer")
        builder.glyphs.verify()
        document = Document(out, meta, st)
        document.multiBuild(story, canvasmaker=canvas_class(header, footer))
        return document.page
