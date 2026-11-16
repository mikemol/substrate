#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""decl_shape_tag.py — make a colliding type's SHAPE visible at its declaration.

Names are vacuous; for a genuinely-ambiguous name (declared in >1 module with
DIFFERENT shapes) the reader can't tell which node a `data/record Name` line is
without inference. This appends a visible tag comment to that line:

    record Section : Set where      -- ⟦shape:053a2000 lift,drop,drop-lift⟧

(a line comment, compile-safe). --check verifies every such decl is tagged;
--fix appends missing tags. Tags match scripts/sppf_node_index.py's hashes.
"""

# ⚑ `hashlib` AND `strip` WENT WITH THE COMPUTATION.  This file hashed and stripped
# because it walked the tree itself; it now reads `_agdatext.shape_decls`, so both
# imports were stranded — the residue a consolidation leaves and the next reader
# mistakes for a dependency.
import os, re, sys, collections

_SNAPPED = []


def _snapshot_once(path):
    """Arm edit_snapshot on the FIRST write of a run; a no-op thereafter.

    ⚑ This tool rewrites files it read — the shape that made 33 files
    unrecoverable (Coxeter/Core.agda 76 lines -> 3).  The write is inside a loop,
    so a per-file `guard` would arm only the first file AND shell out to `git
    stash create` on every iteration; arming once per run is both correct and
    cheap.  Recovery is per-file and MANUAL by design — edit_snapshot never
    restores anything itself.
    """
    if _SNAPPED:
        return
    _SNAPPED.append(True)
    try:
        import edit_snapshot

        # ⚑ `intent="apply"` IS ENTAILED BY THE BRANCH: the sole caller is guarded
        # on `if changed`, and `changed` is set only inside `if fix`, so this line
        # is reached only on a stated `--fix` immediately above an unconditional
        # write.
        # ⚑⚑ AND `require_at_entry` AT THE TOP WOULD BREAK PRE-COMMIT.  The hook
        # invokes this tool BARE (`.githooks/pre-commit:255`, phase A, BLOCKING) to
        # run its CHECK branch; an armed entry gate sees neither `--apply` nor
        # `--dry-run` and exits 2, aborting every commit.
        # ⚑⚑⚑ AND THIS TOOL IS THE ONE WHERE THE ENTRY FORM CANNOT BE RECOVERED BY
        # MOVING THE CALL.  Its mutation flag is spelled `--fix`, and its bare argv
        # is BYTE-IDENTICAL between the hook's read and an operator's run — so
        # "what did the caller ask for" is genuinely unanswerable from argv here,
        # not merely unasked. The fix is to make the tool spell the mutation pair
        # (`--apply`/`--dry-run` beside `--fix`) and move the hook to the stated
        # read; that is a change to a BLOCKING gate's invocation, which is the
        # operator's call and not a paydown agent's. Recorded, not guessed at.
        edit_snapshot.guard("decl_shape_tag", [path], intent="apply")
    except Exception as e:
        print(f"   \u26a0 snapshot unavailable ({e}) \u2014 recover via git if needed")


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agda", "Substrate"))
# ⚑⚑⚑ THIS WAS THE **THIRD** COPY OF THE SHAPE COMPUTATION, and the census that
# found it was run AFTER unifying the other two — I had concluded "two gates
# disagree" from the two I was shown.  `pycodemod --attr sha1 scripts/` reports the
# real population; the frontier of what I had been told was not the edge of the
# duplication.  Three tools, one relation, three private copies, each with its own
# `ALLOW = {⊤,⊥,⊤₁}`:
#
#   check_import_shape.py  ENFORCES (fails on a bare colliding import)
#   sppf_node_index.py     PUBLISHES (the index the failure message cites)
#   decl_shape_tag.py      TAGS      (writes the shape at the declaration)
#
# ⚑ AND THIS ONE DIVERGED A FOURTH WAY: it keyed its collision test on the FILE
# PATH while the other two keyed on the MODULE NAME.  Those differ for a
# parameterized header, so the three could disagree on a name none of the three
# `ALLOW` sets covered.
#
# ⚑ THE `--fix` ARM WRITES AGDA SOURCE, so a wrong verdict here EDITS THE TREE.
# Of the three, this is the one where a private copy of a shared predicate is not
# a reporting defect but a write hazard.
import _agdatext

# ⚑ `with_path=True` IS WHAT LETS THE LAST COPY GO.  The tagger appends to a LINE
# IN A FILE, so it needs the path the other two callers do not; taking that as an
# extra column beats re-walking and re-hashing, which is exactly the act that made
# this the third copy.
_decls = _agdatext.shape_decls(ROOT, with_path=True)
genuine = _agdatext.genuine_ambiguity(_decls, _agdatext.LEVEL_POLY_DUPS)
info = collections.defaultdict(list)  # name -> [(path, kind, hash, heads)]
for _name, _rows in _decls.items():
    for _mod, _kind, _desc, _sh, _p, _heads in _rows:
        info[_name].append((_p, _kind, _sh, _heads))

fix = "--fix" in sys.argv
missing = []
for name in genuine:
    for p, kind, sh, heads in info[name]:
        tag = f"⟦shape:{sh}" + (f" {heads}" if heads else "") + "⟧"
        lines = open(p, encoding="utf-8").read().splitlines()
        dl = re.compile(r"^(data|record)\s+" + re.escape(name) + r"(\s|$|\()")
        changed = False
        for k, line in enumerate(lines):
            if dl.match(line):
                base = re.sub(r"\s*--\s*⟦shape:[^⟧]*⟧\s*$", "", line).rstrip()
                want = base + f"      -- {tag}"
                if line.rstrip() == want:
                    break  # correct tag already present
                if fix:
                    lines[k] = want
                    changed = True
                else:
                    missing.append((name, os.path.relpath(p, ROOT)))
                break
        if changed:
            _snapshot_once(p)
            open(p, "w", encoding="utf-8").write("\n".join(lines) + "\n")

if fix:
    print(f"decl-shape-tag: tagged genuinely-ambiguous declarations ({len(genuine)} names).")
else:
    print(f"decl-shape-tag: {len(missing)} untagged genuinely-ambiguous declarations.")
    for n, p in sorted(missing):
        print(f"    {n:28s} {p}")
    sys.exit(1 if missing else 0)
