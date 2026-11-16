# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.baseline_health` — baseline state over every gate home.

⚑⚑⚑ THE LOAD-BEARING CASE IS THAT EMPTY AND ABSENT STAY APART. They render as adjacent-looking
rows and mean opposite things: ABSENT makes the gate record-and-pass whatever it measured (a
vacuous green), while EMPTY is zero-tolerance — every offender is a NEW key, the STRONGEST
setting and never a defect. A reader that collapsed them, which a bare existence check invites,
would report the strongest configuration and the most vacuous one identically.

⚑⚑ AND `is_defect` IS ASKED, NEVER RE-DERIVED. `BaselineState` records six sites computing that
property by string comparison with three getting it wrong; a case here that spelled out which
states are defects would be the seventh, and it would pass while disagreeing with the authority.

⚑ THE LIVE-TREE CASES ASSERT PRESENCE AND RELATIONSHIPS, NEVER A COUNT. A count of baselines is
a measurement of the repo, red the next time anyone adds a gate.
"""

from __future__ import annotations

from substrate import baseline_health, baseline_state


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the literal reader finds both declaration spellings ──────────────────
    const = 'BASELINE = os.path.join(HERE, "public_ratchet_baseline.txt")\n'
    check(
        "a module-constant baseline is found",
        passed=baseline_health.baselines_named(const) == ["public_ratchet_baseline.txt"],
    )
    # ⚑ THE INLINE SPELLING IS NOT OPTIONAL. One gate carries TWO ratchets by passing paths at
    # the call site, so a declaration-only reader sees neither — and one of those was the
    # zero-byte file the whole mode exists to surface.
    inline = (
        'set_ratchet(a, "snapshot_guard_baseline.txt")\n'
        'set_ratchet(b, "mutation_intent_baseline.txt")\n'
    )
    check(
        "inline call-site baselines are found, both of them",
        passed=len(baseline_health.baselines_named(inline)) == 2,
    )  # noqa: PLR2004
    # ⚑ ONE BASELINE NAMED TWICE IS ONE BASELINE. A gate naming it in a constant AND at the
    # call would otherwise get two rows for one ledger.
    twice = const + 'set_ratchet(c, "public_ratchet_baseline.txt")\n'
    check(
        "a baseline named twice yields one entry",
        passed=len(baseline_health.baselines_named(twice)) == 1,
    )
    check(
        "a file naming no baseline yields none",
        passed=baseline_health.baselines_named("x = 1\n") == [],
    )

    # ── states: EMPTY and ABSENT must not collapse ───────────────────────────
    absent = baseline_health.row_for("g", "no-such-baseline-file.txt")
    check(
        "a missing baseline reads ABSENT",
        passed=absent.state == baseline_state.BaselineState.ABSENT,
    )
    # ⚑ ASKED, NOT RE-DERIVED — the authority decides which states are defects.
    check("and ABSENT is a defect, per the state itself", passed=absent.is_defect)

    # ⚑ EMPTY IS THE STRONGEST SETTING, NOT A DEFECT. Asserting this from the authority keeps
    # a future reader from "fixing" the strongest configuration.
    check("EMPTY is not a defect", passed=not baseline_state.BaselineState.EMPTY.is_defect)
    # ⚑ AND IT CARRIES NO MARK EITHER — a first cut of this case was LABELLED "still deserves
    # a mark" while asserting the opposite, and passed. Both halves came from me rather than
    # from the authority, which is how a case ends up agreeing with the code and disagreeing
    # with its own description. `deserves_mark` flags the rows an operator must look at, and
    # zero-tolerance is not one of them.
    check(
        "and EMPTY carries no mark, being the intended strongest setting",
        passed=not baseline_state.BaselineState.EMPTY.deserves_mark,
    )
    # ⚑ WHEREAS UNREAD DOES: not a defect, but a row the reader could not resolve, which an
    # operator must see rather than read as healthy.
    check(
        "UNREAD is not a defect yet still deserves a mark",
        passed=not baseline_state.BaselineState.UNREAD.is_defect
        and baseline_state.BaselineState.UNREAD.deserves_mark,
    )

    # ── the live tree: the gates a scoped census cannot see ──────────────────
    rows = baseline_health.health()
    gates = {r.gate for r in rows}
    check("a package gate appears in the health table", passed="substrate/private_gate.py" in gates)
    check("and so does the other one", passed="substrate/type_gate.py" in gates)
    check("alongside the scripts-era gates", passed="scripts/check_ban_ratchet.py" in gates)

    # ⚑⚑ TWO GATES OVER ONE LEDGER IS VISIBLE ONLY IN A UNIFIED POPULATION. A scoped census
    # cannot express this because it never holds both rows at once — which is the whole
    # argument for the widened population, independent of what the sharing turns out to mean.
    #
    # ⚑⚑⚑ AND THE SHARING IS OVER: THE MIGRATION COMPLETED AND THIS ARM OUTLIVED IT (gate-G375).
    # It asserted exactly two rows over `private_ratchet_baseline.txt` — the package gate and the
    # `scripts/` origin it was migrated from. MEASURED: `gate_population --gates` reports eighteen
    # gates and NO `check_private_ratchet.py`, and `tool_population --find private` finds no such
    # file either. The origin is gone, so one gate names that ledger and the count is 1.
    #
    # ⚑⚑ A TRACKER OF A TRANSITION MUST FAIL WHEN THE TRANSITION LANDS, which is what this did —
    # the same shape as the `--dropped` arm that went red the day its mode bound. So it now
    # asserts the FINISHED state rather than the transitional one, and it still fails if a second
    # gate ever reappears over this ledger.
    #
    # ⚑ AND `ratchet_key.SCHEMA` ALSO NAMES THIS FILENAME WITHOUT BEING A GATE. It is the schema
    # table, carrying the baseline as DATA, which is why `gate_population` does not count it —
    # a literal census over the tree finds three sites and only one of them is a gate.
    shared = [r.gate for r in rows if r.baseline == "private_ratchet_baseline.txt"]
    check(
        "exactly one gate owns the private ledger, the migration having completed",
        passed=shared == ["substrate/private_gate.py"],
    )
    # ⚑⚑⚑ AND THE PUBLIC LEDGER IS THE LIVE INSTANCE OF THE STATE THE PRIVATE ONE JUST LEFT.
    # MEASURED by the table this module renders: `public_ratchet_baseline.txt` carries TWO rows —
    # `scripts/check_public_ratchet.py` and `substrate/public_gate.py`, both at the same key count
    # — so the two-gates-over-one-ledger condition did not disappear, it MOVED. Pinning it here
    # keeps the unified population's whole argument exercised by a case that is true today, and
    # this arm is the one that will go red when the public migration finishes.
    public = [r.gate for r in rows if r.baseline == "public_ratchet_baseline.txt"]
    check(
        "the public ledger still has two gates — that migration has NOT completed",
        passed=sorted(public) == ["scripts/check_public_ratchet.py", "substrate/public_gate.py"],
    )

    # ── every row's state is a declared one ──────────────────────────────────
    known = set(baseline_state.BaselineState.all())
    check("every row carries a declared state", passed=all(r.state in known for r in rows))

    # ── the reader's own blind spots are part of the reading ─────────────────
    # ⚑ A HEALTH TABLE THAT SILENTLY OMITS A GATE IS THE DEFECT THIS CORRECTS, so it must not
    # commit the same one. The rendering names what it cannot cover.
    text = baseline_health.render()
    check("the rendering names the gates it does not cover", passed="NOT COVERED" in text)
    check("and the table names both homes", passed="scripts/" in text and "substrate/" in text)

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
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
