#!/usr/bin/env python3
"""Build a LaTeX version of the manuscript from the same .txt source as the .docx.

Output: <out-dir>/manuscript.tex and <out-dir>/figures/figure_N.png (copies), ready to compile
with pdflatex, xelatex or tectonic, or to upload as a folder.

The .txt conventions are those of build_manuscript_docx.py: first line = title, "Abstract",
"N. Heading" sections, "## N.M Heading" subsections, "Table N: caption" before a Markdown table,
[[FIGURE n: caption]], $inline$ and $$display$$ math (already LaTeX), **bold**, `code`,
[[PENDING: ...]] placeholders, "[n] ..." reference lines after "References",
and a "%%% REVISION NOTES ... %%% END NOTES" block that is skipped.
"""
import argparse

# Display width of a figure relative to the text width (author's request: Figure 1 smaller).
FIG_SCALE = {1: 0.8}


def bm_scale(k):
    s = FIG_SCALE.get(k, 1.0)
    return "" if s == 1.0 else f"{s:g}"
import re
import shutil
from pathlib import Path

ROOT = Path("/home/aimslab/lead")
TXT_PATH = ROOT / "docs/manuscript_revision_draft.txt"
OUT_DIR = ROOT / "docs/latex"
FIG_DIR = ROOT / "docs/figures/revision"

FIGURE_RE = re.compile(r"^\[\[FIGURE\s+(\d+)\s*:\s*(.*?)\]\]$")
SECTION_RE = re.compile(r"^(\d+)\. ([A-Z][^.]{2,90})$")           # "4. Experimental Results"
SUBSECTION_RE = re.compile(r"^## (\d+\.\d+) (.+)$")
TABLE_CAP_RE = re.compile(r"^Table (\d+): (.*)$")
REF_RE = re.compile(r"^\[(\d+)\] (.*)$")
NUM_ITEM_RE = re.compile(r"^(\d+)\. (.+)$")
CITE_RE = re.compile(r"\[(\d{1,2}(?:\s*[,–-]\s*\d{1,2})*)\]")
SCI_RE = re.compile(r"(\d+(?:\.\d+)?)\s*×\s*10\^\{([+\-−]?\d+)\}")
# Order matters: longer tokens first. Each alternative is kept as one segment.
INLINE_RE = re.compile(r"(\[\[PENDING.*?\]\]|\$[^$]+\$|\*\*.+?\*\*|`[^`]+`)")

TEXT_ESC = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
            "~": r"\textasciitilde{}", "^": r"\textasciicircum{}", "<": r"\ensuremath{<}", ">": r"\ensuremath{>}",
            "|": r"\ensuremath{|}",
            "−": r"\ensuremath{-}", "×": r"\ensuremath{\times}", "≤": r"\ensuremath{\leq}", "≥": r"\ensuremath{\geq}",
            "≈": r"\ensuremath{\approx}", "±": r"\ensuremath{\pm}", "→": r"\ensuremath{\rightarrow}",
            "ρ": r"\ensuremath{\rho}", "π": r"\ensuremath{\pi}", "§": r"\S{}", "†": r"\dag{}",
            "–": "--", "—": "---", "…": r"\ldots{}", "“": "``", "”": "''", "‘": "`", "’": "'"}
MATH_FIX = {"−": "-", "×": r"\times ", "≤": r"\leq ", "≥": r"\geq ", "–": "-"}
PATH_SAFE = re.compile(r"^[A-Za-z0-9_./:\-]+$")


def esc(text):
    return "".join(TEXT_ESC.get(ch, ch) for ch in text)


def plain(text, n_refs):
    """Escape a run of ordinary text; turn scientific notation into math and [n, m] into \\cite."""
    out, pos = [], 0
    pat = re.compile(f"{SCI_RE.pattern}|{CITE_RE.pattern}")
    for m in pat.finditer(text):
        seg = m.group(0)
        if m.group(1) is not None:                       # 1.1 × 10^{-8}
            rep = f"${m.group(1)} \\times 10^{{{m.group(2).replace('−', '-')}}}$"
        else:
            nums = []
            ok = n_refs > 0
            for part in re.split(r"\s*,\s*", m.group(3)):
                rng = re.split(r"\s*[–-]\s*", part)
                lo, hi = int(rng[0]), int(rng[-1])
                ok = ok and 1 <= lo <= hi <= n_refs
                nums += list(range(lo, hi + 1))
            rep = "\\cite{" + ",".join(f"ref{k}" for k in nums) + "}" if ok else esc(seg)
        out.append(esc(text[pos:m.start()]))
        out.append(rep)
        pos = m.end()
    out.append(esc(text[pos:]))
    return "".join(out)


def code(text):
    if "/" in text and PATH_SAFE.match(text):
        return "\\nolinkurl{" + text + "}"
    return "\\texttt{" + esc(text).replace("-", "\\mbox{-}") + "}"


