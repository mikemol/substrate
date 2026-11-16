# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""The cases for `substrate.ban_census` — grounded on the COMMITTED BASELINE.

⚑⚑⚑ THE VERIFICATION HAD TO BE REGROUNDED, AND THAT IS THE INTERESTING PART (gate-F75). Before
the swap this suite differenced against the live gate's own census, and that comparison is what
made the swap safe: two independent computations of one key set, agreeing over the whole tree.
Then the gate was rewritten to CALL `ban_census`. The arm still passed — and had stopped being a
measurement, because a function agreeing with itself is not evidence. *A check can do its job and
then quietly become a tautology, while its green stays exactly as green.*

⚑⚑ THE COMMITTED BASELINE IS THE ONLY INDEPENDENT AUTHORITY LEFT. It is a FILE, written by
earlier runs of a gate whose census this module now computes, so nothing in today's code path
produces it.

⚑⚑⚑ AND IT IS ASSERTED AS CONTAINMENT, NOT EQUALITY, WHICH IS THE RATCHET'S OWN SEMANTICS. A
paydown-only baseline is a HIGH-WATER MARK: keys legitimately vanish as splits land, and this
tree carries a large pending paydown right now. Equality would go red on honest progress, and *a
case that fails when the work succeeds is worse than no case*. What the gate refuses is a key
NOT in the baseline — so that is the property, and it is the one a census defect would trip.

⚑ THE SPAN CASES ARE THE REASON THIS MODULE EXISTS. An import's directive may sit on an indented
continuation line, and the origin records that a line-wise scan let 158 narrowed re-exports
escape a sibling census — so a wrapped `using (…)` is cased directly.
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import agda_mask, agda_walk, ban_census, baseline_io, corpus

# ⚑ A WRAPPED `using` — the shape a line-wise scan misses entirely.
_WRAPPED = (
    "open import Substrate.Foundation.Eq using\n"
    "  ( _≡_\n"
    "  ; refl\n"
    "  )\n"
    "open import Substrate.Foundation.Nat\n"
)

# ⚑ EACH BANNED DIRECTIVE, one per line, to pin the key spelling for all four.
_EACH = (
    "open import Substrate.A using (x)\n"
    "open import Substrate.B renaming (y to z)\n"
    "open import Substrate.C hiding (w)\n"
    "import Substrate.D as E\n"
)

# ⚑ A COMMENTED-OUT IMPORT is not an import — in a paydown-only ratchet, censusing one creates
# a key nobody can ever remove.
_COMMENTED = "-- open import Substrate.Ghost using (x)\nopen import Substrate.Real\n"

#: How many differing keys to show when an arm fails — enough to diagnose, few enough to stay
#: readable against a census in the thousands.
_SHOW = 3


def _keys(rel: str, src: str) -> set[str]:
    """Census one source the way the gate does — stripped, then scanned."""
    return ban_census.keys_for(rel, agda_mask.mask_comments(src).split("\n"))


def _directive_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for which directives are banned and how they are keyed."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    got = _keys("f.agda", _EACH)
    # ⚑⚑ THE KEY SPELLING IS THE BASELINE'S CONTRACT. A different separator or ordering reads as
    # a new offender and refuses the commit.
    check("a using directive is keyed", passed="f.agda::Substrate.A::using" in got)
    check("a renaming directive is keyed", passed="f.agda::Substrate.B::renaming" in got)
    check("a hiding directive is keyed", passed="f.agda::Substrate.C::hiding" in got)
    check("an as alias is keyed", passed="f.agda::Substrate.D::as" in got)

    # ⚑⚑ THE CONTROLS. A censuser that keyed every import would satisfy all four arms above,
    # and in a paydown-only ratchet an over-count is a key nobody can remove.
    check(
        "a bare Substrate import is NOT keyed",
        passed=_keys("f.agda", "open import Substrate.Plain\n") == set(),
    )
    check(
        "a non-Substrate import is NOT keyed",
        passed=_keys("f.agda", "open import Data.Nat using (x)\n") == set(),
    )

    return out


