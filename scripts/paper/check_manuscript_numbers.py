#!/usr/bin/env python3
"""Flag numbers in the manuscript's results section that no analysis output supports.

Helper for a human check: it only says "no source value matches this token",
not that the number is wrong.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path("/home/aimslab/lead")
sys.path.insert(0, str(ROOT / "scripts/evaluation"))
from compute_paper_tables import CANONICAL_44  # noqa: E402  (importing does not run main)

DEFAULT_MS = ROOT / ("docs/Distribution-Curated Fine-Tuning Reduces Closed-Loop Standstill at Scale "
                     "in Continuous-Action Autonomous Driving.txt")
DEFAULT_SOURCES = [ROOT / "docs/provenance/paper_reanalysis_manifest.json",
                   ROOT / "docs/provenance/paper_tables_confirmatory_record.json",
                   ROOT / "docs/provenance/same_input_results.json",
                   ROOT / "docs/provenance/fullload_stage1_results.json",
                   ROOT / "docs/provenance/fullload_vs_base_results.json",
                   ROOT / "docs/provenance/fullload_repeat_test_results.json",
                   ROOT / "docs/provenance/fullload_stage2_readings.json",
                   ROOT / "docs/provenance/decoupling_dataset_composition.json"]

UNIT_WORDS = ["routes", "route", "steps", "step", "models", "model", "tests", "test", "seeds", "seed",
              "km/h", "Hz", "m", "s", "epochs", "epoch"]
YEARS = range(2019, 2028)
# Constants and sums that no analysis output contains: (token, text that must be on the same line, reason).
ALLOW = [
    ("220", "220-route", "size of the full Bench2Drive suite"),
    ("−4.0", "point estimate ≤", "threshold of the pre-registered decision rule"),
    ("−3.89", "gate-active bands together", "sum of two reported band differences (−3.11 and −0.78)"),
]

RULES = """\
Scope: text from the line matching '^4\\. [A-Z]' up to the line starting 'References';
  '%%% REVISION NOTES ... %%% END NOTES' blocks and '[[PENDING: ...]]' spans are removed first.
Tokens: integers (thousands separators allowed), decimals, scientific notation
  ('1.0 \\times 10^{-6}', '7.1e-4'), optional sign (+, -, Unicode minus).
Ignored tokens:
  1. numbered headings / list markers at line start ('4.1', '## 4.2', '3. ')
  2. numbers after Table/Figure/Fig./Section/Sec./Eq./Appendix/Algorithm, after the section sign, or inside [12]-style citations
  3. years 2019-2027
  4. route ids (the 44 in CANONICAL_44, or any number right after the word Route/route)
  5. integers < 100 directly followed by one of: @UNITS@
  6. digits glued to letters/hyphens (model names such as Golden-6400, W4A8)
  7. the constants listed in ALLOW (token plus required words on the same line)
Supported if a source value s, |s|, 100*s or 100*|s| rounds to the token at its printed
  precision (d decimals -> round to d decimals; scientific -> 2 significant digits).
