#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Delete `renaming (old to new)` clauses whose NEW name is never used.

⟡ban: a Substrate import may not carry `using`/`renaming`/`hiding`/`as`.  Most of
the tree's renaming debt is not a live alias at all — MEASURED in
`Category/UniversalProperty/ExtrudeCoEmitGraded/`: **3244 of 3264 clauses name
something DEAD**, i.e. the new name occurs exactly once, on its own import line.
That is ~90% of the tree-wide renaming census.

WHY THIS IS A SEPARATE TOOL.  Nothing else removes them, each for a stated reason:
  * `prune_imports.should_keep` treats renaming/`as` imports as UNTOUCHABLE by
    design (it drops unused BARE imports; measured: 2927 lines over the same 272
    files, with all 3264 clauses left standing);
  * `fix_stale_using` repairs `using` lists from BUILD LOGS — these names are not
    stale, they are unused;
  * `rewire_to_leaves` rewrites `using` lists onto leaves and does not parse
    `renaming` at all.

WHY IT IS SAFE.  The dangerous case for un-renaming is CAPTURE: rewriting `new`
back to `old` can rebind a use site to a different provider (measured witness:
`Algebra/Polynomial/Graded/Defs.agda`, where `_ℕ+_`→`_+_` would capture into a
module parameter).  **A DEAD clause has no use sites**, so there is nothing to
capture.  This tool therefore does NOT rewrite the body — it deletes a clause
naming a name the body never mentions, and refuses everything else.

The live aliases (20 in that family) are a different job: they need the
per-use-site scope gate (`agda_lex.binds_at`) and a token-conservation ledger.

Usage:  drop_dead_renames.py <file-or-dir> ... [--apply]      (default: dry run)
        drop_dead_renames.py [<file-or-dir> …] --verdicts
              # THE CENSUS OVER EVERY LIVE RENAMING CLAUSE, classified: how many can be
              # un-renamed and which are blocked by what. Read-only; never writes.
              # ⚑ BUILT BECAUSE `unrename_verdict` WAS UNREACHABLE FROM A SHELL. The
              # predicate was written and selftested and had exactly one caller, so the
              # corpus question every consumer actually asks could only be answered by
              # re-deriving it in a throwaway script — the `rewire_only` shape (a def with
              # no reachable call) in a PREDICATE rather than a command, and the reason
              # the A2/A3 worklist figures were quoted from a measurement nobody could
              # repeat. Keyed `path::old->new`, so a class is a SET OF KEYS, not a count.
        drop_dead_renames.py --selftest

⚑ A BARE RUN DEFAULTS TO THE WHOLE `agda/` TREE, deliberately: an empty target list once
produced a clean report over ZERO files, which is the guard-degraded-to-measuring-nothing shape
in the tool's own default path.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import agda_lex
from scope_fix import _rename_pairs   # THE renaming-clause parser; never re-derive

# ⚑ ANCHORED TO THIS FILE, not to the cwd.  `agda` resolves module names against
# the INVOCATION directory, and plan section 30 records five fixtures that
# "passed" only because a relative root silently resolved to nothing.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IMPORT = re.compile(r"^\s*(?:open\s+)?import\s+(Substrate\S*)")
WORD = lambda n: re.compile(r"(?<![^\s(){}\[\];,])" + re.escape(n) + r"(?![^\s(){}\[\];,])")


def body_without(lines, keep_out):
    """The file's text minus every import statement (so a name cannot match itself)."""
    return "\n".join("" if i in keep_out else l for i, l in enumerate(lines))


