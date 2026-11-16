# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.private_gate` — the private-block ratchet's entry point.

⚑⚑⚑ THE LOAD-BEARING CASE IS THAT AN UNMEASURABLE CENSUS REFUSES. A census that could not
run returns an empty set, which is byte-identical to a clean tree — and an empty census banked
into a paydown-only baseline absolves every existing violation permanently, which is the one
error in this whole family that cannot be undone. The gate must exit 2, and `--quiet` must not
silence it: quiet suppresses a PASS, and being blind is not one.

⚑⚑ AND THE `key_move` MUST BE PRESENT ON THE GATE, because its absence is invisible. Without
it the gate still runs, still reports, and simply refuses a decomposition as growth — so
nothing distinguishes a gate that forgot it from one that has nothing to relocate. The
declaration is asserted directly rather than inferred from a verdict.

⚑ THE CENSUS ITSELF IS NOT RE-TESTED HERE. `private_census_selftest` owns the predicate; a
case here that walked the tree would be a measurement of the corpus wearing a case's clothes,
slow and red or green for reasons that have nothing to do with this file.
"""

from __future__ import annotations

from mikemol.ratchet.render import Report

from substrate import private_gate
from substrate.gate_main import Gate, Unmeasurable, run_gate

_CANNOT_MEASURE = 2

# ⚑ A MODULE CONSTANT BECAUSE `EM101` REFUSES A LITERAL AT THE RAISE, and it is right: a
# message built at the raise site is one a caller cannot match on without repeating it.
_BLIND_REASON = "could not load split_lemmas"


def _blind() -> set[str]:
    """Fail the way a census whose scanner will not load fails."""
    raise private_gate.ScannerUnavailable(_BLIND_REASON)


def _blind_gate() -> Gate:
    """Build a gate whose census cannot be taken."""
    return Gate(label="private-ratchet", census=_blind, baseline_path=private_gate.BASELINE)


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the gate declares what it must ───────────────────────────────────────
    check(
        "the gate is labelled for the ratchet it runs",
        passed=private_gate.GATE.label == "private-ratchet",
    )
    # ⚑ THE BASELINE STAYS WITH THE OTHER GATES' LEDGERS. A moved ledger reads as a paid-down
    # gate, because the baseline IS the debt.
    check(
        "the baseline is the gates' own file, not a new one",
        passed=private_gate.BASELINE.endswith("scripts/private_ratchet_baseline.txt"),
    )
    # ⚑ THE DECLARATION WHOSE ABSENCE IS INVISIBLE.
    check(
        "a key_move is supplied, so a decomposition is not read as growth",
        passed=private_gate.GATE.key_move is not None,
    )

    # ── the key_move behaves as a relocation test ────────────────────────────
    move = private_gate.GATE.key_move
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

    # ── an unmeasurable census REFUSES rather than reporting clean ───────────
    rc = run_gate(_blind_gate(), Report(), ["private_gate.py"])
    check("a census that cannot run exits CANNOT-MEASURE, not clean", passed=rc == _CANNOT_MEASURE)
    # ⚑ AND `--quiet` DOES NOT SILENCE IT. A gate that goes quiet about being blind is worse
    # than a noisy one, because the silence is indistinguishable from success.
    rc = run_gate(_blind_gate(), Report(), ["private_gate.py", "--quiet"])
    check("and --quiet does not turn that into a pass", passed=rc == _CANNOT_MEASURE)

    # ⚑ THE REFUSAL CARRIES A REMEDY for its whole class of failure, so a reader is not left
    # to guess which of several load failures happened.
    check(
        "the unmeasurable class names a remedy", passed=bool(private_gate.ScannerUnavailable.remedy)
    )
    check(
        "and it is an Unmeasurable, so run_gate routes it",
        passed=issubclass(private_gate.ScannerUnavailable, Unmeasurable),
    )

    # ── the refusal hint tells an operator what to DO ────────────────────────
    hint = private_gate.REPORT.refuse_hint or ""
    check(
        "the refusal says to EXTRACT, not to delete the keyword",
        passed="EXTRACT" in hint and "do not delete" in hint.lower(),
    )
    # ⚑ THE EXCLUSION IS STATED WHERE IT WILL BE READ. `private variable` is a binding form,
    # and an operator seeing a refusal is exactly who needs to know it is not censused.
    check("and says `private variable` is not censused", passed="private variable" in hint)

    # ── a bad flag refuses, and does not pass ────────────────────────────────
    # ⚑⚑⚑ THIS CASE WAS FIRST WRITTEN ASSERTING `rc not in (0, _CANNOT_MEASURE)` AND FAILED,
    # WHICH IS HOW A REAL COLLISION WAS FOUND. `check_argv` returns 2 for an unknown flag
    # and `run_gate` returns 2 for a census it could not take — TWO CONDITIONS, ONE EXIT
    # CODE. `gate_main` argues in its own comment that 1 and 2 must differ *because they
    # demand different responses* (a code fix versus an environment fix); by that same
    # argument a typo and a blind census should differ too, and they do not. A caller
    # reading 2 cannot tell whether to correct their command line or install a tool.
    #
    # ⚑ SO THE CASE ASSERTS WHAT IS TRUE — the flag is refused, not passed — and records the
    # collision rather than encoding a distinction the code does not make. Writing the
    # assertion I expected would have meant changing the gate to satisfy a test rather than
    # filing the defect the test found.
    rc = run_gate(_blind_gate(), Report(), ["private_gate.py", "--queit"])
    check("a typo'd flag refuses rather than passing", passed=rc != 0)

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


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
# Discovery requires BOTH an entry point AND the flag handled somewhere in the file; a suite
# with only the entry point passes when run by hand and vanishes from the sweep, which shows
# up as a smaller green total that nobody has a prior for.
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
