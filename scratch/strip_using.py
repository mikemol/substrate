# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol


import os as _o, sys as _s
_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from agda_imports import _span_end   # THE statement-span authority (agda_lex-backed); never re-derive
#!/usr/bin/env python3
"""Strip `using (…)` filters from `Substrate.*` imports of a chosen module.

⚠ THIS TOOL PAYS DOWN A METRIC, NOT THE DEBT.  Read this before using it.

The aim is to MINIMISE THE INFORMATION EACH FILE IMPORTS, and the information
each file holds.  One lemma per file; a consumer that needs a lemma imports the
file where that lemma is the ONLY thing.  An import must never pull a file
holding more than the import requires.  Filters, qualifiers and barrels are THE
ANTIPATTERN — a `using` list is a way of *appearing* to narrow while still
dragging the whole module in.

So deleting a filter and leaving a bare import of a fat module makes things
WORSE on the axis that matters: the same information is still imported and still
elaborated, and scope is now WIDER than before.  Only the ban-key count falls.
That is metric-gaming.  It also feeds the cap: a parameterised module imported
is APPLIED and ELABORATED, so importing 40 defs to use 1 is exactly the
elaboration cost the `Error 251` kills are made of.

THE FIX IS ALWAYS TO SPLIT UPSTREAM.  The pressure a filter records belongs
upstream, at the module that holds too much; the filter is the symptom.

⚠ DO NOT re-derive the "split only when the names COLLIDE" rule.  It is a
convenient fiction that keeps getting written back into this file and into the
guides, and it inverts the criterion: collision is one SYMPTOM that forces a
filter to exist, never the reason to split.  A module with zero collisions and
forty definitions still over-imports by forty when a consumer needs one.
Globally-unique names do not make a fat import cheap — they only make it quiet.

LEGITIMATE USE: as an intermediate step INSIDE a split, where the upstream is
being decomposed in the same pass and the bare import is immediately narrowed to
the owning leaf (see `narrow_leaf_imports.py`).  Never as a standalone paydown.

Statements carrying `renaming` / `hiding` / `as` are LEFT ALONE: those are a
different debt with a different repair (rename at source), and silently
dropping a rename target breaks every use site.

PERMUTATION-GUARDED: the multiset of imported MODULES must be identical before
and after — this pass may only remove filters, never an import.
"""
import re, sys, os
import agda_lex   # THE statement-span authority; never re-derive

# ⚑⚑ `_snapshot_once` WAS DELETED HERE (Ⓐ49 ⟡split-8-unprotected).  Its rationale is
# KEPT AS RESIDUE, because it was RIGHT about the danger and only wrong about PLACEMENT:
#
#   "This tool rewrites files it read — the shape that made 33 files unrecoverable
#    (Coxeter/Core.agda 76 lines -> 3).  The write is inside a loop, so a per-file
#    `guard` would arm only the first file AND shell out to `git stash create` on
#    every iteration; arming once per run is both correct and cheap."
#
# "Arm once per run" is now structural rather than sentinel-enforced: the snapshot rides
# the single entry-point intent statement, which happens exactly once per run.
# ⚑ AND LEAVING IT AS DEAD CODE WOULD MAKE THE CENSUS READ FALSE-RED — `--unbound-
# snapshot` keys on a `guard` CALL SITE being PRESENT, not on it being REACHABLE.


# ⚑ THIS MODULE SHADOWED `agda_lex.statements` WITH A COLUMN-0 COPY.  Its `IMP`
# was `^(open\s+import|import)` — no `\s*` — so every INDENTED import (inside
# `module M where`, `private`, or a `where open import …`) was INVISIBLE.
# MEASURED by the DRY audit: it disagreed with the authority on **26 of 2941
# files** (`Algebra/Q/Properties/CanonicalBezout.agda` missed 3 imports at :84-88;
# `Algebra/N-to-F2-Parity.agda` missed 2).  The direction is false-negative — it
# never stripped them — but the module's own PERMUTATION GUARD was computed with
# the same broken parser, so **the guard could not detect a loss it could not
# see**.  A guard that shares its subject's blind spot is not a guard.
#
# It already imported `_span_end` for continuations while keeping its own head
# regex one line above: the inverse-DRY shape (adopt the authority for one half,
# re-derive the other) that hid `rewire_to_leaves`' broken import regex for a
# whole arc.
def statements(lines):
    """(start, end_exclusive, module) per import statement — THE authority."""
    return [(st.start, st.end, st.module)
            for st in agda_lex.statements(lines)
            if st.kind in ("import", "open") and st.module]