def inline(text, n_refs, stats=None):
    out = []
    for seg in INLINE_RE.split(text):
        if not seg:
            continue
        if seg.startswith("[[PENDING"):
            if stats is not None:
                stats["pending"] += 1
            out.append("\\pending{" + esc(seg) + "}")
        elif seg.startswith("$") and seg.endswith("$") and len(seg) > 2:
            out.append("$" + "".join(MATH_FIX.get(ch, ch) for ch in seg[1:-1]) + "$")
        elif seg.startswith("**") and seg.endswith("**") and len(seg) > 4:
            out.append("\\textbf{" + inline(seg[2:-2], n_refs, stats) + "}")
        elif seg.startswith("`") and seg.endswith("`") and len(seg) > 2:
            out.append(code(seg[1:-1]))
        else:
            out.append(plain(seg, n_refs))
    return "".join(out)


def table_tex(caption, rows, n_refs, stats):
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]
    width = [max(len(r[c]) for r in rows) for c in range(ncol)]
    data_width = [max((len(r[c]) for r in rows[1:]), default=8) for c in range(ncol)]
    body = []
    for k, r in enumerate(rows):
        cells = [inline(c, n_refs, stats) for c in r]
        if k == 0:
            if ncol > 6:
                cells = [
                    f"\\parbox[b]{{{max(data_width[idx], 8) * 0.55:.1f}em}}{{\\raggedright\\textbf{{{cell}}}}}"
                    if (idx > 0 and len(r[idx]) > data_width[idx] + 2) else ("\\textbf{" + cell + "}" if cell else "")
                    for idx, cell in enumerate(cells)
                ]
            else:
                cells = ["\\textbf{" + c + "}" if c else "" for c in cells]
        body.append(" & ".join(cells) + " \\\\")
        if k == 0:
            body.append("\\midrule")
    cap = "\\caption{" + inline(caption, n_refs, stats) + "}"
    if ncol <= 6:   # text table: long columns wrap
        spec = "".join(">{\\raggedright\\arraybackslash}X" if w > 22 else "l" for w in width)
        if "X" not in spec:
            spec = ">{\\raggedright\\arraybackslash}X" + spec[1:]
        inner = ["\\begin{tabularx}{\\linewidth}{" + spec + "}", "\\toprule", *body, "\\bottomrule", "\\end{tabularx}"]
        return "\n".join(["\\begin{table}[htbp]", "\\small", cap, *inner, "\\end{table}"])
    inner = ["\\resizebox{\\linewidth}{!}{%", "\\begin{tabular}{" + "l" * ncol + "}", "\\toprule", *body, "\\bottomrule",
             "\\end{tabular}}"]
    return "\n".join(["\\begin{table}[htbp]", "\\centering", cap, *inner, "\\end{table}"])


PREAMBLE = r"""\documentclass[11pt,a4paper]{article}
% Built by scripts/paper/build_manuscript_tex.py from the manuscript .txt source. Do not edit by hand:
% edit the .txt and rebuild, so that the .docx and the .tex stay identical in content.
\usepackage{iftex}
\ifPDFTeX
  \usepackage[utf8]{inputenc}
  \usepackage[T1]{fontenc}
  \usepackage{lmodern}
\else
  \usepackage{fontspec}
\fi
\usepackage[margin=1in]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs,tabularx,rotating}
\usepackage{xcolor}
\usepackage[numbers,sort&compress]{natbib}
\usepackage[hidelinks]{hyperref}
\usepackage{microtype}
\graphicspath{{figures/}}
\newcommand{\pending}[1]{\textcolor{red}{\textbf{#1}}}
\setlength{\emergencystretch}{3em}
"""


