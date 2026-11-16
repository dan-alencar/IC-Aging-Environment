#!/usr/bin/env python3
"""IEEE D&T budget check: words (body + references + bios) + 200 per figure/table.

    python analysis/wordcount.py [manuscript/main.tex]

Counts words in the compiled text of each part, using detex-like stripping of
the LaTeX source: macros expand to one word, math to one word, comments and
the preamble are dropped. Also checks the reference count (<= 12), the title
(<= 9 words) and the abstract (~100 words).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]
LIMIT_WORDS, LIMIT_REFS, LIMIT_TITLE = 5000, 12, 9


def strip(tex: str) -> str:
    tex = re.sub(r"(?<!\\)%.*", "", tex)
    tex = re.sub(r"\\begin\{(figure\*?|table\*?|tikzpicture|equation|tabular)\}.*?\\end\{\1\}", " ", tex, flags=re.S)
    tex = re.sub(r"\$\$.*?\$\$|\$[^$]*\$", " X ", tex, flags=re.S)
    tex = re.sub(r"\\(SI|SIrange|num)\{([^}]*)\}(\{([^}]*)\})?(\{([^}]*)\})?", r" \2 \4 ", tex)
    tex = re.sub(r"\\(cite|ref|eqref|label)\{[^}]*\}", " ", tex)
    tex = re.sub(r"\\(textbf|emph|textit|textsc|mbox|footnote|footnotetext)\{", " ", tex)
    tex = re.sub(r"\\v[A-Za-z]+", " 0 ", tex)          # value macros count as one word
    tex = re.sub(r"\\[A-Za-z]+\*?(\[[^\]]*\])?", " ", tex)
    tex = re.sub(r"[{}~\\&]", " ", tex)
    return tex


def words(tex: str) -> int:
    return len([w for w in strip(tex).split() if re.search(r"[A-Za-z0-9]", w)])


def section(tex, start, end):
    i = tex.find(start)
    j = tex.find(end, i + 1) if end else len(tex)
    return tex[i:j] if i >= 0 else ""


def main(argv):
    path = Path(argv[1]) if len(argv) > 1 else PAPER / "manuscript" / "main.tex"
    tex = path.read_text()
    tex_nocomment = re.sub(r"(?<!\\)%.*", "", tex)
    m = re.search(r"\\newcommand\{\\dttitle\}\{([^}]*)\}", tex_nocomment) or \
        re.search(r"\\LARGE\\bfseries (.*?)\}\\\\\[8pt\]", tex_nocomment, flags=re.S)
    title = re.sub(r"\\\\(\[[^\]]*\])?", " ", m.group(1)) if m else ""
    abstract = section(tex_nocomment, "Abstract", "Keywords")
    # body = everything after the title block (D&T features have no "Introduction" heading)
    start = next(m for m in ("\\dtleadin{", "\\vspace{6pt}}]", "\\section{Introduction}") if m in tex_nocomment)
    body = section(tex_nocomment, start, "\\begin{thebibliography}")
    refs = section(tex_nocomment, "\\begin{thebibliography}", "\\end{thebibliography}")
    bios = (section(tex_nocomment, "\\section*{Author Biographies}", "\\end{document}")
            or section(tex_nocomment, "\\end{thebibliography}", "\\end{document}"))
    n_fig = len(re.findall(r"\\begin\{figure\*?\}", tex_nocomment))
    n_tab = len(re.findall(r"\\begin\{table\*?\}", tex_nocomment))
    n_refs = len(re.findall(r"\\bibitem\{", tex_nocomment))
    # captions are counted inside the 200-word float allowance
    w_abs, w_body, w_refs, w_bios = words(abstract), words(body), words(refs), words(bios)
    total = w_abs + w_body + w_refs + w_bios + 200 * (n_fig + n_tab)
    print(f"title words     {len(title.split()):5d}  (limit {LIMIT_TITLE}) : {title.strip()}")
    print(f"abstract        {w_abs:5d}  (target ~100)")
    print(f"body            {w_body:5d}")
    print(f"references      {w_refs:5d}  ({n_refs} refs, limit {LIMIT_REFS})")
    print(f"bios            {w_bios:5d}")
    print(f"figures+tables  {200 * (n_fig + n_tab):5d}  ({n_fig} fig, {n_tab} tab x 200)")
    print(f"TOTAL           {total:5d}  (limit {LIMIT_WORDS}) {'OK' if total <= LIMIT_WORDS else 'OVER'}")
    ok = total <= LIMIT_WORDS and n_refs <= LIMIT_REFS and len(title.split()) <= LIMIT_TITLE
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
