#!/usr/bin/env python3
"""Build docs/latex/supplement.tex from docs/manuscript_supplement.txt.

Uses the text conversion of build_manuscript_tex.py (imported, not changed). Differences from the main text:
no abstract and no reference list (bracketed numbers refer to the reference list of the main text and stay as
text), headings of the form "## S4.1 Title", tables "Table S1: ...", figures "[[FIGURE S1: ...]]".

Usage: python3 scripts/paper/build_supplement_tex.py [--input docs/manuscript_supplement.txt] [--out-dir docs/latex]
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import authors  # noqa: E402
import build_manuscript_tex as bm  # noqa: E402

TXT_PATH = bm.ROOT / "docs/manuscript_supplement.txt"
HEAD_RE = re.compile(r"^## (S\d+(?:\.\d+)?) (.+)$")
FIGURE_RE = re.compile(r"^\[\[FIGURE\s+S(\d+)\s*:\s*(.*?)\]\]$")
TABLE_CAP_RE = re.compile(r"^Table S(\d+): (.*)$")


def build(txt_path=TXT_PATH, out_dir=bm.OUT_DIR):
    lines = [s.strip() for s in Path(txt_path).read_text(encoding="utf-8").splitlines()]
    lines = [s for s in lines if s and s != "---"]
    stats = {"pending": 0, "tables": 0, "figures": 0, "sections": 0, "subsections": 0}
    out_dir = Path(out_dir)
    (out_dir / "figures").mkdir(parents=True, exist_ok=True)
    out = [bm.PREAMBLE.replace("build_manuscript_tex.py from the manuscript .txt source", "build_supplement_tex.py from the supplement .txt source"),
           "\\renewcommand{\\thetable}{S\\arabic{table}}", "\\renewcommand{\\thefigure}{S\\arabic{figure}}",
           "\\title{" + bm.inline(lines[0], 0, stats) + "}", "\\author{" + authors.latex_author_block() + "}",
           "\\date{}", "", "\\begin{document}", "\\maketitle", ""]
    body, i, pending_caption, fig_seen, tab_seen = lines[1:], 0, None, [], []
    n = len(body)
    while i < n:
        s = body[i]
        hm, fm, tm = HEAD_RE.match(s), FIGURE_RE.match(s), TABLE_CAP_RE.match(s)
        if hm:
            level = "subsection" if "." in hm.group(1) else "section"
            out += [f"\\{level}*{{" + bm.inline(hm.group(1) + " " + hm.group(2), 0, stats) + "}", ""]
            stats[level + "s"] += 1
            i += 1
            continue
        if fm:
            k = int(fm.group(1))
            fig_seen.append(k)
            src = bm.FIG_DIR / f"figure_S{k}.png"
            if not src.exists():
                raise SystemExit(f"figure file missing: {src}")
            shutil.copyfile(src, out_dir / "figures" / src.name)
            out += ["\\begin{figure}[htbp]", "\\centering",
                    f"\\includegraphics[width=\\linewidth,height=0.8\\textheight,keepaspectratio]{{{src.name}}}",
                    "\\caption{" + bm.inline(fm.group(2).strip(), 0, stats) + "}", "\\end{figure}", ""]
            stats["figures"] += 1
            i += 1
            continue
        if tm:
            tab_seen.append(int(tm.group(1)))
            pending_caption = tm.group(2)
            i += 1
            continue
        if s.startswith("$$") and s.endswith("$$") and len(s) > 4:
            out += ["\\[", "".join(bm.MATH_FIX.get(ch, ch) for ch in s[2:-2].strip()), "\\]", ""]
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
                raise SystemExit("table without a 'Table Sn:' caption line before it")
            out += [bm.table_tex(pending_caption, rows, 0, stats), ""]
            pending_caption = None
            stats["tables"] += 1
            continue
        if s.startswith(("- ", "* ")):
            out.append("\\begin{itemize}")
            while i < n and body[i].startswith(("- ", "* ")):
                out.append("\\item " + bm.inline(body[i][2:].strip(), 0, stats))
                i += 1
            out += ["\\end{itemize}", ""]
            continue
        if bm.NUM_ITEM_RE.match(s):
            out.append("\\begin{enumerate}")
            while i < n and bm.NUM_ITEM_RE.match(body[i]):
                m2 = bm.NUM_ITEM_RE.match(body[i])
                out.append(f"\\item[{m2.group(1)}.] " + bm.inline(m2.group(2), 0, stats))
                i += 1
            out += ["\\end{enumerate}", ""]
            continue
        out += [bm.inline(s, 0, stats), ""]
        i += 1
    if fig_seen != list(range(1, len(fig_seen) + 1)) or tab_seen != list(range(1, len(tab_seen) + 1)):
        raise SystemExit(f"figures {fig_seen} or tables {tab_seen} are not numbered in order of appearance")
    out += ["\\end{document}", ""]
    (out_dir / "supplement.tex").write_text("\n".join(out), encoding="utf-8")
    print(f"Saved {out_dir / 'supplement.tex'}")
    print(f"sections {stats['sections']}, subsections {stats['subsections']}, tables {stats['tables']}, figures {stats['figures']}")
    print(f"PENDING placeholders: {stats['pending']} ")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Build the supplement .tex from the .txt source.")
    ap.add_argument("--input", default=str(TXT_PATH))
    ap.add_argument("--out-dir", default=str(bm.OUT_DIR))
    a = ap.parse_args()
    build(a.input, a.out_dir)
