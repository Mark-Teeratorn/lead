#!/usr/bin/env python3
"""Build formatted .docx with native Word OMML equations and Heading styles from the manuscript .txt file."""

import argparse
import re
import sys
from pathlib import Path
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree
import latex2mathml.converter
import mathml2omml

TXT_PATH = Path(
    "/home/aimslab/lead/docs/Distribution-Curated Fine-Tuning Reduces Closed-Loop Standstill at Scale in Continuous-Action Autonomous Driving.txt"
)
DOCX_PATH = Path(
    "/home/aimslab/lead/outputs/paper_build_test/Distribution-Curated Fine-Tuning Reduces Closed-Loop Standstill at Scale in Continuous-Action Autonomous Driving.docx"
)
FIG_DIR = Path("/home/aimslab/lead/docs/figures/revision")
FIGURE_RE = re.compile(r"^\[\[FIGURE\s+(\d+)\s*:\s*(.*?)\]\]$")
PENDING_RE = re.compile(r"\[\[PENDING:.*?\]\]")

M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def clean_latex_for_omml(latex_str: str) -> str:
    clean = latex_str.strip()
    clean = clean.replace(r"\operatorname{clip}", r"\mathrm{clip}")
    clean = clean.replace(r"\operatorname{atan2}", r"\mathrm{atan2}")
    clean = clean.replace(r"\Big\|", r"\Vert ").replace(r"\big\|", r"\Vert ")
    clean = clean.replace(r"\lVert", r"\Vert ").replace(r"\rVert", r"\Vert ")
    clean = clean.replace(r"\|", r"\Vert ")
    clean = clean.replace(r"\big[", "[").replace(r"\big]", "]")
    clean = clean.replace(r"\big(", "(").replace(r"\big)", ")")
    return clean


def latex_to_omml_element(latex_str: str, is_display: bool = False):
    clean = clean_latex_for_omml(latex_str)
    mathml = latex2mathml.converter.convert(clean)
    omml = mathml2omml.convert(mathml)
    omml_with_ns = omml.replace("<m:oMath>", f'<m:oMath xmlns:m="{M_NS}">', 1)
    omml_el = etree.fromstring(omml_with_ns.encode("utf-8"))

    # 1. Hide empty <m:sup/> or <m:sub/> in <m:nary> so no empty placeholder box appears
    for nary in omml_el.xpath("//m:nary", namespaces={"m": M_NS}):
        naryPr = nary.find(f"{{{M_NS}}}naryPr")
        sup = nary.find(f"{{{M_NS}}}sup")
        sub = nary.find(f"{{{M_NS}}}sub")
        if naryPr is not None:
            if sup is not None and len(sup) == 0 and (sup.text is None or not sup.text.strip()):
                sh = etree.Element(f"{{{M_NS}}}supHide")
                sh.set(f"{{{M_NS}}}val", "1")
                naryPr.append(sh)
            if sub is not None and len(sub) == 0 and (sub.text is None or not sub.text.strip()):
                sbh = etree.Element(f"{{{M_NS}}}subHide")
                sbh.set(f"{{{M_NS}}}val", "1")
                naryPr.append(sbh)

    # 2. Convert <m:limUpp> diacritics (^, ~, ˙) into proper <m:acc> elements
    acc_map = {
        "^": "\u0302",
        "ˆ": "\u0302",
        "~": "\u0303",
        "˜": "\u0303",
        "˙": "\u0307",
        "\u02d9": "\u0307",
    }
    for limupp in omml_el.xpath("//m:limUpp", namespaces={"m": M_NS}):
        lim_t = "".join(limupp.xpath("./m:lim//m:t/text()", namespaces={"m": M_NS})).strip()
        if lim_t in acc_map:
            acc = etree.fromstring(
                f'<m:acc xmlns:m="{M_NS}"><m:accPr><m:chr m:val="{acc_map[lim_t]}"/></m:accPr></m:acc>'
            )
            e_el = limupp.find(f"{{{M_NS}}}e")
            if e_el is not None:
                acc.append(e_el)
                limupp.getparent().replace(limupp, acc)

    # 2.5 Fix <m:rad> elements missing <m:radPr><m:degHide m:val="1"/></m:radPr><m:deg/>
    for rad in omml_el.xpath("//m:rad", namespaces={"m": M_NS}):
        if rad.find(f"{{{M_NS}}}radPr") is None:
            radPr = etree.fromstring(
                f'<m:radPr xmlns:m="{M_NS}"><m:degHide m:val="1"/></m:radPr>'
            )
            deg = etree.Element(f"{{{M_NS}}}deg")
            rad.insert(0, deg)
            rad.insert(0, radPr)

    # 3. Replace ASCII ~, *, | in <m:t> with unambiguous Unicode math symbols so LibreOffice StarMath never misparses them
    for mt in omml_el.xpath("//m:t", namespaces={"m": M_NS}):
        if mt.text:
            mt.text = (
                mt.text.replace("~", "\u223c")
                .replace("*", "\u2217")
                .replace("|", "\u2502")
                .replace("∣", "\u2502")
            )

    if is_display:
        para_xml = f'<m:oMathPara xmlns:m="{M_NS}"></m:oMathPara>'
        para_el = etree.fromstring(para_xml.encode("utf-8"))
        para_el.append(omml_el)
        return para_el
    return omml_el


