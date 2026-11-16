#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""capstone_to_dir.py — a capstone is a DIRECTORY WITH A README, not a module.

⟡capstone-not-a-barrel.  A capstone `.agda` is a barrel by construction: it
exists to name a roster, and the only way a module can name a roster is to
IMPORT it — so the capstone drags its whole arc into every consumer's core, and
a chain of capstones (one re-exporting the next) compounds it.  A directory
cannot do that.  The attestation is prose; the roster is a table; a consumer
that wants a name binds it at its OWNER.

This tool handles the PURE-BARREL case: a capstone whose body is imports and
comment blocks and NO definitions.  Its content is entirely (prose, roster), so
the conversion is total — nothing is discarded, it changes medium.  A capstone
that DOES define things is not this tool's job: split it with split_lemmas.py
into one-definition-per-file leaves inside the directory, then add the README.

    capstone_to_dir.py <Capstone.agda> ...        # dry run
    capstone_to_dir.py --apply <Capstone.agda> ...

REFUSES a file with any definition (that is the split_lemmas case), so the tool
cannot silently delete content it is not modelling.
"""
import os
import re
import sys

import os as _o, sys as _s
_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from agda_imports import _span_end   # THE statement-span authority (agda_lex-backed); never re-derive
import os as _o, sys as _s
_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from agda_lex import HEADER as _HEADER   # THE header authority; never re-derive

OPTS = re.compile(r"^\{-#\s*OPTIONS")
MODULE = _HEADER   # was ^module\s+(\S+)\s+where — missed 149 parameterized headers + 2 unicode names
IMPORT = re.compile(r"^\s*(?:open\s+)?import\s+(\S+)")
DECL = re.compile(r"^[A-Za-z_][^\s]*\s*:")
COMMENT = re.compile(r"^\s*--")
RULE = re.compile(r"^\s*--\s*-{6,}\s*$")


def parse(path):
    """→ (module, [prose-block], [(mod, names)]) or raise on a definition."""
    lines = open(path, encoding="utf-8").read().split("\n")
    mod = next((MODULE.match(l).group(1) for l in lines if MODULE.match(l)), None)
    prose, roster, cur = [], [], []
    i = 0
    while i < len(lines):
        l = lines[i]
        if DECL.match(l):
            raise SystemExit(f"{path}: defines `{l.split(':')[0].strip()}` — "
                             f"this is the split_lemmas case, not a pure barrel")
        m = IMPORT.match(l)
        if m:
            # an import statement may carry an indented `using (…)` continuation
            # ⚑ span via agda_lex — the naive "every indented line" rule absorbs a
            # following parameterized module header and its telescope.
            j = _span_end(lines, i)
            stmt = lines[i:j]
            text = " ".join(s.strip() for s in stmt)
            names = re.search(r"using\s*\(([^)]*)\)", text)
            roster.append((m.group(1),
                           [n.strip() for n in names.group(1).split(";")] if names else []))
            i = j
            continue
        if COMMENT.match(l) and not RULE.match(l):
            cur.append(re.sub(r"^\s*--\s?", "", l).rstrip())
        elif cur:
            prose.append(cur); cur = []
        i += 1
    if cur:
        prose.append(cur)
    return mod, prose, roster


def render(mod, prose, roster):
    leaf = mod.rsplit(".", 1)[-1]
    out = [f"# {leaf} — {mod}", ""]
    out += ["A capstone is a **directory with a README**, not a module. It ATTESTS a",
            "roster; it does not import one. The former `%s.agda` was a pure barrel —" % leaf,
            "prose and imports, no definitions of its own — so the attestation is prose",
            "and the roster is a table. A consumer that wants one of these names binds",
            "it at its OWNER, directly.", ""]
    body = [b for b in prose if not (len(b) == 1 and b[0].strip() == mod)]
    for blk in body:
        text = "\n".join(blk).strip()
        if not text:
            continue
        out += ["```", text, "```", ""] if any(l.startswith("  ") for l in blk) \
            else [text, ""]
    out += ["## Roster", ""]
    if any(n for _, n in roster):
        out += ["| name | owner |", "|---|---|"]
        for m, names in roster:
            for n in names:
                out.append(f"| `{n}` | `{m}` |")
            if not names:
                out.append(f"| *(whole module)* | `{m}` |")
    else:
        out += ["| owner |", "|---|"] + [f"| `{m}` |" for m, _ in roster]
    out.append("")
    return "\n".join(out)


def main():
    apply = "--apply" in sys.argv
    paths = [a for a in sys.argv[1:] if not a.startswith("--")]
    for p in paths:
        mod, prose, roster = parse(p)
        d = p[:-5]
        md = os.path.join(d, "README.md")
        print(f"{p}\n  -> {md}  ({len(roster)} roster entries, "
              f"{sum(len(n) for _, n in roster)} names)")
        if apply:
            os.makedirs(d, exist_ok=True)
            with open(md, "w", encoding="utf-8") as fh:
                fh.write(render(mod, prose, roster))
            os.remove(p)
    if not apply:
        print("(dry run — pass --apply to write)")


if __name__ == "__main__":
    main()
