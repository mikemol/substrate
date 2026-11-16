# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.public_gate` — the re-export ratchet's entry point.

⚑⚑⚑ THE ABSENT `Unmeasurable` BRANCH IS THE THING TO PIN, NOT TO COPY. `private_gate` loads two
scanners out of `scratch/` and must distinguish *no violations* from *the scanner is missing*; this
gate walks the tree itself, so an empty census IS an empty tree and there is no third state. The
asymmetry is deliberate and stated in the module's own docstring — a case demanding a refusal here
would be asserting a branch the design says must not exist.

⚑⚑ SO WHAT REPLACES IT IS THE CLAIM THAT MAKES THE ABSENCE SAFE: the census must be the tree-walking
one. If it ever became a loader, an empty result would stop meaning an empty tree and banking it
into a paydown-only baseline would absolve every existing violation permanently — the one error in
this family that cannot be undone.

⚑⚑ AND THE `key_move` MUST BE PRESENT, because its absence is invisible. Without it the gate still
runs, still reports, and simply refuses a decomposition as growth — so nothing distinguishes a gate
that forgot it from one with nothing to relocate. The declaration is asserted directly rather than
inferred from a verdict.

⚑ THE CENSUS ITSELF IS NOT RE-TESTED HERE. `public_census` owns the predicate; a case walking the
tree would be a measurement of the corpus wearing a case's clothes — slow, and red or green for
reasons that have nothing to do with this file. That boundary is `private_gate_selftest`'s and is
kept rather than re-derived.
"""

from __future__ import annotations

import sys

from mikemol.ratchet.render import Report

from substrate import public_census, public_gate
from substrate.gate_main import Gate, Unmeasurable, run_gate

_CANNOT_MEASURE = 2

# ⚑ A MODULE CONSTANT BECAUSE `EM101` REFUSES A LITERAL AT THE RAISE, and it is right: a message
# built at the raise site is one a caller cannot match on without repeating it.
_BLIND_REASON = "the census could not be taken"


class _ScannerGone(Unmeasurable):
    """Stand in for a census that cannot be taken, so `run_gate`'s routing is exercised."""

    remedy = "this census cannot fail today — the class exists to pin the lattice"


def _blind() -> set[str]:
    """Fail the way a census that could not be taken fails."""
    raise _ScannerGone(_BLIND_REASON)


def _blind_gate() -> Gate:
    """Build a gate whose census cannot be taken."""
    return Gate(label="public-ratchet", census=_blind, baseline_path=public_gate.BASELINE)


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the gate declares what it must ───────────────────────────────────────
    check(
        "the gate is labelled for the ratchet it runs",
        passed=public_gate.GATE.label == "public-ratchet",
    )
    # ⚑ THE BASELINE STAYS WITH THE OTHER GATES' LEDGERS. A moved ledger reads as a paid-down
    # gate, because the baseline IS the debt — the module's own docstring says so.
    check(
        "the baseline is the gates' own file, not a new one",
        passed=public_gate.BASELINE.endswith("scripts/public_ratchet_baseline.txt"),
    )
    # ⚑ THE DECLARATION WHOSE ABSENCE IS INVISIBLE.
    check(
        "a key_move is supplied, so a decomposition is not read as growth",
        passed=public_gate.GATE.key_move is not None,
    )

    # ── the key_move behaves as a relocation test ────────────────────────────
    move = public_gate.GATE.key_move
    if move is None:
        check("key_move present to exercise", passed=False)
        return out
    check(
        "the same definition at a new path shares a move token",
        passed=move("a/B.agda::helper") == move("a/B/Leaf.agda::helper"),
    )
    # ⚑ AND A DIFFERENT DEFINITION DOES NOT — the direction that must never absolve.
    check(
        "a different definition does not",
        passed=move("a/B.agda::helper") != move("a/B.agda::other"),
    )

    # ── the census is the tree-walking one, which is what makes the absent third state safe ──
    # ⚑⚑⚑ THIS IS THE ARM THE MISSING `Unmeasurable` BRANCH REQUIRES. The module argues that an
    # empty census means an empty tree BECAUSE it walks the tree rather than loading a scanner. If
    # that delegate ever changed, the premise would fail silently and an empty result would bank
    # as clean — so the delegation is asserted rather than assumed.
    check(
        "the gate's census delegates to the tree-walking reader",
        passed=public_gate.census() == public_census.census(),
    )

    # ── an unmeasurable census would still REFUSE if one ever arose ──────────
    # ⚑⚑ THE MACHINERY IS SHARED, so this asserts `run_gate`'s routing rather than a branch of
    # this gate. It matters here because the absent third state is a claim about THIS census, not
    # a claim that the lattice below it has been removed — a future census that can fail must
    # still refuse, and nothing else in this file would say so.
    rc = run_gate(_blind_gate(), Report(), ["public_gate.py"])
    check("a census that cannot run exits CANNOT-MEASURE, not clean", passed=rc == _CANNOT_MEASURE)
    # ⚑ AND `--quiet` DOES NOT SILENCE IT. A gate that goes quiet about being blind is worse than
    # a noisy one, because the silence is indistinguishable from success.
    rc = run_gate(_blind_gate(), Report(), ["public_gate.py", "--quiet"])
    check("and --quiet does not turn that into a pass", passed=rc == _CANNOT_MEASURE)

    # ── the refusal hint tells an operator what to DO ────────────────────────
    hint = public_gate.REPORT.refuse_hint or ""
    check(
        "the refusal says to IMPORT WHAT IS USED, not to narrow the re-export",
        passed="IMPORT WHAT IS USED" in hint,
    )
    # ⚑⚑ THE NON-REMEDY IS NAMED WHERE IT WILL BE READ. Narrowing with `using` hides names while
    # the module stays applied and elaborated, so an operator seeing a refusal is exactly who
    # needs to know it does not count as a paydown.
    check("and says `using` is not a paydown", passed="using" in hint and "not a paydown" in hint)
    # ⚑ AND IT NAMES THE MODE THAT ENUMERATES. A refusal reporting a count with no way to list
    # its members leaves a reader to re-derive what the gate already knew.
    check("and names the mode that enumerates the census", passed="--list" in hint)

    # ── a bad flag refuses, and does not pass ────────────────────────────────
    # ⚑ THE COLLISION `private_gate_selftest` RECORDED HOLDS HERE TOO: `check_argv` returns 2 for
    # an unknown flag and `run_gate` returns 2 for a census it could not take, so a caller reading
    # 2 cannot tell whether to fix a command line or an environment. The case asserts what is TRUE
    # — the flag is refused — rather than encoding a distinction the code does not make.
    rc = run_gate(_blind_gate(), Report(), ["public_gate.py", "--queit"])
    check("a typo'd flag refuses rather than passing", passed=rc != 0)

    return out


def selftest() -> bool:
    """Report whether every case passed, printing the failures."""
    cases = _cases()
    ok = sum(1 for _label, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"public_gate selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(0 if selftest() else 1)