def build(txt_path=TXT_PATH, out_dir=OUT_DIR):
    lines = Path(txt_path).read_text(encoding="utf-8").splitlines()
    # drop the revision-notes block
    kept, skip = [], False
    for ln in lines:
        s = ln.strip()
        if s == "%%% REVISION NOTES":
            skip = True
        if not skip:
            kept.append(s)
        if s == "%%% END NOTES":
            skip = False
    lines = [s for s in kept if s and s != "---"]
    title = lines[0]
    ref_start = lines.index("References")
    refs = []
    for s in lines[ref_start + 1:]:
        m = REF_RE.match(s)
        if not m:
            raise SystemExit(f"unexpected line in the reference list: {s[:80]}")
        refs.append((int(m.group(1)), m.group(2)))
    if [k for k, _ in refs] != list(range(1, len(refs) + 1)):
        raise SystemExit("reference numbers are not 1..N in order")
    n_refs = len(refs)
    stats = {"pending": 0, "tables": 0, "figures": 0, "sections": 0, "subsections": 0}

    out = [PREAMBLE, "\\title{" + inline(title, 0, stats) + "}", "\\author{\\pending{[[PENDING: authors and affiliations]]}}",
           "\\date{}", "", "\\begin{document}", "\\maketitle", ""]
    body = lines[1:ref_start]
    i, n, pending_caption, expect_sec, cites = 0, len(body), None, 1, 0
    fig_seen, tab_seen = [], []
    out_dir = Path(out_dir)
    (out_dir / "figures").mkdir(parents=True, exist_ok=True)
    while i < n:
        s = body[i]
        fm, sm, ssm, tm = FIGURE_RE.match(s), SECTION_RE.match(s), SUBSECTION_RE.match(s), TABLE_CAP_RE.match(s)
        if s == "Abstract":
            out += ["\\begin{abstract}", inline(body[i + 1], n_refs, stats), "\\end{abstract}", ""]
            i += 2
            continue
        if fm:
            k, cap = int(fm.group(1)), fm.group(2).strip()
            fig_seen.append(k)
            src = FIG_DIR / f"figure_{k}.png"
            if not src.exists():
                raise SystemExit(f"figure file missing: {src}")
            shutil.copyfile(src, out_dir / "figures" / src.name)
            out += ["\\begin{figure}[htbp]", "\\centering", f"\\includegraphics[width={bm_scale(k)}\\linewidth,height=0.8\\textheight,keepaspectratio]{{{src.name}}}",
                    "\\caption{" + inline(cap, n_refs, stats) + "}", "\\end{figure}", ""]
            stats["figures"] += 1
            i += 1
            continue
        if sm and int(sm.group(1)) == expect_sec:
            out += ["\\section{" + inline(sm.group(2), n_refs, stats) + "}", ""]
            expect_sec += 1
            stats["sections"] += 1
            i += 1
            continue
        if ssm:
            if int(ssm.group(1).split(".")[0]) != expect_sec - 1:
                raise SystemExit(f"subsection {ssm.group(1)} is outside section {expect_sec - 1}")
            out += ["\\subsection{" + inline(ssm.group(2), n_refs, stats) + "}", ""]
            stats["subsections"] += 1
            i += 1
            continue
        if tm:
            tab_seen.append(int(tm.group(1)))
            pending_caption = tm.group(2)
            i += 1
            continue
        if s.startswith("$$") and s.endswith("$$") and len(s) > 4:
            out += ["\\[", "".join(MATH_FIX.get(ch, ch) for ch in s[2:-2].strip()), "\\]", ""]
            i += 1
            continue
        if s.startswith("|"):
            rows = []
            while i < n and body[i].startswith("|"):
                cells = [c.strip() for c in body[i].strip("|").split("|")]
                if not all(re.match(r"^:?-{2,}:?$", c) for c in cells):
                    rows.append(cells)
                i += 1
            if pending_caption is None:
                raise SystemExit("table without a 'Table N:' caption line before it")
            out += [table_tex(pending_caption, rows, n_refs, stats), ""]
            pending_caption = None
            stats["tables"] += 1
            continue
        if s.startswith(("- ", "* ")):
            out.append("\\begin{itemize}")
            while i < n and body[i].startswith(("- ", "* ")):
                out.append("\\item " + inline(body[i][2:].strip(), n_refs, stats))
                i += 1
            out += ["\\end{itemize}", ""]
            continue
        nm = NUM_ITEM_RE.match(s)
        if nm:
            out.append("\\begin{enumerate}")
            while i < n and NUM_ITEM_RE.match(body[i]) and not (SECTION_RE.match(body[i]) and int(SECTION_RE.match(body[i]).group(1)) == expect_sec):
                m2 = NUM_ITEM_RE.match(body[i])
                out.append(f"\\item[{m2.group(1)}.] " + inline(m2.group(2), n_refs, stats))
                i += 1
            out += ["\\end{enumerate}", ""]
            continue
        out += [inline(s, n_refs, stats), ""]
        i += 1

    if fig_seen != list(range(1, len(fig_seen) + 1)) or tab_seen != list(range(1, len(tab_seen) + 1)):
        raise SystemExit(f"figures {fig_seen} or tables {tab_seen} are not numbered in order of appearance")
    out += ["\\begin{thebibliography}{" + str(n_refs) + "}"]
    for k, text in refs:
        out.append(f"\\bibitem{{ref{k}}} " + inline(text, 0, stats))
    out += ["\\end{thebibliography}", "", "\\end{document}", ""]
    tex = "\n".join(out)
    cites = len(re.findall(r"\\cite\{", tex))
    (out_dir / "manuscript.tex").write_text(tex, encoding="utf-8")
    print(f"Saved {out_dir / 'manuscript.tex'}")
    print(f"sections {stats['sections']}, subsections {stats['subsections']}, tables {stats['tables']}, "
          f"figures {stats['figures']}, references {n_refs}, citation commands {cites}")
    print(f"PENDING placeholders: {stats['pending']} (plus the author line)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Build the manuscript .tex from the .txt source.")
    ap.add_argument("--input", default=str(TXT_PATH), help="manuscript .txt")
    ap.add_argument("--out-dir", default=str(OUT_DIR), help="output folder (manuscript.tex and figures/)")
    a = ap.parse_args()
    build(a.input, a.out_dir)
