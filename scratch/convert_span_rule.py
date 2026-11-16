#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Convert a tool's hand-rolled statement-span loop onto `agda_lex` (the authority).

WHY A SCRIPT AND NOT EIGHT HAND-EDITS.  Hand-patching each site is precisely what
produced fifteen divergent copies of this rule in the first place: two files
(`scope_fix.py`, `decompose_rewrite.py`) even have one GUARDED site and one naive
site, the signature of per-site fixing without a shared home.  A mechanical
conversion is uniform, reviewable as one diff, and re-runnable when the next copy
appears.

THE BUG BEING RETIRED.  `while lines[j].startswith(" ") and lines[j].strip(): j+=1`
treats any indented line as a continuation.  An Agda statement is not delimited by
indentation: an import above a PARAMETERIZED module header
(`module M (a : A)` / `  (b : B)` / `  where`) absorbs the header and its whole
telescope, so a caller that moves or deletes the span takes the module with it.
Measured: 33 files gutted in one arc, `Coxeter/Core.agda` 76 lines -> 3, caught only
by the build — twice, from two different copies of the rule.

`agda_lex._continues` is depth-aware (inside an open paren nothing opens a new
statement, so a wrapped `using (…; module W)` re-export survives) and stops at any
line opening a declaration (F17: an indented `x : Nat` after an import).  It carries
the regression corpus: `python3 scratch/agda_lex.py`.

Emits `_span_end(lines, i)` into the target and rewrites each loop to call it.
DRY-RUN by default; `--apply` snapshots first.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import edit_snapshot

# The naive loop, in the spellings actually present. Group 1 = the index variable
# being advanced, group 2 = the list. `j+1`-style probes are handled separately
# because they advance an INCLUSIVE end rather than an exclusive one.
NAIVE = re.compile(
    r"^(?P<ind>[ \t]*)while\s+(?P<idx>\w+)\s*<\s*len\((?P<lst>\w+)\)\s+and\s+"
    r"(?P=lst)\[(?P=idx)\]\.startswith\(\" \"\)\s+and\s+(?P=lst)\[(?P=idx)\]\.strip\(\)\s*:"
    r"(?P<body>.*)$", re.M)

# ⚑ THE INCLUSIVE SPELLING.  Two sites advance an INCLUSIVE end by probing `j+1`
# (`while j+1 < len(L) and L[j+1]...: j+=1`), so `j` ends ON the last line rather
# than past it.  A converter that matched only the exclusive form would report
# "converted" while leaving these live — the same silent-miss failure this whole
# exercise is retiring.  Detected separately and converted to `_span_end(...) - 1`.
NAIVE_INCL = re.compile(
    r"^(?P<ind>[ \t]*)while\s+(?P<idx>\w+)\s*\+\s*1\s*<\s*len\((?P<lst>\w+)\)\s+and\s+"
    r"(?P=lst)\[(?P=idx)\s*\+\s*1\]\.startswith\(\" \"\)\s+and\s+"
    r"(?P=lst)\[(?P=idx)\s*\+\s*1\]\.strip\(\)\s*:(?P<body>.*)$", re.M)

HELPER = '''
# ⚑ SPAN RULE — the one authority (scratch/agda_lex.py), not re-derived here.
# Indentation does NOT delimit an Agda statement: the naive "every indented line
# continues" loop absorbs the indented parameter telescope of a following
# `module M (a : A) … where` header, so a caller that moves or deletes the span
# takes the module with it (measured: 33 files gutted, Coxeter/Core.agda 76 -> 3).
def _span_end(lines, i):
    """EXCLUSIVE end of the statement starting at lines[i]."""
    import agda_lex
    j = i + 1
    depth = agda_lex._depth_after(agda_lex.mask_comments(lines[i]), 0)
    while j < len(lines) and agda_lex._continues(lines[j], depth):
        depth = agda_lex._depth_after(agda_lex.mask_comments(lines[j]), depth)
        j += 1
    return j
'''

PREAMBLE = ("import os as _os, sys as _sys\n"
            "_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))\n")


def _simple(m):
    """Is the loop body a bare advance (safe to replace) or does it side-effect?"""
    idx = m.group("idx")
    return m.group("body").strip() in ("", f"{idx}+=1", f"{idx} += 1")


def convert(src):
    """(new_src, n_sites). Pure — the decision is inspectable without writing."""
    hits = [(m, False) for m in NAIVE.finditer(src)] + \
           [(m, True) for m in NAIVE_INCL.finditer(src)]
    hits.sort(key=lambda t: t[0].start())
    if not hits:
        return src, 0
    out = src
    for m, incl in reversed(hits):
        ind, idx, lst = m.group("ind"), m.group("idx"), m.group("lst")
        # The loop's body may carry a side effect (e.g. `stmt.append(L[j])` or
        # `skip.add(k)`); replacing the loop wholesale would drop it. Those sites
        # are REPORTED, not rewritten — a silent drop is the failure this retires.
        if not _simple(m):
            continue
        # exclusive form: the index starts ON the head and ends PAST the span, so the
        # head is idx-1.  inclusive form: idx stays on the head throughout and must
        # end ON the last line, hence the -1.
        rhs = (f"_span_end({lst}, {idx}) - 1" if incl
               else f"_span_end({lst}, {idx} - 1)")
        out = out[:m.start()] + f"{ind}{idx} = {rhs}" + out[m.end():]
    n = sum(1 for m, _ in hits if _simple(m))
    if n and "_span_end" not in src:
        # Insert the helper after the module docstring / first import block.
        lines = out.split("\n")
        k = 0
        for i, l in enumerate(lines[:40]):
            if l.startswith(("import ", "from ")):
                k = i + 1
        out = "\n".join(lines[:k]) + "\n" + PREAMBLE + HELPER + "\n".join(lines[k:])
    return out, n


def report_complex(path, src):
    """Sites whose loop body has a side effect — these need a human, not a regex."""
    out = []
    for m in NAIVE.finditer(src):
        body = m.group("body").strip()
        if body not in ("", f"{m.group('idx')}+=1", f"{m.group('idx')} += 1"):
            out.append((src[:m.start()].count("\n") + 1, body))
    return out


if __name__ == "__main__":
    files = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not files:
        print(__doc__)
        print("usage: convert_span_rule.py <file>... (--apply | --dry-run)")
        sys.exit(2)
    # ⚑ ONE ACT: state the intent AND snapshot, BEFORE `apply` is bound.  The
    # `guard` this replaces sat under `if apply:` — correct where it ran, but
    # reached only once apply was already TRUE, so the UNSTATED case (the whole
    # population the contract measures) never reached it.
    _es_ = edit_snapshot
    _es_.require_at_entry(f"convert_span_rule ({len(files)} file(s))", paths=files)
    apply = "--apply" in sys.argv
    total = manual = 0
    for f in files:
        src = open(f, encoding="utf-8").read()
        new, n = convert(src)
        cx = report_complex(f, src)
        if n:
            total += n
            print(f"{n:3d} {'converted' if apply else 'would convert'}  {f}")
            if apply:
                open(f, "w", encoding="utf-8").write(new)
        for ln, body in cx:
            manual += 1
            print(f"    ⚠ MANUAL {f}:{ln} — loop body has a side effect: {body!r}")
    print(f"{total} site(s) {'converted' if apply else 'convertible'}; "
          f"{manual} need(s) a hand edit (reported, never silently skipped)")
