#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Repoint operator SECTIONS at the operator that is actually in scope.

THE DEFECT.  A section is a partially-applied operator written with its hole:
`(_+ x)` is the right section of `_+_`.  When a rename-at-source moves an
operator — §13 moved F₂'s addition to `_+F_` — every section still spelling the
old operator becomes unparseable, and Agda reports

    [NoParseForApplication] Could not parse the application _+ lookup v i
    Operators used in the grammar: None

"None" rather than a candidate, because the section names an operator that no
longer exists in that scope.  MEASURED WITNESS: `Algebra/F2/Vector.agda:167`,
whose lemma `+-identityˡ` is stated over `_+F_` while the file imports
`Foundation.Nat.Plus`'s `_+_` — a different operator on ℕ.

WHY THIS IS A TOOL AND NOT A JUDGEMENT CALL (user, 2026-08-01: *"I'm pointing you
at fixing the tooling every time I see you needing to run more than one tooling
command, or manipulating program output — that indicates you're applying reasoning
not codified"*).  The reasoning was:

    unresolved section  +  exactly one in-scope operator sharing its stem
                        ⇒  rewrite it

which I had been executing by running `--sections`, reading `ambiguous:2` by eye,
adjusting a heuristic, and re-running.  Four commands and two eyeball steps for
what is one predicate.  It is codified here, applied in one pass, and the
ambiguous remainder is REPORTED rather than guessed.

MEASURED POPULATION: **590 unresolved sections tree-wide, 80 with exactly one
in-scope candidate.**  The other 510 are NOT this tool's business — several
candidates is a human decision, and a rewrite there would be a coin flip.

    fix_sections.py                    # report every site + its verdict
    fix_sections.py <file> ...         # scope to files
    fix_sections.py --apply            # rewrite the unambiguous ones
    fix_sections.py --rows             # EVERY site on its own line, actionable or not, each with
                                       # its target (`-> want`) or its blocking reason (`[why]`).
                                       # The default report prints the actionable sites in full
                                       # and collapses the rest into a by-operator TALLY, which is
                                       # the right summary and cannot be read FROM: it says 510
                                       # sites are ambiguous without saying which. `--rows` is the
                                       # un-collapsed population, for reviewing the remainder the
                                       # tool deliberately refuses to guess at.
"""
import os, sys, re

import os as _o, sys as _s
_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import agda_lex                              # THE section / positional authority
import agda_defs                             # THE name -> home authority
from rename_at_source import spellings, apply_spellings   # THE two-spelling rule

_SNAPPED = []


def _snapshot_once(path):
    if _SNAPPED:
        return
    _SNAPPED.append(True)
    try:
        import edit_snapshot
        # ⚑ `intent="apply"` IS ENTAILED BY THE BRANCH: the sole caller is
        # `apply_plan` under `if apply:`, immediately above an unconditional write.
        # Re-reading argv here could only DISAGREE with the branch that decided —
        # and it did: `--selftest` exited 2 because argv carries neither mutation
        # flag while `apply_plan(..., True)` is exactly what the suite drives.
        edit_snapshot.guard('fix_sections', [path], intent="apply")
    except Exception as e:
        print(f"   ⚠ snapshot unavailable ({e}) — recover via git if needed")


def plan(paths=None):
    """[(path, lineno, section, names, want, why)] — DECIDED, not applied.

    `want` is the operator to rewrite to, or None; `why` is `ok` / `no-candidate`
    / `ambiguous:<n>:<cands>` so a reviewer of 590 rows never has to ask the tool
    a second question.
    """
    idx = agda_defs.def_index()
    out, cache = [], {}
    for p, ln, txt, op, _homes in agda_lex.unresolved_sections(paths):
        if p not in cache:
            cache[p] = open(p, encoding="utf-8", errors="replace").read()
        want, why = agda_lex._intended(cache[p], ln, op, idx)
        out.append((p, ln, txt, op, want, why))
    return out


def apply_plan(rows, apply=False):
    """Rewrite each unambiguous site IN PLACE. Returns (files_touched, sites)."""
    by_file = {}
    for p, ln, txt, op, want, why in rows:
        if want:
            by_file.setdefault(p, []).append((ln, op, want))
    touched = sites = 0
    for p, edits in sorted(by_file.items()):
        src = open(p, encoding="utf-8", errors="replace").read()
        lines = src.split("\n")
        # ⚑ REWRITE ONLY THE NAMED LINES.  A file-wide substitution would also hit
        # the operator's own DECLARATION and any legitimate use of the old name —
        # the section is a POSITIONAL fact, so the edit must be positional too.
        for ln, op, want in edits:
            i = ln - 1
            if 0 <= i < len(lines):
                lines[i] = apply_spellings(lines[i], spellings(op, want))
                sites += 1
        if apply:
            _snapshot_once(p)
            open(p, "w", encoding="utf-8").write("\n".join(lines))
        touched += 1
    return touched, sites


def _selftest():
    """Counted from len(cases)."""
    cases = []

    def check(name, got, want):
        cases.append((name, got == want, got, want))

    # ⚑ THE REWRITE IS POSITIONAL AND TWO-SPELLING.  A section writes the BARE
    # form (`_+` / `+_`); the declaration writes `_+_`.  Rewriting only the
    # underscore form leaves the section untouched — the exact bug
    # `rename_at_source.spellings` exists to prevent, which is why this reuses it
    # rather than re-deriving a third copy.
    subs = spellings("_+_", "_+F_")
    check("a right section is rewritten", apply_spellings("cong (_+ x) p", subs),
          "cong (_+F x) p")
    check("a left section too", apply_spellings("cong (x +_) p", subs),
          "cong (x +F_) p")

    # ⚑ ONLY THE NAMED LINE.  A file-wide sweep would rewrite the operator's own
    # declaration; the section is a POSITIONAL fact.
    rows = [("X.agda", 2, "_+", "_+_", "_+F_", "ok")]
    import tempfile, shutil
    d = tempfile.mkdtemp()
    try:
        p = os.path.join(d, "X.agda")
        open(p, "w", encoding="utf-8").write("_+_ : A\nf = cong (_+ x) p\n")
        t, s = apply_plan([(p, 2, "_+", "_+_", "_+F_", "ok")], apply=True)
        out = open(p, encoding="utf-8").read().split("\n")
        check("the declaration line is untouched", out[0], "_+_ : A")
        check("the section line is rewritten", out[1], "f = cong (_+F x) p")
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # ⚑ AMBIGUOUS SITES ARE NOT REWRITTEN — several candidates is a human call.
    t, s = apply_plan([("X.agda", 1, "_+", "_+_", None, "ambiguous:2:_++_,_+F_")],
                      apply=False)
    check("an ambiguous site is skipped", (t, s), (0, 0))

    ok = sum(1 for _n, g, _got, _w in cases if g)
    for n, g, got, w in cases:
        if not g:
            print(f"  FAIL {n}\n       got {got!r} want {w!r}")
    print(f"fix_sections selftest: {ok}/{len(cases)}")
    return ok == len(cases)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if _selftest() else 1)
    args = [a for a in sys.argv[1:] if not a.startswith("-") and os.path.exists(a)]
    # ⚑ THE PLAN NAMES THE TARGETS, ARGV DOES NOT.  A bare run plans TREE-WIDE
    # (`plan(None)`), so a snapshot keyed on argv would copy nothing while the run
    # rewrites 586 sites.  `plan` is a pure DECISION (it writes nothing — that is
    # `apply_plan`), so computing it before the gate is safe and is the only way to
    # know what a snapshot must cover.
    # ⚑ ONE ACT, and BEFORE `ap` is bound. `_snapshot_once` fires at the first
    # pending write inside `apply_plan`, which a run with zero actionable rows
    # never reaches.
    rows = plan(args or None)
    import edit_snapshot as _es
    _es.require_at_entry("fix_sections", paths=sorted({r[0] for r in rows}))
    ap = "--apply" in sys.argv
    # ⚑ ROWS BY DEFAULT ONLY WHEN THE POPULATION IS READABLE.  A tree-wide run
    # emits 586 rows, and every consumer (me, twice) then pipes it through
    # `tail` — which is reasoning performed on program output instead of by the
    # program.  So the tool summarizes ITSELF: actionable rows always, and the
    # unactionable remainder GROUPED BY REASON, since "510 left for a human" is
    # only a worklist if you can see which operators they are.
    todo = [r for r in rows if r[4]]
    for p, ln, txt, op, want, why in todo:
        print(f"{p}:{ln}  {txt}  {op}  -> {want}")
    if len(rows) - len(todo):
        by_op = {}
        for p, ln, txt, op, want, why in rows:
            if not want:
                by_op.setdefault((op, why.split(":")[0]), []).append(f"{p}:{ln}")
        print(f"\n-- {len(rows)-len(todo)} NOT actionable, by operator --")
        for (op, why), where in sorted(by_op.items(), key=lambda kv: -len(kv[1])):
            print(f"  {len(where):>4}  {op:<12} {why:<14} e.g. {where[0]}")
    if "--rows" in sys.argv:
        for p, ln, txt, op, want, why in rows:
            print(f"{p}:{ln}  {txt}  {op}" + (f"  -> {want}" if want else f"  [{why}]"))
    t, s = apply_plan(rows, ap)
    verb = "rewrote" if ap else "WOULD rewrite"
    print(f"{len(rows)} unresolved section(s); {verb} {s} site(s) in {t} file(s); "
          f"{len(rows)-s} left for a human"
          + ("" if ap else "   (dry run — pass --apply)"))
