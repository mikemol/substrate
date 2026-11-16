#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Build the invocation for one suite: budgeted, dependency-supplied, tenant-declared.

⚑ THE BUDGET IS NOT OPTIONAL AND ITS ABSENCE IS SAID OUT LOUD. `membudget run` wraps each
suite in a cgroup lease, so a suite that walks 3457 files makes an eleventh wait instead of
OOMing the box. When the wrapper is missing the suite runs bare — but the LABEL says so rather
than the budget silently vanishing: a guard that degrades to measuring nothing is worse than
one that fails.

⚑⚑⚑ THE LEASE IS SIZED PER LABEL FROM RECORDED PEAKS, AND THE PARAGRAPH THAT USED TO SIT HERE
WAS WRONG IN BOTH HALVES (gate-G374). It read: *"192MB is the shim's own cold-module default,
not a number chosen here… if a suite exceeds it the retry ladder doubles it and the peak is
recorded, so the budget self-corrects."* Neither clause held.

  - **The ladder cannot fire on this path.** `membudget`'s retry is guarded on
    `MEMBUDGET_RETRY_OOM`, and a literal census finds that name in exactly three files —
    `compile_recipe`, its suite, and `gate_status`. This module set no environment at all, so a
    suite over its lease was KILLED, not escalated.
  - **A killed run records nothing.** `_record_time` only runs on `rc == 0`, so the heaviest
    suites erased themselves from the ledger — the budget could not self-correct because the
    correction depended on the run that never completed.

⚑⚑ SO A FLEET-WIDE CONSTANT WAS BOTH TOO SMALL AND TOO LARGE AT ONCE. Measured under a headroom
lease: `sync_verdict_selftest` peaks at 422MB and was killed at 192, while the ledger's median
suite suggests 64MB and leased 192 anyway. One number for ~234 suites is over-sized for the
median and fatal for the tail, which is the defect `membudget`'s own `_auto_mb` argues against.

⚑ THE SIZER ALREADY EXISTED AND NOTHING CONSUMED IT. `substrate/label_lease.size()` rounds a
label's max recorded peak up to the next power of two, and `substrate/label_ledger.ledger_path()`
names the file `membudget` writes. Before this wiring, `module_importers label_lease` reported
ONE importer — its own suite. The measurement and the arithmetic were both in place and the two
were never joined, which is the built-then-orphaned rung this repo keeps finding.

⚑ AN EXPLICIT `SELFTEST_MB` STILL WINS, and that ordering is deliberate: an operator naming a
size did so for a reason history cannot see. History informs the DEFAULT, never the instruction.

⚑⚑ AN ABSENT DEPENDENCY WAS SCORING AS A PASS-SHAPED SKIP, which is why the runner SUPPLIES
declared deps rather than exempting suites that lack them. MEASURED: `jea_circuit` returned
True on `SKIP (numpy absent)`; with numpy supplied it runs **300/300** against a
Laplacian-pseudoinverse oracle at worst |Δ|=1.38e-14 — a real verification that had been
silently not running.

⚑⚑⚑ THE TENANT RIDES ON BOTH BRANCHES, AND THAT ASYMMETRY IS THE RECORDED DEFECT. The `uv`
form REBUILDS the inner command from scratch, so a fix applied to one branch works for every
suite except the ones declaring a dependency — invisible in testing unless a fixture declares
both. This module builds the inner argv ONCE and both branches consume it, so the shape cannot
recur.

⚑ EXTRACTED FROM `scripts/run_selftests.py` (⟡run-selftests-cut). Stopping rule: not until the
file is editable, but **until no module can BECOME uneditable.**
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from mikemol.corpus import suite_pragmas

from substrate import label_lease, label_ledger, tenant_pragma

# The lease wrapper, and the floor a label with no history takes.
#
# ⚑ 192 IS NOW A FALLBACK, NOT A FLEET-WIDE LEASE. It applies to a label the ledger has never
# seen; every label with recorded runs is sized from its own peaks. See the header for why the
# single-constant form was both too small and too large.
MEMBUDGET_ENV = "SUBSTRATE_MEMBUDGET"
SUITE_MB_ENV = "SELFTEST_MB"
DEFAULT_SUITE_MB = "192"

