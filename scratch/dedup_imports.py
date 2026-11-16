#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Drop byte-identical duplicate import statements from a file.

A parameterized module imported twice is APPLIED twice and elaborated twice, so a
duplicate is a cap cost, not just noise (the ⟡cap-384 discipline in CLAUDE.md).

⚑ SPAN RULE.  This tool used the naive "head plus every following indented line"
rule, which does not delimit an Agda statement: an import sitting above a
PARAMETERIZED module header (`module M (a : A)` / `  (b : B)` / `  where`) swallows
the header and the whole telescope.  That exact rule gutted 33 files in one arc —
`Coxeter/Core.agda` went 76 lines to 3 — and was caught only by the build.  The
depth-aware authority in `agda_lex` is the fix, and it is CALLED here rather than
re-derived; re-deriving it is what produced fifteen divergent copies of this bug.

⚑ DRY-RUN BY DEFAULT.  It previously rewrote every file named on argv with no flag,
no preview and no rollback.  `--apply` is now required, and the apply path snapshots
first (`edit_snapshot`), so a bad run is recoverable.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agda_lex
import edit_snapshot


def dedup(lines):
    """(new_lines, n_dropped) — pure, so the decision is testable without a file."""
    out, seen, dropped, i = [], set(), 0, 0
    spans = {s.start: s for s in agda_lex.statements(lines)
             if s.kind in ("import", "open")}
    while i < len(lines):
        s = spans.get(i)
        if s is None:
            out.append(lines[i])
            i += 1
            continue
        stmt = lines[s.start:s.end]
        key = "\n".join(stmt)
        if key in seen:
            dropped += 1
        else:
            seen.add(key)
            out.extend(stmt)
        i = s.end
    return out, dropped


def _selftest():
    """Counted — a hardcoded total once hid an added case (prune_imports.py:332)."""
    cases = []

    def check(name, got, want):
        cases.append((name, got == want, got, want))

    # THE regression: the span must not eat a parameterized module header.
    src = ["open import Substrate.Foundation.Eq",
           "",
           "module Substrate.Groups.Coxeter.Core",
           "  (Word : Set)",
           "  (_++_ : Word → Word → Word)",
           "  where",
           "",
           "body : Set"]
    got, n = dedup(src)
    check("parameterized module header survives", got, src)
    check("nothing dropped when there is no duplicate", n, 0)

    dup = ["open import A", "open import B", "open import A", "x : Set"]
    got2, n2 = dedup(dup)
    check("exact duplicate dropped", got2, ["open import A", "open import B", "x : Set"])
    check("drop counted", n2, 1)

    # A multi-line import is ONE unit: a duplicate means the whole statement matched,
    # not a repeated head with a different tail.
    multi = ["open import A", "  using (x)", "open import A", "  using (y)", "z : Set"]
    got3, n3 = dedup(multi)
    check("differing tails are NOT duplicates", n3, 0)
    check("multi-line statements preserved", got3, multi)

    ok = sum(1 for _, good, _, _ in cases if good)
    for name, good, got, want in cases:
        if not good:
            print(f"  FAIL {name}\n       got  {got!r}\n       want {want!r}")
    print(f"dedup_imports selftest: {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    apply = "--apply" in sys.argv
    files = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not files:
        print(__doc__)
        print("usage: dedup_imports.py <file>... [--apply]")
        sys.exit(2)
    if apply:
        edit_snapshot.guard(f"dedup_imports ({len(files)} file(s))", files)
    total = 0
    for f in files:
        lines = open(f, encoding="utf-8").read().split("\n")
        new, n = dedup(lines)
        if n:
            total += n
            print(f"{n:3d} {'dropped   ' if apply else 'would drop'}  {f}")
            if apply:
                open(f, "w", encoding="utf-8").write("\n".join(new))
    print(f"{total} duplicate import statement(s) "
          f"{'dropped' if apply else 'found (dry run; pass --apply)'}")