def dead_pairs(path):
    """[(lineno, old, new)] for clauses whose NEW name never appears outside imports."""
    raw = open(path, encoding="utf-8", errors="replace").read()
    src = agda_lex.mask_comments(raw)
    lines = src.split("\n")
    # ⚑ THE WHOLE STATEMENT SPAN, not just the head line.  Blanking only lines
    # that match IMPORT leaves a CONTINUATION (`  renaming (a to bA)`) in the
    # "body", so the new name matches ITSELF and every wrapped clause reads as
    # live.  Same self-match that made my step-2 classifier report 100%
    # unfixable — recurring because "body" is easy to define one line at a time.
    imp_lines = set()
    for st in agda_lex.statements(lines):
        if st.kind in ("import", "open") and IMPORT.match(lines[st.start]):
            imp_lines.update(range(st.start, st.end))
    body = body_without(lines, imp_lines)
    out = []
    # ⚑ STATEMENT, NOT LINE.  `lines[i]` misses a WRAPPED import:
    #     open import Substrate.Foundation.Nat.SLesInjective
    #       renaming (_<_ to _<ℕ_; _≤_ to _≤ℕ_)
    # the `renaming` lives on the CONTINUATION, so a single-line read finds
    # nothing and the clause survives.  MEASURED: this hid clauses in the 40
    # ban keys that "held steady" all session while everything else moved.
    # This is the span defect this arc retired in fifteen other tools —
    # reproduced in a tool written today, which is why `agda_lex.statements`
    # is THE authority and a bare `lines[i]` is always suspect.
    for st in agda_lex.statements(lines):
        if st.kind not in ("import", "open"):
            continue
        if not IMPORT.match(lines[st.start]):
            continue
        for old, new in _rename_pairs(st.text):
            # ⚑ SECOND PREDICATE: `new == old` is ALWAYS deletable, regardless of use.
            # `renaming (X to X)` binds a name to itself — it carries no meaning and
            # only ban debt, yet the primary predicate ("the new name is unused")
            # cannot see it, because the name IS used; that is what the alias is for.
            # MEASURED: 4 tree-wide, and 3 of them (`_+F_ to _+F_`) are MY OWN residue
            # from repointing clauses after the Algebra.F2 `_+_` rename at source —
            # a rename-at-source turns every consumer's alias into a self-rename when
            # the alias already matched the new name. So this is not a rarity, it is
            # the standing aftermath of the rename tool, and it needed its own rule.
            if old == new or not WORD(new).search(body):
                out.append((st.start, old, new))
    return out


def rewrite(path, apply=False):
    raw = open(path, encoding="utf-8", errors="replace").read()
    lines = raw.split("\n")
    dead = {(i, o, n) for i, o, n in dead_pairs(path)}
    if not dead:
        return 0
    byline = {}
    for i, o, n in dead:
        byline.setdefault(i, []).append((o, n))
    changed = 0
    # ⚑ THE EDIT LOOP READ `lines[i]`, A SINGLE LINE — the ANALYSIS was converted to
    # `agda_lex.statements` and the WRITE was not.  `dead_pairs` returns `st.start`,
    # the statement's FIRST line, so a wrapped import
    #     open import Substrate.Foundation.Nat.SLesInjective
    #       renaming (_<_ to _<ℕ_)
    # has its `renaming` on the CONTINUATION: the search below found nothing, hit
    # `continue`, and the clause survived while the tool reported success.
    # MEASURED by the DRY audit: 77 statements disagree between the two reads.
    # This is the inverse-DRY class INSIDE the tool whose span defect I fixed hours
    # earlier — converting the half I was looking at and leaving the other half.
    spans = {st.start: st for st in agda_lex.statements(lines)
             if st.kind in ("import", "open")}
    for i, pairs in byline.items():
        st = spans.get(i)
        if st is None:
            continue
        block = "\n".join(lines[st.start:st.end])
        m = re.search(r"renaming\s*\(([^)]*)\)", block, re.S)
        if not m:
            continue
        kept = [c for c in m.group(1).split(";")
                if not any(c.split() == [o, "to", n] for o, n in pairs)]
        if kept:
            new_block = block[:m.start()] + "renaming (" + ";".join(kept) + ")" + block[m.end():]
        else:
            # whole clause dies; drop `using ()` too if it is empty, else keep it
            new_block = (block[:m.start()] + block[m.end():]).rstrip()
            new_block = re.sub(r"\busing\s*\(\s*\)\s*$", "", new_block).rstrip()
        # re-emit the (possibly shorter) statement over its whole span
        repl = [x for x in new_block.split("\n") if x.strip()]
        lines[st.start:st.end] = repl or [""]
        changed += len(pairs)
    if apply:
        import edit_snapshot
        # ⚑ `intent="apply"` IS HONEST HERE ONLY BECAUSE `main` NOW CHECKS THE CONTRACT AT
        # THE DECISION.  This call sits under `if apply:` — it cannot observe an unstated
        # intent, so re-deriving the verdict from argv here would be a check that always
        # passes.  Stating the intent says what is TRUE at this point (apply was chosen)
        # and leaves the actual contract to `ratchet.mutating_argv` at `main`, where the
        # choice happens.  It also un-blocks `_selftest`, which drives this path against a
        # TEMP FIXTURE with `--selftest` in argv and neither mutation flag.
        edit_snapshot.guard("drop_dead_renames", [path], intent="apply")
        open(path, "w", encoding="utf-8").write("\n".join(lines))
    return changed


