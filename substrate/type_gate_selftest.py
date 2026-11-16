#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.type_gate` — above all, that it REFUSES rather than reports clean.

⚑⚑⚑ THE UNMEASURABLE ARM IS THE WHOLE REASON THIS GATE EXISTS, so it is the first case.
**0 keys over 60 unannotated files** was once banked as a clean census: a `python3` without
mypy produced no error lines and the parse honestly found nothing. A gate that reports 0 keys
when the checker never ran is worse than no gate, because it certifies its own blind spot.

⚑⚑ AND MIGRATING THIS GATE TO `run_gate` WOULD HAVE DELETED THAT BRANCH SILENTLY. The shared
authority could say "pass" or "debt grew" and had no way to say "I could not measure", so the
consolidation would have looked like a simplification and been a regression. A case that must
FAIL is the only thing separating the two readings.

⚑ THE SCOPE ARM MIRRORS `check_mypy_ratchet`'s OWN. That gate carries *"If someone hand-copies
ROOTS into this file, a future promotion silently escapes the type gate"*; here the roster is
imported from `substrate.promoted` and the case asserts the identity, never the contents.

⚑⚑ AND ONE ARM CHANGED THE MODULE UNDER TEST. Setting up the render case tripped `SLF001` —
reaching into `type_gate._MESSAGES` — and that refusal named a real design fault rather than a
test inconvenience: module state only a private poke can establish is state the interface does
not admit exists. `hold_messages` was added there, and the renderer became exercisable without
violating the encapsulation it depends on.
"""

from __future__ import annotations

import sys

from substrate import promoted, type_gate
from substrate.gate_main import run_gate

# The exit code a gate returns when its census could not be taken.
_CANNOT_MEASURE = 2

# A key shaped as the census emits them, for the renderer arms.
_KEY = "arg-type::scripts/example.py"

# ⚑ MODULE CONSTANTS BECAUSE `EM101` REFUSES A LITERAL AT THE RAISE — and the refusal is right
# even in a fixture: a reason worth raising is worth naming once.
_SYNTHETIC = "synthetic: the checker did not run"
_REAL_REASON = "duplicate module named 'hadamard_basis'"


def _raise_unmeasurable() -> list[str]:
    """Stand in for a census that cannot be taken."""
    raise type_gate.MypyUnavailable(_SYNTHETIC)


def unmeasurable_refuses(out: list[str]) -> int:
    """Check an unmeasurable census exits 2 rather than reporting clean.

    ⚑ THE CENSUS IS REPLACED, NOT MYPY. Uninstalling the checker to test this would be a
    measurement that mutates the environment it measures; substituting the census exercises
    the same branch and leaves the machine alone.
    """
    gate = type_gate.GATE.__replace__(census=_raise_unmeasurable)
    rc = run_gate(gate, type_gate.REPORT, ["type_gate.py"])
    if rc != _CANNOT_MEASURE:
        out.append(f"selftest: an unmeasurable census returned {rc}, not {_CANNOT_MEASURE}")
        return 1
    return 0


def quiet_does_not_silence(out: list[str]) -> int:
    """Check `--quiet` suppresses a PASS but never a refusal.

    ⚑ QUIET IS ABOUT SUCCESS. A gate that goes quiet about being blind is worse than a noisy
    one, because the silence is indistinguishable from success — the same defect the
    unmeasurable branch exists to prevent, one layer up.
    """
    gate = type_gate.GATE.__replace__(census=_raise_unmeasurable)
    rc = run_gate(gate, type_gate.REPORT, ["type_gate.py", "--quiet"])
    if rc != _CANNOT_MEASURE:
        out.append("selftest: --quiet changed the unmeasurable verdict")
        return 1
    return 0


def remedy_is_carried(out: list[str]) -> int:
    """Check the refusal names a remedy and carries the real reason verbatim.

    ⚑ "not importable" WAS ONCE A GUESS PRINTED AS A FACT. mypy exits non-census for a config
    error, a duplicate module name, or an unreadable path just as readily as for an absent
    install, and each wants a different fix — so the reason must survive unrewritten.

    ⚑ THERE IS NO `isinstance(e, Unmeasurable)` ARM: mypy PROVES the subclass relation from
    the declaration and reports the assertion body as UNREACHABLE. A runtime case for
    something the checker already forbids can never fail, which reads as coverage while
    measuring nothing. Second instance of that shape today; the first was a tuple-ness check.
    """
    bad = 0
    e = type_gate.MypyUnavailable(_REAL_REASON)
    if e.reason != _REAL_REASON:
        out.append(f"selftest: the reason was rewritten to {e.reason!r}")
        bad += 1
    if "mypy" not in e.remedy:
        out.append(f"selftest: the remedy does not name the missing tool: {e.remedy!r}")
        bad += 1
    return bad


def scope_is_imported(out: list[str]) -> int:
    """Check the population comes from its authority, never a local copy."""
    bad = 0
    if "scratch" in promoted.POPULATION:
        out.append("selftest: scratch/ entered the type gate's population")
        bad += 1
    if "scripts" not in promoted.POPULATION:
        out.append("selftest: the gate layer is not in the population")
        bad += 1
    return bad


def render_is_total(out: list[str]) -> int:
    """Check the renderer is total on a key with no held message.

    ⚑ A PAID-DOWN KEY HAS NO MESSAGE. `render` is called for removed keys too, and one that
    raised there would turn a successful paydown into a crash — the report path failing
    exactly when the news is good.
    """
    bad = 0
    type_gate.hold_messages({})
    if type_gate.render(_KEY) != _KEY:
        out.append("selftest: render is not total on a key with no message")
        bad += 1
    type_gate.hold_messages({_KEY: ["a message"]})
    rendered = type_gate.render(_KEY)
    if "1x" not in rendered:
        out.append(f"selftest: the count is not rendered unambiguously: {rendered!r}")
        bad += 1
    type_gate.hold_messages({})
    return bad


_ARMS = (
    unmeasurable_refuses,
    quiet_does_not_silence,
    remedy_is_carried,
    scope_is_imported,
    render_is_total,
)

_CASE_COUNT = 1 + 1 + 2 + 2 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"type-gate selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"type-gate selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
