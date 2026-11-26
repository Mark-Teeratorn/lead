#!/usr/bin/env python3
"""Build an IEEE Access version of the manuscript from the same .txt source.

The text is converted by build_manuscript_tex.py (same escaping, citations, tables and figures); this script
then moves the result into the IEEE Access class (ieeeaccess.cls, two columns):

  * front matter: title, author/address/corresponding-author placeholders, abstract, keywords (alphabetical);
  * section cross-references "Section 3.4" -> "Section III-D" (IEEE numbering), supplementary ones unchanged;
  * tables as full-width floats; figures single-column or full-width by aspect ratio;
  * placeholders for the end statements and biographies that IEEE Access requires.

The IEEE Access template files (class, fonts, logos) are not part of this repository: put them in
docs/latex_ieeeaccess/template/ (from the IEEE Access LaTeX template, ACCESS_latex_template_20240429).

Usage: python3 scripts/paper/build_manuscript_ieeeaccess.py [--input docs/manuscript_revision_draft.txt]
"""
import argparse
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_manuscript_tex as bm  # noqa: E402
import authors  # noqa: E402

ROOT = Path("/home/aimslab/lead")
OUT_DIR = ROOT / "docs/latex_ieeeaccess"
TEMPLATE_DIR = OUT_DIR / "template"
SHORT_TITLE = "Inertia in a Fine-Tuned VLA Driving Policy"
FULL_WIDTH_ASPECT = 1.6      # figures wider than this (width / height) span both columns
FIG_SCALE = {}               # per-figure width relative to the column or page, e.g. {1: 0.9}

DISPLAY_SPLITS = [
    ("\\[\nx_k = ", "\\begin{gather*}\nx_k = "),
    (", \\quad y_k = \\sum_{j=1}^{k} \\tfrac{\\Delta t}{2}\\big(v_{j-1}\\sin\\psi_{j-1} + v_j\\sin\\psi_j\\big)\n\\]",
     ", \\\\\ny_k = \\sum_{j=1}^{k} \\tfrac{\\Delta t}{2}\\big(v_{j-1}\\sin\\psi_{j-1} + v_j\\sin\\psi_j\\big)\n\\end{gather*}"),
    ("\\[\n\\mathcal{L}_{\\text{CFM}}(\\theta) = \\mathbb{E}_{s \\sim p(s),\\, \\mathbf{A}_0,\\, (\\mathbf{x}_t, \\mathbf{A}_1) \\sim \\mathcal{D}} \\left[",
     "\\begin{multline*}\n\\mathcal{L}_{\\text{CFM}}(\\theta) = \\mathbb{E}_{s \\sim p(s),\\, \\mathbf{A}_0,\\, (\\mathbf{x}_t, \\mathbf{A}_1) \\sim \\mathcal{D}} \\\\ \\left["),
    ("(\\mathbf{A}_1 - \\mathbf{A}_0) \\rVert_2^2 \\right]\n\\]", "(\\mathbf{A}_1 - \\mathbf{A}_0) \\rVert_2^2 \\right]\n\\end{multline*}"),
]

ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


def ieee_section(num):
    """'3' -> 'III', '3.4' -> 'III-D'."""
    parts = num.split(".")
    s = ROMAN[int(parts[0])]
    if len(parts) > 1:
        s += "-" + chr(ord("A") + int(parts[1]) - 1)
    return s


SEC_REF_RE = re.compile(r"(Sections?)((?:\s*(?:,|and|or|to|--)?\s*(?<![S\d.])\d{1,2}(?:\.\d{1,2})?(?![\d.]\d))+)")
SEC_NUM_RE = re.compile(r"(?<![S\d.])(\d{1,2}(?:\.\d{1,2})?)(?![\d])")


def convert_section_refs(tex, n_sections):
    def fix(m):
        nums = m.group(2)
        def one(k):
            top = int(k.group(1).split(".")[0])
            return ieee_section(k.group(1)) if 1 <= top <= n_sections else k.group(1)
        return m.group(1) + SEC_NUM_RE.sub(one, nums)
    return SEC_REF_RE.sub(fix, tex)


def split(tex, start, end):
    i, j = tex.index(start), tex.index(end)
    return tex[i + len(start):j], tex[j + len(end):]


def ieee_authors():
    up = ["\\uppercase{" + n + "}\\authorrefmark{1}" for n in authors.names()]
    return up[0] if len(up) == 1 else ", ".join(up[:-1]) + ", and " + up[-1]


def header_name():
    g, f, _ = authors.AUTHORS[0]
    return g[0] + ". " + f


def biographies(pend):
    out = []
    for n in authors.names():
        out += ["\\begin{IEEEbiographynophoto}{" + n + "}",
                pend + "biography of " + n + "; IEEE Access asks for one (and usually a photo) for every author]]}",
                "\\end{IEEEbiographynophoto}", ""]
    return out


