#!/usr/bin/env python3
"""Number audit: every literal number in the manuscript text must be either a
\\v... macro from generated/values.tex or a commanded / specification /
bibliographic value listed in analysis/number_whitelist.txt.

    python analysis/audit_numbers.py         # prints orphans, exit 1 if any
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]
TEX = PAPER / "manuscript" / "main.tex"
WL = PAPER / "analysis" / "number_whitelist.txt"


def main():
    wl = set()
    for line in WL.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            wl.add(line)
    tex = TEX.read_text()
    body = tex[tex.index("\\begin{document}"):]
    body = re.sub(r"(?<!\\)%.*", "", body)                                  # comments
    body = re.sub(r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}", " ", body, flags=re.S)
    body = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", " ", body, flags=re.S)
    body = re.sub(r"\\section\*\{Author Biographies\}.*", " ", body, flags=re.S)
    body = re.sub(r"\\end\{thebibliography\}.*", " ", body, flags=re.S)     # biographies follow the references
    body = re.sub(r"\\v[A-Za-z]+", " ", body)                               # value macros
    body = re.sub(r"\\fontsize\{[^}]*\}\{[^}]*\}", " ", body)              # font sizes
    body = re.sub(r"[\d.]+\s*(pt|mm|cm|in|em|ex)\b|[\d.]+\\(textwidth|linewidth)", " ", body)   # layout lengths
    body = re.sub(r"\\begin\{(minipage|tabular)\}\{[^}]*\}", " ", body)
    body = re.sub(r"\{@\{\}[^}]*\}", " ", body)                            # tabular specs
    body = re.sub(r"\\(cite|ref|eqref|label|includegraphics|setlength|vspace|hspace)(\[[^\]]*\])?\{[^}]*\}", " ", body)
    body = re.sub(r"\\[A-Za-z]+", " ", body)
    orphans = []
    for m in re.finditer(r"(?<![A-Za-z])(\d+(?:[.,]\d+)*)", body):
        tok = m.group(1).rstrip(".,")
        if tok not in wl:
            ctx = body[max(0, m.start() - 35):m.end() + 25].replace("\n", " ")
            orphans.append((tok, " ".join(ctx.split())))
    if orphans:
        print(f"{len(orphans)} orphan number(s):")
        for tok, ctx in orphans:
            print(f"  {tok:>8}  ...{ctx}...")
        return 1
    print("number audit: OK (every number is a macro or whitelisted)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
