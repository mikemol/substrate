#!/usr/bin/env python3
"""check_sumtype_ratchet.py — duplicate type-declarations are DEBT; ratchet them down.

The SIBLING of check_carrier_locality.py. That gate governs canonical OPERATORS
over globally-UNIQUE carriers; this one governs the DUPLICATION of the carriers
themselves — the `data`/`record` names it must SKIP because they are declared in
≥2 files (ambiguous, `several modules each declare their own Word`). Every such
duplicate declaration is a fork-in-waiting (the scattered `data V₄` copies that
Ⓒ.v4 later unified onto one home are the cautionary tale).

CENSUS (materialized from the tree, not a frozen list): the SET of keys
`<name>::<relpath>` for every declaration of a name declared in ≥2 files. This
set is DEBT — it may only be PAID DOWN (consolidate duplicates onto one home,
import/re-export elsewhere), never grown: a NEW copy of an already-duplicated
name, or a name becoming newly-duplicated, is REFUSED. A paydown auto-lowers the
baseline. (RATCHET semantics + I/O are the shared scripts/ratchet.py, mirroring
set1_ratchet_cores.py; this is the 3rd such ratchet.)

The existing duplicates are GRANDFATHERED at the baseline (legacy debt frozen,
like Set₁ and the carrier-locality ALLOW set) — some are genuine forks to merge,
some legitimately-parallel per-instance types (per-Zₙ `Gen`/`Canonical`); the
ratchet does not adjudicate, it only forbids GROWTH and rewards consolidation.

Blocking gate. Exit 0 = clean, 1 = a new duplicate appeared.
Usage: check_sumtype_ratchet.py [--quiet]
"""
import os
import sys

import ratchet
from check_carrier_locality import ROOT, DECL, strip_comments, agda_files

BASELINE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "sumtype_ratchet_baseline.txt")


def census():
    """The duplicate-declaration set: {name::relpath} for names declared in ≥2 files."""
    decls = {}                                    # name -> set of files
    for path in agda_files():
        with open(path, encoding="utf-8") as fh:
            src = strip_comments(fh.read())
        for line in src.splitlines():
            m = DECL.match(line)
            if m:
                decls.setdefault(m.group(1), set()).add(path)
    dup = set()
    for name, files in decls.items():
        if len(files) >= 2:                       # a duplicated type name = debt
            for path in files:
                dup.add(f"{name}::{os.path.relpath(path, ROOT)}")
    return dup


def main():
    quiet = "--quiet" in sys.argv
    return ratchet.set_ratchet(
        census(), BASELINE, "sumtype-ratchet", quiet,
        noun="duplicate type-declaration(s)",
        refuse_hint="Reuse the existing declaration (import / re-export it), or "
                    "consolidate the copies onto one home — do NOT add a parallel copy.")


if __name__ == "__main__":
    sys.exit(main())
