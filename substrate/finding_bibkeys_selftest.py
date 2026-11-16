#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pin the ledger-key reader, and pin that UNREADABLE never smooths into EMPTY.

⚑⚑⚑ THE THIRD OUTCOME IS THE POINT OF THIS SUITE. A caller handed `set()` for a failed read
reports every witness as unpaired and renders a census claiming total drift — produced by a
tool that did not run, and indistinguishable from a real finding once printed. So the cases
assert `None` explicitly, and assert the OTHER direction too: a directory with no bibs is
genuinely empty, because there was nothing to fail on.

⚑⚑ THE LIVE CASE READS THE REAL LEDGERS, because the property that matters most — that the
key set is non-trivial and matches what the owning tool reports — cannot be exhibited by a
fixture I write. A reader agreeing with my fixture and disagreeing with `bibstruct` has not
been verified.

⚑ AND THE NON-KEY ROWS ARE CASED. `bibstruct --entries` leads with a denominator line and can
emit a warning line; taking token zero blindly interns both as findings, which would inflate
the bib side of every pairing census by two.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import finding_bibkeys

ROOT = Path(__file__).resolve().parent.parent
LEDGERS = ROOT / ".claude" / "agents"

# ⚑ A FLOOR, DELIBERATELY WELL BELOW THE LIVE COUNT (gate-G40). The property under test is that
#   the read is NON-TRIVIAL, not that it equals today's total — a case pinned to the current
#   figure goes red on the next filing and teaches the next reader to loosen it.
NONTRIVIAL = 100

Case = tuple[str, bool]


def _empty_cases() -> list[Case]:
    """Return the cases pinning that no-bibs is EMPTY while a failed read is UNREADABLE."""
    with tempfile.TemporaryDirectory() as where:
        bare = Path(where)
        keys, bibs = finding_bibkeys.bib_keys(bare)
        missing_keys, missing_bibs = finding_bibkeys.bib_keys(bare / "not-a-directory")
    return [
        # ⚑ A DIRECTORY WITH NO BIBS IS GENUINELY EMPTY — nothing ran, so nothing failed.
        ("a directory with no bibs yields an empty key set", keys == set()),
        ("...and reports no bibs found", bibs == []),
        ("...and is NOT the unreadable outcome", keys is not None),
        # ⚑ AN ABSENT DIRECTORY IS THE SAME KIND OF EMPTY, not a crash.
        ("an absent directory yields empty rather than raising", missing_keys == set()),
        ("...with no bibs listed", missing_bibs == []),
    ]


def _listing_cases() -> list[Case]:
    """Return the cases pinning that the bib listing is stable and suffix-scoped."""
    with tempfile.TemporaryDirectory() as where:
        home = Path(where)
        for name in ("zeta.bib", "alpha.bib", "notes.md", "script.py"):
            (home / name).write_text("", encoding="utf-8")
        found = finding_bibkeys.ledger_bibs(home)
    names = [p.name for p in found]
    return [
        ("only .bib files are listed", names == ["alpha.bib", "zeta.bib"]),
        # ⚑ SORTED, BECAUSE A DUPLICATE KEY IS DECIDED BY READ ORDER. An unstable listing makes
        #   which declaration wins depend on the filesystem rather than on anything visible.
        ("...and the order is sorted rather than filesystem-dependent", names == sorted(names)),
        ("a non-bib sibling is not picked up", "notes.md" not in names),
    ]


def _live_cases() -> list[Case]:
    """Read the REAL ledgers, since a fixture cannot exhibit the property that matters.

    ⚑ THE DENOMINATOR AND WARNING ROWS ARE THE HAZARD HERE. `--entries` leads with a count line
    and may emit a `⚑` warning; both would intern as keys under a blind token-zero read and
    inflate the bib side of the pairing census.
    """
    if not LEDGERS.is_dir():
        return [("the ledger directory is present to read", False)]
    keys, bibs = finding_bibkeys.bib_keys(LEDGERS)
    if keys is None:
        return [("⚑ the live ledgers read — an UNREADABLE result here is a real finding", False)]
    return [
        ("the live ledgers are readable", True),
        ("...over several bib files", len(bibs) > 1),
        ("...yielding a non-trivial key population", len(keys) > NONTRIVIAL),
        # ⚑ THE NON-KEY ROWS MUST NOT HAVE BEEN INTERNED.
        ("no denominator row was read as a key",
         not any(k.startswith("entries:") for k in keys)),
        ("no warning row was read as a key", not any(k.startswith("⚑") for k in keys)),
        # ⚑ A KNOWN KEY IS PRESENT, so the read is not merely non-empty but CORRECT.
        ("a key filed this session is present",
         "gate-G57-the-findings-drain-has-a-first-unit" in keys),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = _empty_cases() + _listing_cases() + _live_cases()
    bad = [label for label, holds in cases if not holds]
    print(f"finding_bibkeys: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