# ── un-rename: the LIVE aliases ────────────────────────────────────────────
from agda_defs import def_index as _def_index


def unrename_verdict(path, mod, old, new):
    """('SAFE'|reason) for un-renaming `new`->`old` in `path`.

    THREE gates, in cost order.  Measured over the 185 live clauses that survive
    `drop_dead_renames`: 126 SAFE, 26 blocked by gate (2), 33 by gate (1),
    **0 by gate (3)** — recorded because the scope gate was the one I expected to
    dominate and it binds least.  Cheap checks first is not just performance: a
    verdict attributable to the simplest failing gate is the easiest to act on.
    """
    raw = open(path, encoding="utf-8", errors="replace").read()
    src = agda_lex.mask_comments(raw)
    lines = src.split("\n")
    imported = {IMPORT.match(l).group(1) for l in lines if IMPORT.match(l)}
    body = "\n".join("" if IMPORT.match(l) else l for l in lines)
    # (1) another provider of `old` is imported here -> un-renaming is ambiguous.
    #     The fix is upstream (rename_at_source on the OTHER provider), not here.
    if (set(_def_index().get(old, [])) - {mod}) & imported:
        return "COLLISION: another imported module provides this name"
    # (2) `old` already occurs FREE in the body -> the rewrite would merge two
    #     distinct references into one spelling.
    #     ⚑ A TELESCOPE BINDER IS NOT A USE.  Naively scanning the whole body
    #     counted `module Over (old : Set)` as an occurrence, so gate (2) always
    #     fired first and gate (3) COULD NOT BE REACHED — the capture check was
    #     unreachable code and the selftest is what exposed it (it asked for a
    #     capture verdict and got OCCUPIED).  Exclude the header lines of every
    #     module scope before asking.
    scopes = agda_lex.module_scopes(raw)
    hdr = set()
    for _n, _i, params, start, _end in scopes:
        if old in params:
            # the header runs from its `module` line to `start` (its body's first line)
            for j in range(max(0, start - 12), start):
                hdr.add(j)
    body2 = "\n".join("" if (i in hdr or IMPORT.match(l)) else l
                       for i, l in enumerate(lines))
    if WORD(old).search(body2):
        return "OCCUPIED: `old` already appears in the body"
    # (3) `old` is bound by an enclosing telescope AT a use site -> CAPTURE.
    #     (The Graded/Defs.agda witness: `_ℕ+_`->`_+_` inside `module Over (_+_ : …)`.)
    uses = [i + 1 for i, l in enumerate(lines)
            if WORD(new).search(l) and not IMPORT.match(l)]
    if any(agda_lex.binds_at(raw, old, u) for u in uses):
        return "CAPTURE: `old` is bound by a module telescope at a use site"
    return "SAFE"