Exit status: 1 if any token is unsupported, else 0.
""".replace("@UNITS@", ", ".join(UNIT_WORDS))

NUM = r"[+\-−]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
SCI = (r"[+\-−]?\d+(?:\.\d+)?\s*(?:\\times|×)\s*10\^\{?[+\-−]?\d+\}?"
       r"|[+\-−]?\d+(?:\.\d+)?[eE][+\-−]?\d+")
TOKEN_RE = re.compile(rf"(?<![\w.,\-])(?:{SCI}|{NUM})(?![\w])|(?<=[A-Za-z]\-)\d+")
UNIT_RE = re.compile(r"^\s*(?:\\text\{\s*|\\mathrm\{\s*|\\,|~)?\s*(" + "|".join(re.escape(u) for u in UNIT_WORDS) + r")(?![A-Za-z])")


def flatten(obj, path=""):
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        yield path, float(obj)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from flatten(v, f"{path}.{k}" if path else str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from flatten(v, f"{path}[{i}]")


def results_lines(text):
    """Return list of (lineno, text) for the results section, with notes/PENDING blanked."""
    lines = text.splitlines()
    in_notes = False
    for i, l in enumerate(lines):
        s = l.strip()
        if s == "%%% REVISION NOTES":
            in_notes = True
        if in_notes:
            lines[i] = ""
        if s == "%%% END NOTES":
            in_notes = False
    start = next((i for i, l in enumerate(lines) if re.match(r"^4\. [A-Z]", l)), None)
    if start is None:
        sys.exit("results heading ('4. <Capital>...') not found")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("References")), len(lines))
    block = "\n".join(lines[start:end])
    block = re.sub(r"\[\[PENDING:.*?\]\]", lambda m: re.sub(r"[^\n]", " ", m.group(0)), block, flags=re.S)
    return [(start + 1 + k, l) for k, l in enumerate(block.split("\n"))]


def parse(tok):
    """Return (value, decimals or None, is_sci)."""
    t = tok.replace("−", "-").replace(",", "").replace(" ", "")
    m = re.match(r"^([+\-]?\d+(?:\.\d+)?)(?:\\times|×)10\^\{?([+\-]?\d+)\}?$", t)
    if m:
        return float(m.group(1)) * 10 ** int(m.group(2)), None, True
    if re.search(r"[eE]", t):
        return float(t), None, True
    d = len(t.split(".")[1]) if "." in t else 0
    return float(t), d, False


def sig2(x):
    return float(f"{x:.1e}")


def match(val, d, sci, sources):
    for path, s in sources:
        for c in (s, abs(s), 100 * s, 100 * abs(s)):
            if sci:
                if c != 0 and sig2(c) == sig2(val):
                    return path
            elif abs(c - val) <= 0.5 * 10 ** (-d) + 1e-9:
                return path
    return None


def ignore_reason(line, m, tok, val, d, sci, route_ids):
    pre, post = line[:m.start()], line[m.end():]
    if re.match(r"^\s*(?:#+\s*)?\d+(?:\.\d+)*\.?\s", line) and m.start() <= (len(line) - len(line.lstrip()) + 8) \
            and re.match(r"^\s*(?:#+\s*)?\d+(?:\.\d+)*\.?$", line[:m.end()]):
        return "heading/list marker"
    if re.search(r"(?:Tables?|Figures?|Figs?\.|Sections?|Secs?\.|Eqs?\.|Equations?|Appendix|Algorithm|§)\s*\(?\s*$", pre):
        return "table/figure/section ref"
    if re.search(r"\[[\d,\s–\-]*$", pre) and re.match(r"^[\d,\s–\-]*\]", post):
        return "bracket reference"
    if not sci and d == 0 and val == int(val) and int(val) in YEARS and "," not in tok:
        return "year"
    if tok.lstrip("+-−") in route_ids or re.search(r"[Rr]outes?\s*[`'\"(]?\s*$", pre):
        return "route id"
    if not sci and d == 0 and abs(val) < 100 and UNIT_RE.match(post):
        return "small integer + unit"
    if re.search(r"[A-Za-z]-$", pre):
        return "glued to name"
    for t, needle, reason in ALLOW:
        if tok == t and needle in line:
            return f"allowed constant: {reason}"
    return None


def main():
    ap = argparse.ArgumentParser(description="Check manuscript results numbers against analysis JSONs.",
                                 epilog=RULES, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manuscript", default=str(DEFAULT_MS))
    ap.add_argument("--sources", nargs="+", default=[str(p) for p in DEFAULT_SOURCES])
    ap.add_argument("--show-supported", action="store_true", help="also list supported tokens and the matching source path")
    a = ap.parse_args()

    sources = []
    for p in a.sources:
        sources += [(f"{Path(p).name}:{k}", v) for k, v in flatten(json.loads(Path(p).read_text()))]
    print(f"{len(sources)} numeric source values from {len(a.sources)} file(s)")
    route_ids = set(CANONICAL_44)

    sup = unsup = ign = 0
    rows = []
    for ln, line in results_lines(Path(a.manuscript).read_text(encoding="utf-8")):
        for m in TOKEN_RE.finditer(line):
            tok = m.group(0)
            val, d, sci = parse(tok)
            why = ignore_reason(line, m, tok, val, d, sci, route_ids)
            if why:
                ign += 1
                continue
            hit = match(val, d, sci, sources)
            ctx = line[max(0, m.start() - 30):m.end() + 30].replace("\n", " ")
            if hit:
                sup += 1
                if a.show_supported:
                    print(f"  ok   L{ln:<4} {tok:<14} <- {hit}")
            else:
                unsup += 1
                rows.append((ln, tok, ctx))
    if rows:
        print(f"\n{'line':>5}  {'token':<16} context")
        for ln, tok, ctx in rows:
            print(f"{ln:>5}  {tok:<16} ...{ctx}...")
    print(f"\nsupported: {sup}  unsupported: {unsup}  ignored: {ign}")
    return 1 if unsup else 0


if __name__ == "__main__":
    sys.exit(main())
