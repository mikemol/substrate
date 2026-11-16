#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Write `Selftest.mk` — the flat, membudget-gated makefile over every discovered suite.

⚑ THE CLI IS ITS OWN MODULE BECAUSE THE RENDERER SHOULD NOT WRITE FILES. `gen_selftest_mk`
takes data and returns text; this decides where that text lands and what to report. A renderer
that also wrote would be untestable without a filesystem, and a case that has to mkdir a
tempdir to check a string is a case testing the wrong thing.

    selftest_mk.py            # write Selftest.mk
    selftest_mk.py --print    # render to stdout, write nothing
    selftest_mk.py --check    # REFUSE if the committed file is not what we would render

⚑⚑ THE NON-LEAF SUITES ARE REPORTED, NOT MERELY HANDLED. A suite declaring `runs_roster` fans
out — it invokes the roster containing it — and `suite_claims` gives it `claim:roster` so two
cannot run at once. Printing them keeps that visible: a reader who does not know the fan-out
exists cannot tell a serialized suite from a slow one, and `--output-sync=target` buffers only
the OUTER target of a recipe that fans out.

⚑⚑⚑ `--check` EXISTS BECAUSE ITS ABSENCE PRODUCED A FALSE GREEN AND A LOST SUITE (⟡roster-
currency-ungated, 2026-09-01). A session added `substrate/suite_record_selftest.py`, ran
`gen_selftest_mk.py --check` to confirm the roster was current, read exit 0, and reported the
roster clean. **`gen_selftest_mk.py` is a pure RENDERER with no `main` and no CLI** — it accepts
any flag, executes the module, and exits 0 having done nothing. Discovery found 236 suites;
`Selftest.mk` declared 235; the missing one was the suite just written, and it went unrun.

⚑⚑ **A FLAG A PROGRAM DOES NOT IMPLEMENT IS INDISTINGUISHABLE FROM ONE IT SATISFIES.** Both
exit 0 and print nothing. That is `census-green-is-a-fact-about-the-census` in its purest form —
the verdict came from a program that never looked, and the reader could not tell. The mode
belongs HERE, in the module that owns the file, and it must be REACHED BY A GATE: a mode nobody
runs is what `declared_indexes` shipped, after which the next writer reintroduced the very
defect it diagnosed.

⚑ IT COMPARES RENDERED TEXT, NOT SUITE COUNTS. A count matching while the sets differ is the
worst case (`census-keyed-on-one-spelling`): two rosters of 236 with one suite swapped for
another read identical by number. The rendered file IS the artefact, so it is what is compared.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from mikemol.corpus import suite_discovery

from substrate import corpus, gen_selftest_mk, suite_claims, suite_declared

if TYPE_CHECKING:
    from pathlib import Path

# Where the generated makefile lands. Repo root, beside the other build entry points.
TARGET = "Selftest.mk"

# The prefix every stamp target carries in the rendered text.
_STAMP = "$(BUILD)/"


def targets(body: str) -> tuple[str, ...]:
    """Return the stamp targets a rendered makefile declares.

    ⚑ READ OFF THE RENDERED TEXT, so this sees what `make` sees rather than what discovery
    believes — which is the whole point of a differential check.
    """
    return tuple(
        line.split(":", 1)[0].strip()
        for line in body.splitlines()
        if line.startswith(_STAMP) and ".ran:" in line
    )


def check(body: str, path: Path, *, quiet: bool = False) -> int:
    """Refuse when the committed makefile is not what discovery would render now.

    ⚑⚑ THE DIFFERENCE IS NAMED BY TARGET, NOT JUST REPORTED AS "differs". A reader told only
    that the file is stale still has to work out WHICH suite moved; the missing-target list is
    the actionable half, and it says whether a suite was ADDED (regenerate) or LOST (a predicate
    changed, which is a different repair entirely).

    ⚑ AN ABSENT FILE IS STALE, NOT AN ERROR. A fresh checkout has no `Selftest.mk` and the
    remedy is the same one: run the generator.

    ⚑ `quiet` IS FOR THE CASES, NEVER FOR THE GATE. A negative control must drive a REFUSAL, and
    four of them printing their (correct) stale-roster diagnostics into a build log makes a
    PASSING suite read as a broken roster — a gate whose success output looks like failure is
    its own defect. The verdict is unaffected; only the explanation is withheld, and the gate
    never passes this.
    """

    def say(line: str) -> None:
        """Emit one diagnostic unless the caller is driving a fixture."""
        if not quiet:
            sys.stderr.write(line)

    try:
        found = path.read_text(encoding="utf-8")
    except OSError:
        say(f"gen-selftest-mk: {TARGET} is absent — run `selftest_mk.py`\n")
        return 1

    if found == body + "\n":
        return 0

    want, have = frozenset(targets(body)), frozenset(targets(found))
    say(f"gen-selftest-mk: {TARGET} is STALE — regenerate with `selftest_mk.py`\n")
    for target in sorted(want - have):
        say(f"  + discovered but NOT declared (would not run): {target}\n")
    for target in sorted(have - want):
        say(f"  - declared but NOT discovered (would fail to build): {target}\n")
    if want == have:
        # ⚑ THE SET CAN MATCH WHILE THE TEXT DIFFERS — a changed lease, claim tag, or the
        # generator itself. Reporting "stale" without saying the roster is unchanged would
        # send a reader hunting for a suite that never moved.
        say(
            "  ⚑ the suite set is UNCHANGED; a recipe body differs "
            "(lease, claim tag, or the generator)\n"
        )
    return 1


def main(argv: list[str]) -> int:
    """Render the makefile and write it, print it, or check the committed copy."""
    suites = suite_discovery.discover(corpus.ROOT)
    fanout = frozenset(suite_declared.self_including([label for label, _p in suites]))
    reaching = suite_claims.reaching_store(suites)
    body = gen_selftest_mk.text(suites, reaching, fanout)

    if "--print" in argv:
        sys.stdout.write(body)
        return 0

    path = corpus.ROOT / TARGET

    if "--check" in argv:
        return check(body, path)

    path.write_text(body + "\n", encoding="utf-8")
    sys.stdout.write(
        f"gen-selftest-mk: {len(suites)} suite(s), {len(reaching)} claiming "
        f"{suite_claims.PG}, {len(fanout)} non-leaf -> {TARGET}\n"
    )
    for label in sorted(fanout):
        sys.stdout.write(f"  ⚑ non-leaf (runs the roster): {label}\n")
    return 0


# ⚑⚑ `--selftest` DELEGATES TO THE SIBLING SUITE RATHER THAN EXITING 0 (⟡silent-nine). This
# guard used to return a bare `0` so `suite_discovery` would see the module — which made it a
# roster member asserting NOTHING, reported `silent (0/0)` by the very runner it generates the
# makefile for. That is the defect `suite_run`'s own docstring records catching in ITSELF on its
# first run through the new recipe, and the fix it prescribes is exactly this: a module whose
# cases live in a sibling must RUN that sibling.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        from substrate import selftest_mk_selftest

        sys.exit(selftest_mk_selftest.selftest())
    sys.exit(main(sys.argv))
