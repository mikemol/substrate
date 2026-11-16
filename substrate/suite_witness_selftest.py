#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.suite_witness` — the kinds, and what an absent reading means.

⚑⚑ `unrun` IS NOT A FAILURE KIND, AND THAT IS THE LOAD-BEARING CASE. A suite with no fresh
stamp has no reading at all; the absence has three causes the stamp cannot separate — never
run, ran and failed (the wrapper stamps only on success), or cleaned. Folding it into `silent`
or `cases` would name a cause the evidence does not support, and reporting it as ok would bank
a green verdict nothing measured.

⚑ THE MODULE'S OTHER PROPERTY — that it cannot start a build — is not asserted here. A source
scan for `subprocess` would be a fragile proxy, and the honest form is a census over EVERY file
(⟡dispatch-through-make), not a string search inside one suite.
"""

from __future__ import annotations

import sys

from substrate import suite_witness

# The kinds a stamp can carry, from `suite_outcome`. Only `ok` means fine.
_KINDS = ("ok", "cases", "vacuous", "unfit", "refused", "silent", "unread")


def only_ok_is_ok(out: list[str]) -> int:
    """Check every kind except `ok` is reported as not-ok."""
    rows: list[suite_witness.Row] = [
        suite_witness.Row(label=f"{k}.py", kind=k, fresh=True) for k in _KINDS
    ]
    bad = suite_witness.not_ok(rows)
    if len(bad) != len(_KINDS) - 1:
        out.append(f"selftest: {len(bad)} of {len(_KINDS)} kinds read as not-ok")
        return 1
    if any(r.kind == suite_witness.OK for r in bad):
        out.append("selftest: an `ok` suite was reported as not-ok")
        return 1
    return 0


def unrun_is_not_ok_and_is_its_own_kind(out: list[str]) -> int:
    """Check a suite with no fresh reading is reported, and not as a failure kind.

    ⚑ THE THREE CAUSES — never run, ran and failed, cleaned — are not separable from a missing
    stamp. Folding `unrun` into `silent` would name one of them.
    """
    row = suite_witness.Row(label="x.py", kind=suite_witness.UNRUN, fresh=False)
    bad = 0
    if not suite_witness.not_ok([row]):
        out.append("selftest: an unrun suite read as ok")
        bad += 1
    if suite_witness.UNRUN in _KINDS:
        out.append("selftest: `unrun` collides with a suite_outcome kind")
        bad += 1
    return bad


def rows_reads_the_live_tree(out: list[str]) -> int:
    """Check the reader returns one row per discovered suite.

    ⚑ A ROW PER SUITE, NEVER A SCALAR. The witness this replaces was corrected from one verdict
    over 49 suites to a row emitter, because a scalar standing for a population cannot be
    ranked and cannot close on its own.
    """
    got = suite_witness.rows()
    if not got:
        out.append("selftest: the reader returned no rows over a live tree")
        return 1
    if any(r.kind == suite_witness.OK and not r.fresh for r in got):
        out.append("selftest: a row reported `ok` without a fresh stamp")
        return 1
    return 0


_ARMS = (only_ok_is_ok, unrun_is_not_ok_and_is_its_own_kind, rows_reads_the_live_tree)

_CASE_COUNT = 1 + 2 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"suite-witness selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"suite-witness selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
