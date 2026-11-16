# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.build_targets` — the declared roster, checked against the live makefile.

⚑⚑⚑ THE EXTRACTION IS ONLY HONEST IF IT AGREES WITH WHAT THE BUILD ACTUALLY RUNS, and the live
`agda/Makefile` is that witness. It was generated from the three hand-maintained lists this
roster replaces, so comparing against it is comparing the derivation to the thing derived — the
one check that can catch a gate silently dropped or renamed during the extraction.

⚑⚑ AND ONE ROW IS DELIBERATELY EXPECTED TO DIVERGE: `check-public` now runs the migrated package
gate rather than the retiring script, so its RECIPE differs from the live file by design while
its NAME must still match. Asserting name-agreement and recipe-divergence separately is what
keeps the intended change from hiding an unintended one.
"""

from __future__ import annotations

from substrate import build_targets, corpus, make_rules


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the roster is well-formed ────────────────────────────────────────────
    check("every check target is named", passed=all(t.name for t in build_targets.CHECKS))
    check("and every one carries a command", passed=all(t.command for t in build_targets.CHECKS))
    # ⚑ THE RATIONALE IS DATA, NOT DECORATION. A row without it emits a recipe less informative
    # than the hand-written block it replaced.
    check("and every one states why it exists", passed=all(t.why for t in build_targets.CHECKS))
    check(
        "the names are unique", passed=len(set(build_targets.names())) == len(build_targets.CHECKS)
    )

    # ── blocking vs advisory is a KIND, not a severity ───────────────────────
    check("every check target blocks", passed=all(t.is_blocking for t in build_targets.CHECKS))
    check("and the advisory one does not", passed=not build_targets.ADVISORY.is_blocking)
    check(
        "the advisory target is outside the check roster",
        passed=build_targets.ADVISE not in build_targets.names(),
    )

    # ── lookup ───────────────────────────────────────────────────────────────
    check(
        "a declared target is found by name", passed=build_targets.by_name("check-cap") is not None
    )
    check("and an undeclared one is not", passed=build_targets.by_name("check-nothing") is None)

    # ── agreement with the LIVE makefile ─────────────────────────────────────
    root = corpus.ROOT / "agda" / "Makefile"
    if not root.exists():
        check("the root Makefile is present to compare against", passed=False)
        return out

    live = make_rules.read(root)
    declared = set(build_targets.names())

    # ⚑⚑⚑ THE AGREEMENT CASE. A gate the live build runs but this roster omits would be
    # SILENTLY DROPPED the moment the emitter reads from here — the failure mode that makes an
    # extraction worse than the monolith it replaced.
    missing = {name for name in declared if not make_rules.has_target(live, name)}
    check("every declared check target exists in the live makefile", passed=not missing)

    # ⚑ AND THE OTHER DIRECTION: a `check-` target the live file has and this does not.
    live_checks = set(live.targets_matching("check-"))
    check(
        "and the live makefile declares no check target this roster lacks",
        passed=not (live_checks - declared),
    )

    # ⚑⚑ THE INTENDED DIVERGENCE, ASSERTED RATHER THAN ASSUMED. `check-public` keeps its NAME
    # and changes its RECIPE, because the gate migrated into the package. Pinning both halves is
    # what stops a deliberate change from concealing an accidental one.
    public = build_targets.by_name("check-public")
    check("check-public still runs a gate", passed=public is not None and bool(public.command))
    check(
        "and it now names the package module, not the retiring script",
        passed=public is not None
        and "substrate.public_gate" in public.command
        and not any("check_public_ratchet" in part for part in public.command),
    )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"build-targets selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