# ⚑ THE CEILING THIS MODULE ALLOWS HISTORY TO INFER, above `label_lease`'s own 384. A suite is a
# one-shot local process, not one of ~21 concurrent agda compiles packed into a shared budget, so
# the reason that ceiling is low upstream does not apply here. MEASURED: the `sync_verdict` pair
# peaks at ~421MB, which 384 would clamp BELOW the known need — the loud-clamp state the sizer
# exists to report rather than a size anyone wants.
SUITE_CEILING_MB = 1024

# ⚑ RESOLVED, NOT ASSUMED PRESENT. `uv` supplies a suite's declared optional deps; if it is
# absent the suite runs bare and reports its own SKIP, which is the honest degradation.
_UV = shutil.which("uv")


def uv_path() -> str | None:
    """Return the resolved `uv`, or None when it is not installed.

    ⚑ AN ACCESSOR BECAUSE A CASE MUST ASK. Whether `uv` exists is machine-dependent, so the
    dependency-supplying arm has to know which branch is CORRECT here rather than assert one —
    and reaching for the private name to find out would be `SLF001` telling me the module does
    not admit a question its own suite needs to ask.
    """
    return _UV


def membudget(root: Path) -> str:
    """Return the lease wrapper's path — overridable, so a case can point it elsewhere."""
    return os.environ.get(MEMBUDGET_ENV) or str(root / "scripts" / "membudget")


def label_of(path: str) -> str:
    """Return the ledger label for one suite.

    ⚑ ONE SPELLING, BECAUSE THE LABEL IS A JOIN KEY. It names the row `membudget` writes and the
    row the sizer reads back, so a second derivation would silently size a suite from a history
    belonging to nothing.
    """
    return f"selftest:{Path(path).name}"


def suite_mb(path: str | None = None) -> str:
    """Return the lease in MB for one suite: explicit, else sized from history, else the floor.

    ⚑ THE ORDER IS THE WHOLE DESIGN. `SELFTEST_MB` is an instruction and wins outright. Absent
    that, a label with recorded peaks is sized from its own maximum; a label with none takes the
    floor. So history informs a default and never overrides a caller.

    ⚑ NO PATH MEANS NO HISTORY TO CONSULT, which keeps the nullary form a caller can still ask
    for the floor — and makes this readable without a ledger present at all.
    """
    named = os.environ.get(SUITE_MB_ENV)
    if named:
        return named
    if path is None:
        return DEFAULT_SUITE_MB
    sizing = label_lease.size(
        label_ledger.ledger_path(), label_of(path), int(DEFAULT_SUITE_MB), SUITE_CEILING_MB
    )
    return str(sizing.lease_mb)


def _budgeted(wrapper: str) -> bool:
    """Report whether the lease wrapper is present and executable."""
    return Path(wrapper).is_file() and os.access(wrapper, os.X_OK)


def inner_command(path: str, interpreter: str) -> list[str]:
    """Build the un-budgeted invocation: the interpreter, the suite, its flag and tenant.

    ⚑ BUILT ONCE AND SHARED BY BOTH BRANCHES. The pre-split form assembled it twice — plainly
    and again inside the `uv` branch — which is exactly how the tenant flag came to be applied
    to one branch and not the other.
    """
    tenant = tenant_pragma.tenant(path)
    deps = suite_pragmas.requires(path)
    tail = [path, "--selftest", *([tenant] if tenant else [])]
    if deps and _UV:
        # `uv run` provides the interpreter; the lease still wraps it.
        with_flags = [flag for dep in deps for flag in ("--with", dep)]
        return [_UV, "run", "--quiet", *with_flags, "python3", *tail]
    return [interpreter, *tail]


def command(path: str, interpreter: str, root: Path) -> list[str]:
    """Return the full argv for running one suite, budgeted when the wrapper exists."""
    inner = inner_command(path, interpreter)
    wrapper = membudget(root)
    if not _budgeted(wrapper):
        return inner
    return [wrapper, "run", suite_mb(path), label_of(path), "--", *inner]