def set_run_font(run, size_pt=12, bold=False, italic=False):
    run.font.name = "Times New Roman"
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(0, 0, 0)
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), "Times New Roman")
    rFonts.set(qn("w:hAnsi"), "Times New Roman")
    rFonts.set(qn("w:cs"), "Times New Roman")


def add_math_or_code_segment(paragraph, text: str, size_pt=12, bold=False):
    # Split by inline math $...$
    parts = re.split(r"(\$[^\$]+\$)", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("$") and part.endswith("$") and len(part) > 2:
            latex_code = part[1:-1]
            try:
                omml_el = latex_to_omml_element(latex_code, is_display=False)
                paragraph._p.append(omml_el)
            except Exception as e:
                print(f"Warning: inline math fallback for {latex_code}: {e}")
                r = paragraph.add_run(latex_code)
                set_run_font(r, size_pt=size_pt, bold=bold, italic=True)
        else:
            # Handle `code` spans inside non-math text
            subparts = re.split(r"(`[^`]+`)", part)
            for sp in subparts:
                if not sp:
                    continue
                if sp.startswith("`") and sp.endswith("`") and len(sp) > 2:
                    r = paragraph.add_run(sp[1:-1])
                    set_run_font(r, size_pt=size_pt, bold=bold)
                else:
                    r = paragraph.add_run(sp)
                    set_run_font(r, size_pt=size_pt, bold=bold)


def add_formatted_text_and_math(paragraph, text: str, size_pt=12, default_bold=False):
    # Outer split by **bold** first so ** spans that contain $...$ or `...` are parsed cleanly
    bold_segments = re.split(r"(\*\*.*?\*\*)", text)
    for seg in bold_segments:
        if not seg:
            continue
        if seg.startswith("**") and seg.endswith("**") and len(seg) > 4:
            inner = seg[2:-2]
            add_math_or_code_segment(paragraph, inner, size_pt=size_pt, bold=True)
        else:
            add_math_or_code_segment(paragraph, seg, size_pt=size_pt, bold=default_bold)


def format_paragraph_spacing(p, space_before=0, space_after=6, line_spacing=1.15, align=None):
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing = line_spacing
    if align is not None:
        p.alignment = align


def main(txt_path=TXT_PATH, docx_path=DOCX_PATH):
    raw_text = Path(txt_path).read_text(encoding="utf-8")
    lines = raw_text.splitlines()
    pending_count = 0

    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    major_headings = {
        "Abstract",
        "1. Introduction",
        "2. Related Work",
        "3. Methodology",
        "4. Experimental Results and Statistical Analysis",
        "5. Discussion and Limitations",
        "6. Conclusion, Reproducibility, and Disclosures",
        "References",
    }

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i].strip()
        if not line or line == "---":
            i += 1
            continue

        # Revision notes block: skipped entirely
        if line == "%%% REVISION NOTES":
            while i < n and lines[i].strip() != "%%% END NOTES":
                i += 1
            i += 1
            continue

        # Figure placeholder: [[FIGURE n: caption]]
        fm = FIGURE_RE.match(line)
        if fm:
            fig_n, fig_caption = fm.group(1), fm.group(2).strip()
            img_path = FIG_DIR / f"figure_{fig_n}.png"
            caption_text = f"Figure {fig_n}. {fig_caption}"
            if img_path.exists():
                p = doc.add_paragraph()
                format_paragraph_spacing(p, space_before=8, space_after=4, line_spacing=1.0, align=WD_ALIGN_PARAGRAPH.CENTER)
                p.add_run().add_picture(str(img_path), width=Inches(6))
            else:
                print(f"Warning: figure file missing: {img_path}")
                caption_text = "[figure file missing] " + caption_text
            p = doc.add_paragraph()
            format_paragraph_spacing(p, space_before=2, space_after=8, line_spacing=1.15)
            add_formatted_text_and_math(p, caption_text, size_pt=11)
            i += 1
            continue

        # Pending placeholders: keep as visible bold text and count
        if PENDING_RE.search(line):
            pending_count += len(PENDING_RE.findall(line))
            p = doc.add_paragraph()
            format_paragraph_spacing(p, space_before=0, space_after=6, line_spacing=1.15)
            for seg in re.split(r"(\[\[PENDING:.*?\]\])", line):
                if not seg:
                    continue
                if PENDING_RE.fullmatch(seg):
                    r = p.add_run(seg)
                    set_run_font(r, size_pt=12, bold=True)
                else:
                    add_formatted_text_and_math(p, seg, size_pt=12)
            i += 1
            continue

        # Title (first non-empty line)
        if i == 0:
            p = doc.add_paragraph(style="Title")
            format_paragraph_spacing(p, space_before=0, space_after=12, line_spacing=1.15, align=WD_ALIGN_PARAGRAPH.CENTER)
            add_formatted_text_and_math(p, line, size_pt=16, default_bold=True)
            i += 1
            continue

        # Major section heading (Heading 1)
        if line in major_headings or re.match(r"^\d+\. [A-Z][^.]{2,90}$", line) and len(line.split()) <= 8 and not line.endswith(":") and "**" not in line:
            p = doc.add_paragraph(style="Heading 1")
            format_paragraph_spacing(p, space_before=14, space_after=6, line_spacing=1.15)
            add_formatted_text_and_math(p, line, size_pt=14, default_bold=True)
            i += 1
            continue

        # Subsection heading (## 3.x / 4.x -> Heading 2)
        if line.startswith("## "):
            heading_text = line[3:].strip()
            p = doc.add_paragraph(style="Heading 2")
            format_paragraph_spacing(p, space_before=12, space_after=6, line_spacing=1.15)
            add_formatted_text_and_math(p, heading_text, size_pt=12.5, default_bold=True)
            i += 1
            continue

        # Table Caption (Table X: ...)
        if re.match(r"^Table S?\d+:", line):
            p = doc.add_paragraph()
            format_paragraph_spacing(p, space_before=8, space_after=4, line_spacing=1.15)
            add_formatted_text_and_math(p, line, size_pt=11, default_bold=True)
            i += 1
            continue

        # Display equation $$...$$
        if line.startswith("$$") and line.endswith("$$") and len(line) > 4:
            latex_code = line[2:-2].strip()
            p = doc.add_paragraph()
            format_paragraph_spacing(p, space_before=6, space_after=6, line_spacing=1.15, align=WD_ALIGN_PARAGRAPH.CENTER)
            try:
                omml_para = latex_to_omml_element(latex_code, is_display=True)
                p._p.append(omml_para)
            except Exception as e:
                print(f"Warning: display math fallback for {latex_code}: {e}")
                r = p.add_run(latex_code)
                set_run_font(r, size_pt=12, italic=True)
            i += 1
            continue

        # Markdown Table
        if line.startswith("|"):
            table_lines = []
            while i < n and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            data_rows = []
            for tl in table_lines:
                cells = [c.strip() for c in tl.strip("|").split("|")]
                if all(re.match(r"^:?-{2,}:?$", c) for c in cells):
                    continue
                data_rows.append(cells)
            if data_rows:
                num_cols = max(len(r) for r in data_rows)
                table = doc.add_table(rows=len(data_rows), cols=num_cols)
                table.style = "Table Grid"
                font_sz = 8.0 if num_cols >= 10 else (9.0 if num_cols >= 8 else 10.0)
                for r_idx, row_cells in enumerate(data_rows):
                    if r_idx == 0:
                        trPr = table.rows[0]._tr.get_or_add_trPr()
                        trPr.append(OxmlElement("w:tblHeader"))
                    for c_idx, cell_text in enumerate(row_cells):
                        cell = table.cell(r_idx, c_idx)
                        cell_p = cell.paragraphs[0]
                        format_paragraph_spacing(cell_p, space_before=2, space_after=2, line_spacing=1.05)
                        add_formatted_text_and_math(
                            cell_p,
                            cell_text,
                            size_pt=font_sz,
                            default_bold=(r_idx == 0),
                        )
            continue

        # Bullet / numbered list items or normal body paragraphs
        if line.startswith("* ") or line.startswith("- "):
            p = doc.add_paragraph()
            format_paragraph_spacing(p, space_before=2, space_after=4, line_spacing=1.15)
            p.paragraph_format.left_indent = Inches(0.25)
            add_formatted_text_and_math(p, "• " + line[2:].strip(), size_pt=12)
        else:
            p = doc.add_paragraph()
            format_paragraph_spacing(p, space_before=0, space_after=6, line_spacing=1.15)
            add_formatted_text_and_math(p, line, size_pt=12)

        i += 1

    Path(docx_path).parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(docx_path))
    print(f"Saved {docx_path}")
    print(f"PENDING placeholders: {pending_count}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Build the manuscript .docx from the .txt source.")
    ap.add_argument("--input", default=str(TXT_PATH), help="manuscript .txt")
    ap.add_argument("--output", default=str(DOCX_PATH), help="output .docx")
    a = ap.parse_args()
    main(a.input, a.output)
