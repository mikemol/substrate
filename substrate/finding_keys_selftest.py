# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.finding_keys` — the ordinal-collision reader.

⚑ THE LOAD-BEARING CASE IS THE UNSLUGGED KEY. A bare `family-O12` holds its ordinal
exactly as a slugged key does, and a reader that skipped it would report a TAKEN ordinal as
FREE — handing a filer the collision the tool exists to prevent. The live ledger contains
such keys, so this is not a hypothetical shape.

⚑⚑ AND THE CENSUS OVER-REPORTS BY CONSTRUCTION, which a case states rather than leaving to
a reader. Some collisions are DELIBERATE: a slug ending `-reframe` or `-rekey`, or a pair
naming opposite verdicts, is a SUPERSESSION where sharing the ordinal is the point. A
paydown that erased them would destroy the ledger's own correction record, so the reader
reports collisions and does not call them defects.

⚑ THE FIXTURE CARRIES KEYS AND NOTHING ELSE. The reader matches a quoted key followed by a
colon, so a witness body is decoration — and a fixture reproducing one would be asserting
against a shape the reader never inspects.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from substrate import finding_keys

_KEYS = (
    "gate-F1-first-finding",
    "gate-F1-second-finding",
    "gate-F2-only-one",
    "gate-O12",
    "sql-F1-different-family",
    "swarm-F5-reframe",
    "swarm-F5-original",
)

COLLIDED_IN_FIXTURE = 2
SLUGS_ON_COLLIDED = 2


def _fixture() -> str:
    """Render a ledger-shaped roster holding exactly `_KEYS`."""
    lines = ["WITNESSES = {"]
    lines += [f'    "{k}": lambda: _standing("x"),' for k in _KEYS]
    lines.append("}")
    return "\n".join(lines) + "\n"


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    with tempfile.TemporaryDirectory() as tmp:
        led = Path(tmp) / "findings.py"
        led.write_text(_fixture(), encoding="utf-8")

        rows = finding_keys.ordinals(led)
        collided = finding_keys.collisions(led)
        gate_f = finding_keys.taken("gate", "F", led)
        gate_o = finding_keys.taken("gate", "O", led)
        sql_f = finding_keys.taken("sql", "F", led)
        text = finding_keys.render(led)

    # ── the ordinal index ────────────────────────────────────────────────────
    labels = {o.label for o in rows}
    check("every ordinal is indexed", passed="gate-F1" in labels and "gate-F2" in labels)
    check("a different family is kept apart", passed="sql-F1" in labels)

    # ⚑ THE UNSLUGGED KEY — reporting it FREE would hand a filer a collision.
    check("an unslugged key still holds its ordinal", passed="gate-O12" in labels)
    check("and reads as taken in its own series", passed=gate_o == {12})

    # ── the taken set ────────────────────────────────────────────────────────
    check("the taken set covers the family's ordinals", passed=gate_f == {1, 2})
    check("and excludes another family's", passed=sql_f == {1})

    # ── collisions ───────────────────────────────────────────────────────────
    check("a shared ordinal is reported", passed=len(collided) == COLLIDED_IN_FIXTURE)
    both = next((o for o in collided if o.label == "gate-F1"), None)
    check("and names every slug filed under it",
          passed=both is not None and len(both.slugs) == SLUGS_ON_COLLIDED)
    check("a single-occupant ordinal is NOT a collision",
          passed=all(o.label != "gate-F2" for o in collided))

    # ⚑ THE OVER-REPORT: a supersession pair collides deliberately, and the reader
    # reports it as a collision without calling it a defect. Pinned so a later paydown
    # cannot quietly erase the ledger's correction record.
    check("a deliberate supersession still reports as a collision",
          passed=any(o.label == "swarm-F5" for o in collided))

    # ── the render states its own scope ──────────────────────────────────────
    check("the render reports the collided count", passed="2 collided ordinal(s)" in text)
    check("and refuses to suggest a next number",
          passed="NO NEXT NUMBER IS SUGGESTED" in text)
    check("and says the full key stays unique",
          passed="nothing was overwritten" in text)

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


if __name__ == "__main__":
    raise SystemExit(0 if selftest() else 1)
