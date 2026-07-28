#!/usr/bin/env python3
"""check_public_ratchet.py — EVERY `open … public` re-export is DEBT; ratchet them down.

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
`using (…)`), never grown. A NEW re-export of any kind is REFUSED; a paydown
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

# The unit is the STATEMENT, not the line: Agda accepts import directives in any order and
# across continuation lines, so `public` may sit on line 1 with `using (…)` on line 2, or after
# multi-line arguments. A line-anchored scan misses both shapes.
OPEN = re.compile(r"^([ \t]*)open\s+(?:import\s+)?(\S+)")
PUBLIC = re.compile(r"(?<![\w.-])public(?![\w.-])")


def census():
    """The re-export set: {relpath::opened} for EVERY `open … public`, narrowed or not.

    ⛔ POLICY (user, 2026-07-27): a policy-driven ban on ALL re-exports. The old census counted
    only WHOLESALE re-exports, so a narrowed `open X using (…) public` was not "exempt debt" —
    it was INVISIBLE debt, absent from the baseline entirely. Reading the policy off what the
    instrument happened to count is the stale-proxy error this ratchet exists to prevent: the
    predicate must match the POLICY, not the gate's convenience. Widening it therefore RAISES
    the baseline before it falls, which is the ratchet working, not a regression.

    `open import Agda.Primitive … public` is excluded — the catalog does not index compiler
    builtins, so there is no owner to bind at, and `Foundation/Level.agda` re-exporting `Level`
    IS the insulation boundary working. Everything else is debt, including `open <Rec> … public`
    (a record's fields / an applied module), which pays down by REDOING THE APPLICATION at the
    owner rather than by deleting a keyword.
    """
    out = set()
    for path in agda_files():
        with open(path, encoding="utf-8") as fh:
            lines = strip_comments(fh.read()).splitlines()
        rel = os.path.relpath(path, ROOT)
        i = 0
        while i < len(lines):
            m = OPEN.match(lines[i])
            if not m:
                i += 1
                continue
            ind, stmt, j = len(m.group(1)), [lines[i]], i + 1
            while j < len(lines) and lines[j].strip() and \
                    (len(lines[j]) - len(lines[j].lstrip())) > ind:
                stmt.append(lines[j])
                j += 1
            opened = m.group(2)
            if PUBLIC.search("\n".join(stmt)) and not opened.startswith("Agda.Primitive"):
                out.add(f"{rel}::{opened}")
            i = j
    return out


def main():
    quiet = "--quiet" in sys.argv
    return ratchet.set_ratchet(
        census(), BASELINE, "public-ratchet", quiet,
        noun="`open … public` re-export(s)",
        refuse_hint="A module re-exports ONLY what it DEFINES. Bind the names at their "
                    "OWNER (a direct, NON-public `open`) in each consumer, or narrow "
                    "this re-export with `using (…)`. A wholesale re-export copies the "
                    "whole upstream API into every consumer's core.")


if __name__ == "__main__":
    sys.exit(main())