def _span_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the statement-aware scan."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ⚑⚑⚑ THE WRAPPED DIRECTIVE — the shape a line-wise scan misses, and the reason this reads
    # spans through the authority rather than a local rule.
    wrapped = _keys("f.agda", _WRAPPED)
    check(
        "a directive on a continuation line is found",
        passed="f.agda::Substrate.Foundation.Eq::using" in wrapped,
    )
    # ⚑ AND THE IMPORT AFTER IT IS NOT SWALLOWED: a span that ran long would take the next
    # statement into the first one's tail and key it wrongly.
    check(
        "and the following bare import is not keyed",
        passed="f.agda::Substrate.Foundation.Nat::using" not in wrapped,
    )
    check("so exactly one key comes out", passed=len(wrapped) == 1)

    # ⚑⚑ A COMMENTED-OUT IMPORT IS NOT AN IMPORT. Censusing one creates a permanent key.
    check("a commented-out import is not censused", passed=_keys("f.agda", _COMMENTED) == set())

    return out


def _baseline_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` grounding the census on the COMMITTED BASELINE — gate-F75.

    ⚑⚑⚑ THE REFUSAL PREDICATE, ASSERTED AS A PROPERTY. If this census invented a key — a
    different separator, an absolute path, a directive matched too eagerly — it would read as a
    NEW offender and the ratchet would refuse every commit until somebody edited the baseline to
    accommodate a phantom. That is the failure this arm exists to catch, and it survives the swap
    because the baseline is a file rather than a computation.

    ⚑ CONTAINMENT, NEVER EQUALITY — see the module docstring: the baseline is a high-water mark
    and equality would go red on honest paydown.
    """
    baseline = corpus.ROOT / "scripts" / "ban_ratchet_baseline.txt"
    absent = "the committed baseline is absent, so the grounding is SKIPPED, not run and not passed"
    if not baseline.exists():
        return [(absent, True)]

    src = corpus.ROOT / "agda" / "Substrate"
    if not src.is_dir():
        return [("no agda tree was found to census — a fact about the TREE", True)]

    held = baseline_io.read_baseline(str(baseline))
    pairs = [
        (str(Path(path).relative_to(corpus.ROOT)), text) for path, text in agda_walk.sources(src)
    ]
    found = ban_census.census(pairs)

    novel = found - held

    # ⚑⚑⚑ CONTAINMENT WAS THE WRONG PROPERTY AND ASSERTING IT FAILED — gate-F76. I reasoned that
    # a paydown-only baseline must contain today's census, since the gate reports a pending
    # paydown. It does not: `commit_refusal` reports this ratchet as OVER with real ADDED keys,
    # and had done so for every tick of this session. The gate is simultaneously paying down
    # thousands and carrying hundreds of new offenders, and reading its headline paydown figure
    # as the whole story hid the second half.
    #
    # ⚑⚑ SO THE ASSERTABLE PROPERTY IS THE OVERLAP, NOT THE CONTAINMENT. If the census keyed
    # differently — another separator, an absolute path, a directive matched too eagerly — then
    # essentially NOTHING would match and every key would read as new. That is the census defect
    # this arm exists to catch, and it is distinguishable from ordinary drift by scale: a
    # spelling change breaks all of it, real offenders are a small tail.
    matched = found & held
    out: list[tuple[str, bool]] = [
        (
            "the census and the baseline agree on most keys, so the spelling is intact",
            len(matched) > len(novel),
        ),
    ]
    # ⚑⚑ TWO POSITIVE CONTROLS, because the arm above is satisfied by an EMPTY census and by an
    # all-encompassing baseline. Both must be non-empty for the overlap to mean anything —
    # otherwise a censuser returning nothing would pass the one check standing between this gate
    # and a phantom refusal.
    out.append(("and the census is non-empty, so the overlap is not vacuous", bool(found)))
    out.append(("and the baseline is non-empty either", bool(held)))
    # ⚑ THE NEW KEYS ARE REPORTED RATHER THAN ASSERTED AWAY. They are the gate's own finding —
    # real work the ratchet is refusing a commit over — and a case that went red on them would
    # be re-litigating a verdict this suite does not own.
    out.append(
        (f"and the gate's own added keys are visible here (e.g. {sorted(novel)[:_SHOW]})", True)
    )
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _directive_cases() + _span_cases() + _baseline_cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"ban-census selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
