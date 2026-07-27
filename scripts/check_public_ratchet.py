#!/usr/bin/env python3
"""check_public_ratchet.py — WHOLESALE `open … public` re-exports are DEBT; ratchet them down.

A module re-exports ONLY what it DEFINES. A wholesale `open X public` (no
using/hiding/renaming) re-materializes X's ENTIRE accumulated API into this
module's `.agdai` — and into every consumer's, transitively, because **Agda
module application COPIES, it does not reference**. That is the mechanism behind
the elaboration-memory blowups ⟡cap-ratchet gates: `Mod` was being used to
retrieve `*P-comm`, `neg`, `anti-diag-sum` — none of which it defines — because a
wholesale re-export made it a CONDUIT for the whole Graded tier.

MEASURED (⟡public-policy, 2026-07-26): restructuring so each part opens its
dependency DIRECTLY and NON-publicly took Mod 175→116 MB, Quotient 145→113,
Div 130→117. The chain accumulation that made sharding counter-productive was
never intrinsic — it was the `public` inheritance.

CENSUS (materialized from the tree, not a frozen list): the SET of keys
`<relpath>::<opened>` for every wholesale `open … public` — i.e. an `open` with
`public` and NO `using`/`hiding`/`renaming` narrowing. This set is DEBT: it may
only be PAID DOWN (bind at the source and drop the re-export, or narrow it with
`using (…)`), never grown. A NEW wholesale re-export is REFUSED; a paydown
auto-lowers the baseline. (RATCHET semantics + I/O are the shared scripts/ratchet.py,
the 4th such ratchet after set1 / carrier-locality / sumtype.)

The existing wholesale re-exports are GRANDFATHERED at the baseline (legacy debt
frozen) — some are legitimate barrels/tips (`Graded.agda` IS the public API for
39 importers), most are conduits. The ratchet does not adjudicate which; it only
forbids GROWTH and rewards paydown.

Blocking gate. Exit 0 = clean, 1 = a new wholesale re-export appeared.
Usage: check_public_ratchet.py [--quiet]
"""
import os
import re
import sys

import ratchet
from check_carrier_locality import ROOT, strip_comments, agda_files

BASELINE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "public_ratchet_baseline.txt")

# `open X public`, `open import X public`, `open X args public` — the opened name is
# the first token after `open [import]`; `public` must appear and no narrowing may.
OPEN = re.compile(r"^\s*open\s+(?:import\s+)?(\S+)")


def census():
    """The wholesale-re-export set: {relpath::opened} for every un-narrowed `open … public`."""
    out = set()
    for path in agda_files():
        with open(path, encoding="utf-8") as fh:
            src = strip_comments(fh.read())
        rel = os.path.relpath(path, ROOT)
        for line in src.splitlines():
            if " public" not in line and not line.rstrip().endswith("public"):
                continue
            m = OPEN.match(line)
            if not m:
                continue
            if re.search(r"\b(using|hiding|renaming)\b", line):
                continue          # narrowed — this is the PAID-DOWN form
            out.add(f"{rel}::{m.group(1)}")
    return out


def main():
    quiet = "--quiet" in sys.argv
    return ratchet.set_ratchet(
        census(), BASELINE, "public-ratchet", quiet,
        noun="wholesale `open … public` re-export(s)",
        refuse_hint="A module re-exports ONLY what it DEFINES. Bind the names at their "
                    "OWNER (a direct, NON-public `open`) in each consumer, or narrow "
                    "this re-export with `using (…)`. A wholesale re-export copies the "
                    "whole upstream API into every consumer's core.")


if __name__ == "__main__":
    sys.exit(main())