def build(txt_path, out_dir=OUT_DIR):
    out_dir = Path(out_dir)
    with tempfile.TemporaryDirectory() as tmp:
        bm.build(txt_path, tmp)
        src = (Path(tmp) / "manuscript.tex").read_text(encoding="utf-8")
        (out_dir / "figures").mkdir(parents=True, exist_ok=True)
        for f in (Path(tmp) / "figures").glob("*.png"):
            shutil.copyfile(f, out_dir / "figures" / f.name)

    title = re.search(r"\\title\{(.*)\}\n", src).group(1)
    abstract, rest = split(src, "\\begin{abstract}\n", "\n\\end{abstract}")
    body, rest = rest.split("\\begin{thebibliography}", 1)
    biblio = "\\begin{thebibliography}" + rest.split("\\end{thebibliography}")[0] + "\\end{thebibliography}"

    # keywords paragraph -> keywords environment (alphabetical, as IEEE Access asks)
    km = re.search(r"\n\\textbf\{Keywords:\}\s*(.*)\n", body)
    if not km:
        raise SystemExit("keywords paragraph not found")
    kws = [k.strip() for k in km.group(1).split(";") if k.strip()]
    kws = sorted(kws, key=str.lower)
    keywords = ", ".join(kws)
    keywords = keywords[0].upper() + keywords[1:]
    body = body.replace(km.group(0), "\n")

    n_sections = len(re.findall(r"\\section\{", body))
    body = convert_section_refs(body, n_sections)
    abstract = convert_section_refs(abstract, n_sections)

    # floats: tables span both columns; figures by aspect ratio
    body = body.replace("\\begin{table}[htbp]", "\\begin{table*}[!t]").replace("\\end{table}", "\\end{table*}")
    from PIL import Image

    def fig(m):
        name = m.group(2)
        k = int(re.search(r"figure_(\d+)", name).group(1))
        w, h = Image.open(out_dir / "figures" / name).size
        wide = w / h > FULL_WIDTH_ASPECT
        scale = FIG_SCALE.get(k, 1.0)
        width = ("" if scale == 1.0 else f"{scale:g}") + ("\\textwidth" if wide else "\\columnwidth")
        env = "figure*" if wide else "figure"
        return (f"\\begin{{{env}}}[!t]\n\\centering\n\\includegraphics[width={width},height=0.45\\textheight,"
                f"keepaspectratio]{{{name}}}\n{m.group(3)}\n\\end{{{env}}}")
    body = re.sub(r"\\begin\{figure\}\[htbp\]\n\\centering\n\\includegraphics\[([^\]]*)\]\{([^}]*)\}\n(\\caption\{.*?\})\n\\end\{figure\}",
                  fig, body, flags=re.S)
    body = body.replace("\\maketitle", "").strip("\n")
    body = body.replace("\\texttt{", "\\code{")
    # display equations that are too wide for one column: broken over two lines
    for old, new in DISPLAY_SPLITS:
        if body.count(old) != 1:
            raise SystemExit(f"display split not found once: {old[:60]}")
        body = body.replace(old, new)
    body = body.replace("\\textbf{", "\\strong{")

    pend = "\\pending{[[PENDING: "
    tex = "\n".join([
        "\\documentclass{ieeeaccess}",
        "% Built by scripts/paper/build_manuscript_ieeeaccess.py from the manuscript .txt source. Do not edit by",
        "% hand: edit the .txt and rebuild, so that the .docx, the article PDF and this file stay identical in content.",
        "\\usepackage{cite}",
        "\\usepackage{amsmath,amssymb,amsfonts}",
        "\\usepackage{graphicx}",
        "\\usepackage{textcomp}",
        "\\usepackage{booktabs,tabularx,array}",
        "\\usepackage{url}",
        "\\usepackage{xcolor}",
        "\\graphicspath{{figures/}}",
        "\\newcommand{\\pending}[1]{\\textcolor{red}{\\textbf{#1}}}",
        "\\usepackage[hidelinks]{hyperref}",
        "% \\textbf around \\texttt breaks inside tabularx with this class; robust equivalents are used instead",
        "\\DeclareRobustCommand{\\code}[1]{{\\ttfamily #1}}",
        "\\DeclareRobustCommand{\\strong}[1]{{\\bfseries #1}}",
        "\\setlength{\\emergencystretch}{3em}",
        "",
        "\\begin{document}",
        "\\vol{14}",
        "\\year{2026}",
        "\\history{Date of publication xxxx 00, 0000, date of current version xxxx 00, 0000.}",
        "\\doi{10.1109/ACCESS.0000.DOI}",
        "",
        "\\title{" + title + "}",
        "\\author{" + ieee_authors() + "}",
        "\\address[1]{" + authors.AFFILIATION + "}",   # e-mail only in the corresponding-author line, as in most IEEE Access papers
        "",
        "\\markboth",
        "{" + header_name() + " \\headeretal: " + SHORT_TITLE + "}",
        "{" + header_name() + " \\headeretal: " + SHORT_TITLE + "}",
        "",
        "\\corresp{Corresponding author: " + authors.names()[authors.CORRESPONDING]
        + " (e-mail: " + authors.emails()[authors.CORRESPONDING] + ").}",
        "",
        "\\begin{abstract}",
        abstract.strip(),
        "\\end{abstract}",
        "",
        "\\begin{keywords}",
        keywords,
        "\\end{keywords}",
        "",
        "\\titlepgskip=-21pt",
        "",
        "\\maketitle",
        "",
        body,
        "",
        "\\section*{Acknowledgment}",
        authors.AI_DISCLOSURE + " " + pend + "funding, and data and code availability]]}",
        "",
        biblio,
        "",
        *biographies(pend),
        "\\EOD",
        "",
        "\\end{document}",
        "",
    ])
    (out_dir / "manuscript_ieeeaccess.tex").write_text(tex, encoding="utf-8")
    if TEMPLATE_DIR.exists():
        for f in TEMPLATE_DIR.iterdir():
            if f.is_file():
                shutil.copyfile(f, out_dir / f.name)
    else:
        print(f"Warning: template folder missing ({TEMPLATE_DIR}); the .tex will not compile without it")
    words = len(re.sub(r"\\[a-zA-Z]+|[{}$]", " ", abstract).split())
    print(f"Saved {out_dir / 'manuscript_ieeeaccess.tex'}; abstract about {words} words; keywords: {keywords}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input", default=str(bm.TXT_PATH))
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    a = ap.parse_args()
    build(a.input, a.out_dir)
