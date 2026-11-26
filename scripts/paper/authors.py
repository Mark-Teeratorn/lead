"""Author list of the manuscript, first to last, used by every builder (Word, article PDF, IEEE Access PDF)."""

AUTHORS = [
    ("Teeratorn", "Kanjanarajit", "teeratorn6810@gmail.com"),
    ("Noppawit", "Tharakittikirati", None),
    ("Paveetas", "Anantachaimontree", None),
    ("Poom", "Konghuayrob", None),     # advisor (Assistant Professor); IEEE bylines carry no academic titles
]
# Only the corresponding author's e-mail is printed.
AFFILIATION = "King Mongkut's Institute of Technology Ladkrabang, Bangkok 10520, Thailand"
CORRESPONDING = 0          # index into AUTHORS
# ORCID iDs (entered in the IEEE submission system; IEEE adds the icon at publication)
ORCID = {"Teeratorn Kanjanarajit": "0009-0000-7369-0477"}
# Disclosure of AI use (IEEE policy: in the Acknowledgment)
AI_DISCLOSURE = ("The authors used Claude (Anthropic) for text editing and to improve the grammar and readability "
                 "of this article. The authors reviewed and edited all output and take full responsibility for the content.")


def names():
    return [f"{g} {f}" for g, f, _ in AUTHORS]


def name_list():
    n = names()
    return n[0] if len(n) == 1 else ", ".join(n[:-1]) + " and " + n[-1]


def emails():
    return [e for _, _, e in AUTHORS if e]


def corresponding_line():
    return "Corresponding author: " + names()[CORRESPONDING] + " (e-mail: " + AUTHORS[CORRESPONDING][2] + ")"


def latex_author_block():
    """\\author{...} body for the article class."""
    # the article class sets \\author in a tabular, which does not wrap: two lines of names
    n = names()
    k = (len(n) + 1) // 2
    byline = ", ".join(n[:k]) + ",\\\\\n" + (", ".join(n[k:-1]) + " and " + n[-1] if len(n) - k > 1 else "and " + n[-1]) \
        if len(n) > 2 else name_list()
    return (byline + "\\\\[4pt]\n\\normalsize " + AFFILIATION + "\\\\\n\\small Corresponding author: "
            + names()[CORRESPONDING] + " (e-mail: \\nolinkurl{" + AUTHORS[CORRESPONDING][2] + "})")
