#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Run a set-ratchet gate: validate argv, build the run, and rule — once, for all of them.

⚑⚑ NINE GATES REPEAT THE SAME `main()` AND DIFFER IN ONE FUNCTION. Each calls
`check_argv` with the same three flags, reads `--quiet` and `--list` out of `sys.argv` by
hand, and hands twelve arguments to `set_ratchet`. The only genuinely per-gate parts are
WHICH census to take, WHERE its baseline lives, and WHAT to say when it refuses.

⚑ THIS IS THE `render` LIFT ONE LEVEL UP, AND THE SAME ARGUMENT APPLIES. Four gates once
hand-rolled a `--list` block because the authority could not print their richer per-key
output; the measured difference was ONE LINE each, and lifting it deleted four dispatch
blocks. The dispatch itself is the same shape: nine copies of a flag parse differing in a
census function. A gate that forks this to add a flag is the defect to prevent, so the
flags live here and a gate declares only what it measures.

⚑⚑ AND IT IS THE ROUTE THAT RETIRES `ratchet_legacy`. Every gate converted to `run_gate`
stops calling the twelve-argument `set_ratchet`, so the exemption in `pyproject.toml`
shrinks toward deletable rather than being carried as permanent-looking debt. The
migration and the deduplication are one edit per gate, not two.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from mikemol.ratchet.render import Report

from substrate.ratchet_core import Census, Permission
from substrate.ratchet_core import set_ratchet as _rule
from substrate.ratchet_flags import check_argv

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

# ⚑ THE FLAGS EVERY SET-RATCHET GATE ACCEPTS, DECLARED ONCE. A gate that spells its own
# set can omit one by accident — measured on `--dry-run`, which `set_ratchet` resolves
# from argv but which six of eleven gates did not list, so the authority's own capability
# was unreachable through them. `check_argv` folds in `UNIVERSAL_FLAGS` on top of this.
GATE_FLAGS = frozenset({"--quiet", "--list", "--selftest"})

_DEFAULT_REPORT = Report()

# Exit code for a census that could not be taken. Distinct from 1 (debt grew) because the
# two demand different responses: 1 is fixed at the offending site, 2 is fixed in the
# environment, and conflating them sends a reader to look for code that is not wrong.
_CANNOT_MEASURE = 2


class Unmeasurable(Exception):  # noqa: N818 - it is a state, not an error condition
    """A census could not be taken, so there is nothing to rule on.

    ⚑⚑ WITHOUT THIS, `run_gate` COULD ONLY SAY 0 OR 1 — AND A GATE THAT CANNOT SAY
    "I DID NOT RUN" REPORTS ITS OWN BLIND SPOT AS A PASS. `check_mypy_ratchet` was built
    after exactly that defect: a `python3` without mypy installed produced no error lines, the
    parse honestly found nothing, and **0 keys over 60 unannotated files** was banked as a
    clean census. Its docstring calls the refusal branch *"the one branch that separates 'no
    type errors' from 'the checker never ran'"*.

    ⚑ SO MIGRATING THAT GATE TO `run_gate` WOULD HAVE SILENTLY DELETED ITS REASON FOR
    EXISTING. The authority could express "debt grew" and not "I am blind", so the migration
    would have looked like a simplification and been a regression — the shape where a
    consolidation quietly drops the one branch the consolidated thing was for.

    ⚑ IT CARRIES ITS REASON, NEVER JUST ITS FAILURE. "not importable" was once a guess
    printed as a fact; mypy exits non-census for a config error, a duplicate module name, or
    an unreadable path just as readily as for an absent install, and each wants a different
    fix. The constructor takes the real message.
    """

    #: What to suggest when a subclass knows the remedy for its whole class of failure.
    remedy: str = ""

    def __init__(self, reason: str) -> None:
        """Record why the census could not be taken.

        ⚑ THE REMEDY IS THE CLASS'S, THE REASON IS THE RAISE SITE'S — and the split is not
        cosmetic. A remedy is constant for a whole kind of failure ("install mypy for this
        interpreter"), so passing it at every raise is the same string re-typed and free to
        drift; a reason is whatever the tool actually said, which is exactly what must NOT be
        summarised into a plausible story.
        """
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True, slots=True)
class Gate:
    """A census that has not been taken yet, and where its verdict is kept.

    ⚑⚑ `PLR0913` FIRED A SEVENTH TIME AND MEANT THE SAME THING AGAIN: `label`, `census`,
    `baseline_path` and `key_move` are a `Census` before its keys exist. `ratchet_core`'s
    `Census` holds a taken census; this holds the recipe for one, which is the difference
    between what a gate DECLARES and what a run MEASURES.

    ⚑ THE CENSUS IS A CALLABLE, NOT A SET, so it is not taken when argv is refused. A gate
    whose census walks the Agda tree costs seconds; running it before discovering the
    operator typo'd a flag is work nobody asked for, and the refusal is the answer either
    way.
    """

    label: str
    census: Callable[[], Iterable[str]]
    baseline_path: str
    key_move: Callable[[str], str] | None = None

    def take(self) -> Census:
        """Run the census and pair it with its baseline."""
        return Census.of(self.census(), self.baseline_path, self.label, self.key_move)


def run_gate(gate: Gate, report: Report = _DEFAULT_REPORT, argv: list[str] | None = None) -> int:
    """Validate argv, take the census, and rule on it. 0 = pass, 1 = debt grew.

    ⚑ `--quiet` AND `--list` ARE READ HERE, ONCE. Nine gates read them out of `sys.argv`
    by hand and passed them down; a tenth would have had to remember. They are the
    authority's vocabulary, so the authority reads them.
    """
    args = sys.argv if argv is None else argv
    rc = check_argv(args, GATE_FLAGS, gate.label)
    if rc is not None:
        return rc
    tail = args[1:]
    # ⚑ `__replace__`, NOT `_replace` — the ⟡symbolic-reference-only conversion turned `Report`
    # from a `NamedTuple` into a frozen slotted dataclass, and the copy-with-changes spelling
    # differs. `copy.replace()` is the version-neutral form; the dunder is what a dataclass
    # provides directly (PEP 681, Python 3.13).
    shaped = report.__replace__(quiet="--quiet" in tail, list_keys="--list" in tail)
    try:
        taken = gate.take()
    except Unmeasurable as e:
        # ⚑ REFUSE, DO NOT REPORT CLEAN. `--quiet` does NOT silence this: quiet suppresses a
        # PASS, and this is not one. A gate that goes quiet about being blind is worse than a
        # noisy one, because the silence is indistinguishable from success.
        sys.stderr.write(
            f"{gate.label}: CANNOT MEASURE — refusing rather than reporting clean.\n"
            f"  reason: {e.reason}\n"
        )
        if e.remedy:
            sys.stderr.write(f"  try:  {e.remedy}\n")
        return _CANNOT_MEASURE
    return _rule(taken, shaped, Permission.resolve(args))
