#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.ledger_converge.plan` — every bucket, and idempotence.

⚑ EVERY ENTRY LANDS IN EXACTLY ONE BUCKET, and the case says so: a writer whose buckets could
overlap or leak would report a total that is not the population. The fixture holds one entry per
outcome — rewritten, field added, already converged, no roster row, unspellable.

⚑⚑ IDEMPOTENCE IS THE LOAD-BEARING CASE. Planning over the planned text must change nothing; a
converger that rewrote on every run would never read as done, and one that drifted would rewrite
checks nobody asked it to touch.

⚑ AND COMMENTS SURVIVE. The fixture leads with a comment, because `bib_edit`'s masked-locate is
only sound while the mask preserves length — a comment AFTER the edited field would pass against
a corrupting mask.
"""

from __future__ import annotations

import sys

from substrate import bib_parse, ledger_converge

FIXTURE = """% the ledger's adjudication record — must survive every write

@misc{A-rewrite,
  section  = {finding},
  claim    = {needs its check rewritten},
  check    = {item:A-rewrite}
}

@misc{B-add,
  section  = {finding},
  claim    = {carries no check at all}
}

@misc{C-done,
  section  = {finding},
  claim    = {already converged},
  check    = {standing}
}

@misc{D-no-roster,
  section  = {plan},
  claim    = {a plan entry, no witness},
  check    = {traces:x#y}
}

@misc{E-refused,
  section  = {finding},
  claim    = {its witness cannot be spelled},
  check    = {item:E-refused}
}
"""

SPELLED = {"A-rewrite": "selftest:true", "B-add": "unwitnessed", "C-done": "standing"}
REFUSED = {"E-refused": "E-refused: kind x has no check spelling"}


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    done = ledger_converge.plan(FIXTURE, SPELLED, REFUSED)
    if not isinstance(done, ledger_converge.Plan):
        return [("the fixture plans without a refusal", False)]
    check = {key: fields.get("check", "") for key, fields in bib_parse.parse(done.text).items()}
    buckets = [done.rewritten, done.added, done.unchanged, done.no_roster, done.refused]
    again = ledger_converge.plan(done.text, SPELLED, REFUSED)
    return [
        ("the fixture plans without a refusal", True),
        ("a stale check is rewritten", done.rewritten == ["A-rewrite"]),
        ("the rewritten check is the roster spelling", check["A-rewrite"] == "selftest:true"),
        ("a missing check is ADDED", done.added == ["B-add"]),
        ("the added check is the roster spelling", check["B-add"] == "unwitnessed"),
        ("a converged check is left alone", done.unchanged == ["C-done"]),
        ("a key with no roster row keeps its check", check["D-no-roster"] == "traces:x#y"),
        ("an unspellable witness keeps its check", check["E-refused"] == "item:E-refused"),
        ("every entry lands in exactly one bucket", sum(map(len, buckets)) == len(check)),
        ("the leading comment survives", done.text.startswith("% the ledger's adjudication")),
        (
            "planning the planned text changes nothing",
            isinstance(again, ledger_converge.Plan)
            and again.text == done.text
            and not again.rewritten
            and not again.added,
        ),
    ]


def selftest() -> int:
    """Run every case, reporting failures by name, and return an exit code."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"ledger-converge selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 1)
