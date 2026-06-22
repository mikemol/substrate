#!/usr/bin/env python3
"""jea_check — the shared self-test harness for jea/ strictify + probe scripts.

The test-fixtures home the consolidation map (Π) had been waiting on: at RFS ≥3 the
byte-identical `check`/`results`/TALLY harness — copied across jea_strictify_{gcalc,
kirchhoff,rotation} and jea_parity_species_probe — folds to one place. `Checks` collects
(name, PASS/FAIL) results and renders the TALLY/FAILURES summary; the bug-fix (and any
future format change) now happens once.

Usage (keeps the old `check`/`results` names so call sites are unchanged):

    from jea_check import Checks
    _checks = Checks(); check = _checks.check; results = _checks.results
    ...
    check("some property", lhs == rhs)
    ...
    _checks.tally("exact checks")            # top-level scripts
    # or, inside main(): return 0 if _checks.tally("...") else 1
"""


class Checks:
    def __init__(self):
        self.results = []

    def check(self, name, cond):
        ok = bool(cond)
        self.results.append((name, ok))
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        return ok

    def tally(self, label="exact checks"):
        npass = sum(ok for _, ok in self.results)
        print(f"\n=== TALLY: {npass}/{len(self.results)} {label} pass ===")
        fails = [nm for nm, ok in self.results if not ok]
        if fails:
            print("FAILURES:", fails)
        return npass == len(self.results)
