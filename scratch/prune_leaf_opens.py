#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Drop the inherited prelude APPLICATIONS a split leaf does not use.

`split_param_module.py` copies the parent's whole body prelude into every leaf,
so a one-line leaf still carries `open F.Over CR` + `open Core.Over CR d f-lo` +
`open Expand.Over CR d f-lo` even when it cites none of them. A module
application COPIES, so each of those is ~a full telescope of elaboration
(⟡cap-residue, ~+10MB apiece) — and it compounds at the CONSUMER, which now
applies several leaves that each re-apply the same parents. That is what made
Div's 3-4-leaf consumers (ModZero, BezoutFold/Step, DLogHom, …) cross the cap
again after the tip was retired.

Deciding "does this leaf use any name from that parent?" statically needs the
parent's full export closure (FromCommRing re-exports all of Graded). The
TYPECHECKER already knows: drop a candidate pair, recompile, keep the drop iff
it still compiles. Empirical, and it cannot be wrong about scope.

USAGE: prune_leaf_opens.py <leaf.agda>...            (dry run)
       prune_leaf_opens.py <leaf.agda>... --apply
"""
import os, re, subprocess, sys

# ⚑⚑ `_snapshot_once` WAS DELETED HERE (Ⓐ49 ⟡split-8-unprotected).  Its rationale is
# KEPT AS RESIDUE — it was RIGHT about the danger, wrong only about PLACEMENT:
#
#   "This tool rewrites files it read — the shape that made 33 files unrecoverable
#    (Coxeter/Core.agda 76 lines -> 3).  The write is inside a loop, so a per-file
#    `guard` would arm only the first file AND shell out to `git stash create` on
#    every iteration; arming once per run is both correct and cheap."
#
# "Arm once per run" is now structural: the snapshot rides the single entry-point intent
# statement.  Leaving this as dead code would make `--unbound-snapshot` read FALSE-RED,
# since it keys on a `guard` call site being PRESENT, not on it being REACHABLE.


AGDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "agda")
MB = os.environ.get("PRUNE_MB", "768")


def check(path):
    rel = os.path.relpath(path, AGDA)
    r = subprocess.run(
        [os.path.join(AGDA, "..", "scripts", "membudget"), "run", MB, "prune",
         "--", "agda", "--safe", "--without-K", "-i.", rel],
        cwd=AGDA, capture_output=True, text=True)
    return r.returncode == 0


def candidates(lines):
    """(open_ix, import_ix, module) for each inherited prelude application."""
    out = []
    for i, l in enumerate(lines):
        m = re.match(r"^\s+open\s+(\S+)\.Over\b", l)
        if not m:
            continue
        mod = m.group(1)
        # the matching import: `import <mod>` or `import <full> as <mod>`
        ii = next((j for j, x in enumerate(lines)
                   if re.match(r"^import\s+" + re.escape(mod) + r"\s*$", x)
                   or re.match(r"^import\s+\S+\s+as\s+" + re.escape(mod) + r"\s*$", x)), None)
        out.append((i, ii, mod))
    return out


def prune(path, apply):
    orig = open(path, encoding="utf-8").read()
    lines = orig.split("\n")
    if not check(path):
        return "SKIP (does not compile as-is)"
    dropped = []
    for _, _, mod in candidates(lines):
        cur = open(path, encoding="utf-8").read().split("\n")
        drop = {i for i, l in enumerate(cur)
                if re.match(r"^\s+open\s+" + re.escape(mod) + r"\.Over\b", l)
                or re.match(r"^import\s+" + re.escape(mod) + r"\s*$", l)
                or re.match(r"^import\s+\S+\s+as\s+" + re.escape(mod) + r"\s*$", l)}
        if not drop:
            continue
        # ⚑ THE WRITE-SITE `_snapshot_once(path)` IS GONE, NOT MOVED (Ⓐ49).  It sat
        # BELOW `if not drop: continue`, so a run that found nothing droppable armed
        # nothing — while still having written and restored this file on the dry path.
        # The snapshot is taken at the entry intent statement, both modes.
        open(path, "w", encoding="utf-8").write(
            "\n".join(l for i, l in enumerate(cur) if i not in drop))
        if check(path):
            dropped.append(mod)
        else:
            open(path, "w", encoding="utf-8").write("\n".join(cur))
    if not apply:
        open(path, "w", encoding="utf-8").write(orig)
    return ", ".join(dropped) or "nothing droppable"


if __name__ == "__main__":
    # ⚑⚑ THE GUARD MOVED HERE FROM THE FIRST PENDING WRITE (Ⓐ44 ⟡move-guards-to-entry).
    # `_snapshot_once` sits inside `prune`'s loop under `if not drop: continue`, so a run
    # that found nothing droppable never armed it — and this tool WRITES THE FILE EVEN IN
    # DRY RUN (it writes, re-`check`s, then restores at the end), which is exactly the
    # case a write-sited guard cannot express and a caller cannot infer.  At entry the
    # caller states intent per invocation, before any dispatch.
    import edit_snapshot as _es
    _paths = [a for a in sys.argv[1:] if not a.startswith("--")]
    # ⚑⚑⚑ SNAPSHOT BOUND TO THE INTENT STATEMENT (Ⓐ49 ⟡split-8-unprotected), with
    # `paths=` so the UNTRACKED half is reached: `snapshot()` covers tracked content
    # whole-worktree, but `_copy_untracked(paths)` is the only mechanism that copies an
    # untracked file aside, and untracked files are the population most likely to need it.
    _es.require_at_entry("prune_leaf_opens", paths=_paths)
    apply = "--apply" in sys.argv
    # ⚑⚑⚑ AND THIS TOOL IS THE EXCEPTION THAT THE BINDING ALONE GETS WRONG.  It WRITES
    # THE FILE EVEN IN DRY RUN — it writes, re-`check`s, then restores at the end — so a
    # STATED `--dry-run` still mutates the tree, and `require_at_entry` deliberately
    # takes NO snapshot on a stated dry-run ("a stated dry-run writes nothing to
    # snapshot").  For every other tool that is correct; here it would leave the one mode
    # that is advertised as safe as the only unprotected one.
    # ⚑ SO THE DRY PATH ARMS THE SNAPSHOT EXPLICITLY, stating `intent="apply"` because
    # that is the truth about what this process does to the filesystem — the flag
    # describes the OPERATOR'S request, this states the TOOL'S behaviour, and where they
    # disagree the filesystem is what needs recovering.  A restore-at-the-end is a
    # promise, not a guarantee: a crash between the write and the restore leaves the
    # damage, which is exactly the snapshot's case.
    if not apply:
        # ⚑⚑⚑ THE ONE SANCTIONED DIVERGENCE IN THE TREE (⟡intent-contextvar).  The
        # ambient intent here is `dry-run` — `require_at_entry` above bound it from the
        # operator's flag — and this states `apply`, because that is the truth about what
        # this process does to the filesystem.  Under write-once those two CANNOT both be
        # written, and that refusal is correct for every other tool; here the divergence
        # is real, so it is spelled as a registered override that runs in a COPIED
        # context.  The outer `dry-run` binding is untouched.
        #
        # ⚑ IT IS DELIBERATELY EXPENSIVE TO SPELL — a callable, a reason, and a
        # registration in `edit_snapshot.SANCTIONED_OVERRIDES`.  An override as cheap as
        # a keyword argument is the defect with more steps: the next writer reaches for
        # it the moment a refusal is inconvenient.
        _es.INTENT.override(
            "apply",
            reason="writes the file even on a stated --dry-run (writes, re-checks, "
                   "restores at the end); a crash between the write and the restore "
                   "leaves the damage, which is precisely the snapshot's case",
            label="prune_leaf_opens (dry-run writes-then-restores)",
        ).run(lambda: _es.guard(
            "prune_leaf_opens (dry-run writes-then-restores)",
            paths=_paths, intent="apply"))
    # ⚑ THE OPERAND FILTER EXCLUDED ONE FLAG BY NAME, AND THE ENTRY GUARD EXPOSED IT.
    # `a != "--apply"` let EVERY other flag through as a path: `--dry-run` reached
    # `prune()` and died `FileNotFoundError: '--dry-run'`.  It was latent before only
    # because nothing made a caller type a second flag — the contract now does, so a
    # name-keyed filter becomes a crash on the very invocation the contract requires.
    # Filtering by SHAPE (`--` prefix) rather than by one spelling is the same
    # census-keyed-on-one-spelling fix applied to an argv.
    for p in [a for a in sys.argv[1:] if not a.startswith("--")]:
        print(f"{os.path.basename(p)}: {prune(p, apply)}", flush=True)
    if not apply:
        print("(dry run — files restored)")
