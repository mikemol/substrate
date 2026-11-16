# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.gate_population` — which files are ratchet gates, and where.

⚑⚑⚑ THE LOAD-BEARING CASES ARE THE OVER-ADMISSIONS, because every defect this module hit
while being written was in that direction. A population reader is judged by what it wrongly
INCLUDES as much as by what it finds: the authority a gate calls, a file that merely reads
baselines, and the reader itself all match a naive source-text predicate, and each one was
admitted by a real cut of this code before being excluded.

⚑⚑ A DEFINITION IS NOT A USE, and that is asserted directly rather than through the live
tree. `def run_gate(` matches a regex for `run_gate(`; so does `def write_baseline(`. Two
authorities entered the population that way, which is the library-as-its-own-consumer shape,
and the fix is structural rather than a name list.

⚑ THE LIVE-TREE CASE IS DELIBERATELY WEAK. It asserts that a known gate is found and a known
authority is not, never a COUNT — a count here would be a measurement of the repo wearing a
case's clothes, red on the next file anyone adds.
"""

from __future__ import annotations

from substrate import gate_population

_CALLS = "x = set_ratchet(census, path)\n"
_WRITES = 'open(BASELINE, "w").write(text)\n'
_RUNS = "return run_gate(GATE, REPORT, argv)\n"


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the three witnesses, each sufficient alone ───────────────────────────
    check("calling the shared ratchet is a witness", passed=gate_population.is_gate(_CALLS))
    check("writing a baseline is a witness", passed=gate_population.is_gate(_WRITES))
    # ⚑ THE PACKAGE'S SPELLING. Without this arm a migrated gate reads as not-a-gate, which
    # is the omission this whole module exists to close.
    check("running a declared Gate is a witness", passed=gate_population.is_gate(_RUNS))

    # ── a file doing none of it is not a gate ────────────────────────────────
    check(
        "prose about ratchets is not a witness",
        passed=not gate_population.is_gate("# this module reads baselines\n"),
    )

    # ── A DEFINITION IS NOT A USE — the over-admissions, asserted directly ───
    check(
        "the file that DEFINES set_ratchet is not a gate",
        passed=not gate_population.is_gate("def set_ratchet(census):\n    pass\n"),
    )
    check(
        "the file that DEFINES write_baseline is not a gate",
        passed=not gate_population.is_gate("def write_baseline(path, keys):\n    pass\n"),
    )
    check(
        "the file that DEFINES run_gate is not a gate",
        passed=not gate_population.is_gate("def run_gate(gate, report):\n    pass\n"),
    )

    # ⚑ AND A DEFINER THAT ALSO USES A DIFFERENT WITNESS IS STILL A GATE. The exclusion is
    # per-capability, not per-file: defining one thing must not blind the reader to another.
    check(
        "defining one capability does not mask a different witness",
        passed=gate_population.is_gate("def run_gate(g):\n    pass\n" + _CALLS),
    )

    # ── the homes are declared, and both are named ───────────────────────────
    check("scripts/ is a declared gate home", passed="scripts" in gate_population.GATE_HOMES)
    # ⚑ THE POINT OF THE MODULE. A gate that migrated must not leave the census.
    check("substrate/ is a declared gate home", passed="substrate" in gate_population.GATE_HOMES)

    # ── the live tree: presence and absence, never a count ───────────────────
    found = set(gate_population.gates())
    check("a migrated gate is found", passed="substrate/type_gate.py" in found)
    check("and so is the newer one", passed="substrate/private_gate.py" in found)
    # ⚑ THE INSTRUMENT IS NOT ITS SUBJECT. This file's own prose quotes the spellings it
    # matches on, so a source-text predicate finds its own documentation.
    check(
        "the population reader excludes itself", passed="substrate/gate_population.py" not in found
    )
    check("and the shared ratchet authority", passed="scripts/ratchet.py" not in found)

    # ── `outside` names what a scoped census would miss ──────────────────────
    missed = gate_population.outside("scripts")
    check(
        "outside() reports the gates a scripts-scoped census cannot see",
        passed=bool(missed) and all(not m.startswith("scripts/") for m in missed),
    )

    # ── the known misses are carried, not hidden ─────────────────────────────
    # ⚑ A REPLACEMENT THAT LOSES COVERAGE MUST SAY SO. Reporting only what it newly finds is
    # how a widening reader quietly drops rows the old one had.
    misses = gate_population.known_misses()
    check("the reader carries the gates it still misses", passed=bool(misses))
    check(
        "and each miss states WHY, not just that it is missing",
        passed=all(len(why) > len(path) for path, why in misses),
    )

    # ── the CLI answers, and an unknown flag REFUSES ─────────────────────────
    # ⚑⚑⚑ THIS MODULE EXITED 0 PRINTING NOTHING, bare and on `--help`, until the dispatch was
    # added. A silent exit 0 is indistinguishable from a tool that ran and found nothing —
    # so these cases assert the two states are DIFFERENT, which is the only way the
    # distinction stays true. Every mode is checked against the usage, because a mode present
    # in MODES and absent from USAGE is the divergence this family is measured for.
    check(
        "every declared mode is named in the usage",
        passed=all(flag in gate_population.USAGE for flag in gate_population.MODES),
    )
    check(
        "and every mode named in the usage is declared",
        passed=all(
            line.split()[1] in gate_population.MODES
            for line in gate_population.USAGE.splitlines()
            if line.startswith("  gate_population.py --") and line.split()[1] != "--selftest"
        ),
    )

    # ⚑ A BARE RUN PRINTS THE USAGE AND REFUSES — never the silent success that made this
    # reader's own findings unreachable from a command line.
    check(
        "a bare run refuses rather than exiting silently",
        passed=gate_population.main(["gate_population.py"]) == gate_population.REFUSED,
    )
    check(
        "and an unknown flag refuses too",
        passed=gate_population.main(["gate_population.py", "--nope"]) == gate_population.REFUSED,
    )

    # ⚑ EACH RENDERER PRODUCES A NON-EMPTY READING AND NAMES ITS COUNT. A renderer returning
    # "" would read as a clean population — the false zero this module exists to prevent.
    check(
        "--gates renders the population with a count",
        passed="gate(s)" in gate_population.render_gates(""),
    )
    check(
        "--outside renders what a scoped census misses",
        passed="outside scripts/" in gate_population.render_outside(""),
    )
    check(
        "--misses renders each miss with its reason",
        passed="known miss(es)" in gate_population.render_misses(""),
    )
    # ⚑ AND `--outside` TAKES ITS HOME AS AN ARGUMENT rather than assuming one. Asking about
    # `substrate` must report the scripts-resident gates, not repeat the default's answer.
    check(
        "outside() is parameterised by home, not fixed to one",
        passed=gate_population.render_outside("substrate")
        != gate_population.render_outside("scripts"),
    )

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