def token_ledger(before, after, old, new, k):
    """Assert the ONLY change is k occurrences of `new` becoming `old`.

    ⚑ A SUBSTITUTION IS NOT A PERMUTATION, so `agda_imports`' Counter-equality
    assertion does not transfer and a line-conservation guard is BLIND here: the
    dangerous failure (capture) deletes nothing and changes no line count.  The
    invariant that does bind is on TOKENS:  S' = S - k*{new} + k*{old}, with no
    other token's count moving.  A greedy regex eating a longer name containing
    `new`, or the two-spelling substitution firing on an unintended occurrence,
    both break it.
    """
    import collections as _c
    tok = lambda t: _c.Counter(re.findall(r"[^\s(){}\[\];,]+", t))
    a, b = tok(before), tok(after)
    delta = {t: b[t] - a[t] for t in set(a) | set(b) if b[t] != a[t]}
    want = {new: -k, old: k} if old != new else {}
    return delta == want, delta


def _selftest():
    """Counted from len(cases)."""
    cases = []

    def check(name, got, want):
        cases.append((name, got == want, got, want))

    import tempfile

    def probe(text):
        with tempfile.NamedTemporaryFile("w", suffix=".agda", delete=False,
                                         encoding="utf-8") as fh:
            fh.write(text)
            p = fh.name
        try:
            return [(o, n) for _i, o, n in dead_pairs(p)]
        finally:
            os.unlink(p)

    check("dead: new name never used -> reported",
          probe("open import Substrate.M using () renaming (a to bA)\nf : Set\n"),
          [("a", "bA")])
    check("LIVE: new name used in the body -> NOT reported",
          probe("open import Substrate.M using () renaming (a to bA)\nf = bA\n"), [])
    check("a name used only on ANOTHER import line is still dead",
          probe("open import Substrate.M using () renaming (a to bA)\n"
                "open import Substrate.N using (bA)\nf : Set\n"),
          [("a", "bA")])
    check("multi-clause: only the dead one is reported",
          probe("open import Substrate.M renaming (a to bA; c to dC)\nf = dC\n"),
          [("a", "bA")])
    check("a use inside a COMMENT does not keep a clause alive",
          probe("open import Substrate.M using () renaming (a to bA)\n-- bA is nice\nf : Set\n"),
          [("a", "bA")])
    check("operator clause parses",
          probe("open import Substrate.M using () renaming (_+_ to _⊕_)\nf : Set\n"),
          [("_+_", "_⊕_")])
    check("non-Substrate import is out of scope",
          probe("open import Agda.Primitive using () renaming (a to bA)\nf : Set\n"), [])
    # ⚑ THE SPAN CASE.  A WRAPPED import puts `renaming` on a continuation line;
    # reading `lines[i]` alone found nothing and the clause survived silently.
    check("WRAPPED statement: renaming on a continuation line is seen",
          probe("open import Substrate.M\n  renaming (a to bA)\nf : Set\n"),
          [("a", "bA")])
    check("WRAPPED + live: a used continuation clause is NOT dead",
          probe("open import Substrate.M\n  renaming (a to bA)\nf = bA\n"), [])

    # ── the SECOND predicate: new == old ───────────────────────────────────
    # ⚑ The distinguishing case is `rename-to-self WITH THE NAME IN USE`: the
    # primary predicate clears it only when unused, so a test on an unused
    # self-rename would pass under BOTH rules and prove nothing.
    check("self-rename is dead even though the name IS USED "
          "(the primary predicate cannot see this)",
          probe("open import Substrate.M using () renaming (a to a)\nf = a\n"),
          [("a", "a")])
    check("self-rename, name unused — also dead (both rules agree)",
          probe("open import Substrate.M using () renaming (a to a)\nf : Set\n"),
          [("a", "a")])
    check("a GENUINE alias whose target is used is still NOT dead",
          probe("open import Substrate.M using () renaming (a to bA)\nf = bA\n"), [])
    check("operator self-rename",
          probe("open import Substrate.M using () renaming (_+F_ to _+F_)\nf = _+F_\n"),
          [("_+F_", "_+F_")])

    # ── rewrite(): the EDIT path, not just the analysis ────────────────────
    # ⚑ The suite tested `dead_pairs` only, so the edit loop's single-line read
    # survived the span fix untouched.  These drive `rewrite()` end-to-end.
    def edited(text):
        with tempfile.NamedTemporaryFile("w", suffix=".agda", delete=False,
                                         encoding="utf-8") as fh:
            fh.write(text); p2 = fh.name
        try:
            rewrite(p2, apply=True)
            return open(p2, encoding="utf-8").read()
        finally:
            os.unlink(p2)

    check("edit: WRAPPED statement's dead clause is actually REMOVED "
          "(lines[i] found nothing here and silently skipped)",
          "renaming" in edited("open import Substrate.M\n  renaming (a to bA)\nf : Set\n"),
          False)
    check("edit: single-line dead clause removed",
          "renaming" in edited("open import Substrate.M using () renaming (a to bA)\nf : Set\n"),
          False)
    check("edit: a LIVE clause is left alone",
          "renaming" in edited("open import Substrate.M using () renaming (a to bA)\nf = bA\n"),
          True)
    # ⚑ editing spans in a loop shifts later indices — two wrapped statements in
    # one file is the case that exposes it.
    two = edited("open import Substrate.M\n  renaming (a to bA)\n"
                 "open import Substrate.N\n  renaming (c to dC)\nf : Set\n")
    check("edit: TWO wrapped statements both cleaned (no index drift)",
          two.count("renaming"), 0)
    check("edit: two-statement edit keeps both imports",
          two.count("open import"), 2)

    # ── unrename_verdict: the three gates ──────────────────────────────────
    def verdict(text, mod, old, new):
        with tempfile.NamedTemporaryFile("w", suffix=".agda", delete=False,
                                         encoding="utf-8") as fh:
            fh.write(text); p2 = fh.name
        try:
            return unrename_verdict(p2, mod, old, new)
        finally:
            os.unlink(p2)

    check("verdict SAFE when the alias is live and nothing blocks",
          verdict("open import Substrate.M using () renaming (zz-uniq to qq)\n"
                  "f = qq\n", "Substrate.M", "zz-uniq", "qq"), "SAFE")
    check("verdict OCCUPIED when `old` already appears in the body",
          verdict("open import Substrate.M using () renaming (zz-uniq to qq)\n"
                  "f = qq\ng = zz-uniq\n", "Substrate.M", "zz-uniq", "qq"),
          "OCCUPIED: `old` already appears in the body")
    # ⚑ CAPTURE with NOTHING else blocking: `old` occurs ONLY as a telescope
    # binder, never free in the body, so gate (2) passes and only the scope
    # walk can refuse. This is the Graded/Defs.agda class, isolated.
    # ── verdict_census: the CORPUS question, not one clause ────────────────
    # ⚑ THESE EXIST BECAUSE THE PREDICATE WAS UNREACHABLE FROM A SHELL.
    # `unrename_verdict` was selftested against three fixtures and had one
    # caller, so the question every consumer actually asks -- how many clauses
    # are SAFE, and which are blocked by what -- could only be answered by
    # re-deriving it in a throwaway script.  A tested predicate with no command
    # is the `rewire_only` shape (1 def, 0 reachable calls) wearing a
    # predicate's clothes.
    with tempfile.TemporaryDirectory() as d:
        p3 = os.path.join(d, "Live.agda")
        with open(p3, "w", encoding="utf-8") as fh:
            fh.write("open import Substrate.M using () renaming (zz-uniq to qq)\n"
                     "f = qq\n")
        got = verdict_census([p3])
        check("census finds the live clause", sum(len(v) for v in got.values()), 1)
        check("census classes it SAFE", list(got), ["SAFE"])
        check("census keys by path::old->new",
              got["SAFE"][0].endswith("::zz-uniq->qq"), True)

        # ⚑ A WRAPPED statement is one clause, not zero: the span authority is
        # what makes that true, and reading it wrongly is how the first run of
        # this census reported `0 across 3457 files` -- a clean-looking answer
        # produced by looking at nothing.
        p4 = os.path.join(d, "Wrapped.agda")
        with open(p4, "w", encoding="utf-8") as fh:
            fh.write("open import Substrate.M\n"
                     "  using ()\n"
                     "  renaming (zz-uniq to qq)\n"
                     "f = qq\n")
        check("census spans a WRAPPED renaming statement",
              sum(len(v) for v in verdict_census([p4]).values()), 1)

        # a self-rename is drop_dead's own class, never an un-rename candidate
        p5 = os.path.join(d, "Self.agda")
        with open(p5, "w", encoding="utf-8") as fh:
            fh.write("open import Substrate.M using () renaming (qq to qq)\nf = qq\n")
        check("census skips a self-rename",
              sum(len(v) for v in verdict_census([p5]).values()), 0)

    check("verdict CAPTURE when `old` is bound by a telescope at the use site",
          verdict("open import Substrate.M using () renaming (zz-uniq to qq)\n"
                  "module Over (zz-uniq : Set)\n"
                  "  where\n"
                  "  f = qq\n", "Substrate.M", "zz-uniq", "qq"),
          "CAPTURE: `old` is bound by a module telescope at a use site")

    # ── token_ledger ───────────────────────────────────────────────────────
    ok1, _ = token_ledger("f = qq\ng = qq", "f = zz\ng = zz", "zz", "qq", 2)
    check("ledger: exactly k swaps -> holds", ok1, True)
    ok2, _ = token_ledger("f = qq", "f = zz\nh = zz", "zz", "qq", 1)
    check("ledger: an EXTRA token appearing -> refused", ok2, False)
    ok3, _ = token_ledger("f = qqx", "f = zzx", "zz", "qq", 1)
    check("ledger: a greedy rewrite inside a LONGER name -> refused", ok3, False)

    ok = sum(1 for _, g, _, _ in cases if g)
    for name, good, got, want in cases:
        if not good:
            print(f"  FAIL {name}\n       got  {got!r}\n       want {want!r}")
    print(f"drop_dead_renames selftest: {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def main(argv):
    if "--selftest" in argv:
        return _selftest()
    # ⚑⚑⚑ THE MUTATION INTENT IS CHECKED HERE, AT THE DECISION, not at the write.
    # `apply = "--apply" in argv` below IS the choice, and it used to be made silently:
    # a bare run printed `(dry run — pass --apply)` and returned 0 having never consulted
    # the contract.  `edit_snapshot.guard` enforces the same rule but sits at `:143`
    # inside `if apply:` — reached only once apply is already TRUE — so the unstated case,
    # the entire population the ratchet measures, could never reach it.
    #
    # ⚑⚑ MEASURED, NOT REASONED: with `SUBSTRATE_EXPLICIT_MUTATION=1` — the setting whose
    # whole purpose is to REFUSE an unstated intent — this tool still printed its dry-run
    # summary and exited 0.  A ratchet whose census cannot see the population is a
    # resolution, so the fix had to move the check to where the decision happens.
    # `pycodemod --guarded guard` is the census: 24 of 61 sites sit under an `if`.
    import sys as _sys
    _sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import ratchet as _r
    rc = _r.mutating_argv(argv, "drop_dead_renames")
    if rc is not None:
        return rc
    apply = "--apply" in argv
    targets = [a for a in argv[1:] if not a.startswith("-")]
    # ⚑ NO TARGET MEANS THE WHOLE TREE, not nothing.  A bare run enumerated an
    # EMPTY file list and printed `0 dead clause(s) across 0 file(s)` -- which
    # reads as "the tree is clean" and is actually "I looked at nothing".  A
    # report indistinguishable from success is the guard-degraded-to-measuring-
    # nothing shape (plan section 52), here in the tool's own default path.
    if not targets:
        targets = [os.path.join(ROOT, "agda")]
    files = []
    for t in targets:
        files.extend(agda_lex.agda_files(t) if os.path.isdir(t) else [t])

    if "--verdicts" in argv:
        return _verdict_census(files)

    total = 0
    for f in files:
        n = rewrite(f, apply)
        if n:
            total += n
            print(f"{n:4d} {'dropped' if apply else 'would drop'}  {f}")
    print(f"{total} dead renaming clause(s) across {len(files)} file(s)"
          f"{'' if apply else '  (dry run — pass --apply)'}")
    return 0


def verdict_census(files=None):
    """{verdict-class: [(path, mod, old, new)]} over every LIVE renaming clause.

    ⚑ BUILT BECAUSE `unrename_verdict` WAS UNREACHABLE FROM A SHELL.  The
    predicate was written, selftested against three hand-made fixtures, and had
    exactly one caller -- so the corpus question every consumer actually asks
    ("how many clauses can be un-renamed, and which are blocked by what") could
    only be answered by re-deriving it in a throwaway script.  That is the
    `rewire_only` shape (1 def, 0 reachable calls) in a predicate rather than a
    command, and it is why the A2/A3 figures in the worklist are quoted from a
    measurement nobody could repeat.

    Keyed `path::old->new` so a class is a set of KEYS, not a count -- the same
    reason every ratchet keys its census rather than tallying it."""
    if files is None:
        files = agda_lex.agda_files(os.path.join(ROOT, "agda"))
    out = {}
    for path in files:
        try:
            raw = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        # ⚑ `statements()` TAKES LINES, NOT A STRING.  Passing the raw text made
        # it iterate CHARACTERS, so the census reported `0 live clauses across
        # 3457 files` -- a clean-looking answer produced by looking at nothing.
        # Read the authority's signature rather than inferring it from a call
        # site; that is the third time this arc an authority's contract was
        # guessed (after telescope_groups' VERBATIM text and group_statements'
        # callable opener).
        for st in agda_lex.statements(agda_lex.mask_comments(raw).split("\n")):
            if st.kind != "import" or "renaming" not in st.text:
                continue
            mod = st.module          # the authority already parsed it
            if not mod or not mod.startswith("Substrate"):
                continue
            for old, new in _rename_pairs(st.text):
                if old == new:
                    continue          # a self-rename is drop_dead's own class
                v = unrename_verdict(path, mod, old, new)
                cls = v.split(":", 1)[0]
                key = "%s::%s->%s" % (os.path.relpath(path, ROOT), old, new)
                out.setdefault(cls, []).append(key)
    return out


def _verdict_census(files):
    got = verdict_census(files)
    total = sum(len(v) for v in got.values())
    for cls in sorted(got):
        rows = sorted(got[cls])
        print("%-10s %4d   %s" % (cls, len(rows), rows[0] if rows else ""))
        for r in rows[1:4]:
            print("%-10s        %s" % ("", r))
        if len(rows) > 4:
            print("%-10s        ... and %d more" % ("", len(rows) - 4))
    print("%d live renaming clause(s) across %d file(s)" % (total, len(files)))
    return 0


# selftest-tenant: sandbox
# ⚑ ⟡tenant-mandatory — reaches a store via `scope_fix→scope_store→store`. SANDBOX: this tool
# rewrites Agda source, so a suite reading the live corpus to rehearse a rewrite is the
# wrong-tenant failure at its worst. Surfaced 2026-08-24 when a deferred `import store` two
# hops away was hoisted — the chain THROUGH a lazy import is truncated, not just its module.
if __name__ == "__main__":
    sys.exit(main(sys.argv))