def strip(path, prefix, apply=True):
    L = open(path).read().split("\n")
    before = sorted(m for _, _, m in statements(L))
    out, changed = list(L), 0
    for s, e, mod in reversed(statements(L)):
        if not mod.startswith(prefix):
            continue
        txt = " ".join(x.strip() for x in L[s:e])
        if re.search(r"\b(renaming|hiding|public)\b", txt) or re.search(r"\bas\s+\S+", txt):
            continue
        new = re.sub(r"\s*\busing\s*\([^)]*\)", "", txt).rstrip()
        if new == txt.rstrip():
            continue
        out[s:e] = [new]
        changed += 1
    if not changed:
        return 0, "no filter to strip"
    # PERMUTATION GUARD — filters may go, imports may not.
    after = sorted(m for _, _, m in statements(out))
    if before != after:
        return 0, f"REFUSING: import set changed ({len(before)}→{len(after)})"
    # The permutation guard above runs in BOTH modes: a dry run that skipped it
    # would report a count the apply pass might then refuse — the preview must
    # answer the same question the write does.
    if apply:
        # ⚑ THE WRITE-SITE `_snapshot_once(path)` IS GONE, NOT MOVED (Ⓐ49).  It sat under
        # `if apply:` — a guard BEHIND the decision it gates, so the unstated case (the
        # whole population the contract measures) could never reach it.  The snapshot is
        # taken at the entry intent statement, which is also why this run no longer
        # snapshots TWICE (measured: two SHAs printed for one invocation before this).
        open(path, "w").write("\n".join(out))
    return changed, ""


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pref = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--module=")), None)
    # ⚑⚑ INTENT AT ENTRY (Ⓐ44 ⟡move-guards-to-entry).  `_snapshot_once` sits inside
    # `strip()` under `if apply`, so it is reached only on a run that is already writing
    # — it can never refuse the bare invocation, which is the invocation this tool's own
    # comment below records as having been the dangerous one.
    # ⚑⚑⚑ AND IT MOVED ABOVE THE USAGE BAIL (Ⓐ49 ⟡split-8-unprotected).  The bail below
    # used to run FIRST, so `strip_using.py` with no arguments printed usage and exited 2
    # having never asked for intent — the guard was one dispatch short of entry and the
    # census could not see it, because `--unbound-snapshot` classifies by SOURCE POSITION
    # and the guard was inside `__main__` either way.  MEASURED: a bare invocation
    # printed `None` + usage instead of the mutation refusal.
    # ⚑ THE USAGE BAIL IS NOT A READ-PATH EXEMPTION.  Under this contract a tool that CAN
    # mutate demands the statement at EVERY invocation, including one that would only
    # have printed usage — otherwise the tool's author has decided once which paths are
    # exempt and every caller inherits it silently.
    import edit_snapshot as _es
    _es.require_at_entry("strip_using", paths=args)
    if not args or not pref:
        print(__doc__)
        print("usage: strip_using.py --module=<Substrate.Prefix> <file.agda> ...")
        sys.exit(2)
    # ⚑ THIS TOOL WROTE ON EVERY INVOCATION, WITH NO WAY TO LOOK FIRST — and its own
    # docstring opens "⚠ THIS TOOL PAYS DOWN A METRIC, NOT THE DEBT."  It is
    # HUMAN-INVOKED (not called by split_pipeline, does not declare stage_warning),
    # which by this repo's measured convention is exactly the class that gates on
    # `--apply`: a DRIVER-called stage errs apply-by-default so a silent no-op cannot
    # leave a split half-finished, a hand-run tool errs preview-by-default so a bare
    # invocation cannot rewrite the tree.  `prune_imports` cost an unintended 12-line
    # deletion by having this backwards; this one had no flag at all.
    apply = "--apply" in sys.argv
    tot = 0
    for p in args:
        n, msg = strip(p, pref, apply=apply)
        tot += n
        if msg and "REFUS" in msg:
            print(f"  {msg}  {p}")
    verb = "stripped" if apply else "WOULD strip"
    print(f"{verb} {tot} `using` filter(s) across {len(args)} file(s)"
          + ("" if apply else "   (dry run — pass --apply to execute)"))
