#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Is this process already inside a suite — the re-entrancy mark, and nothing else.

⚑⚑⚑ THIS BOUNDS A RELATION WITH A GENUINE SELF-EDGE, WHICH IS WHY IT IS NOT THE BOUND-SHAPED
DEFECT THIS REPO KEEPS FILING. A depth cap on a well-founded descent is a capability bound
wearing a termination bound's clothes — a three-level walk that lost 1,506 of 2,964 modules, a
round cap that read a converging sequence as divergent. **This is different in kind**: a suite
can invoke a roster that contains it, so the graph really does have a cycle, and refusing to
re-enter is the only thing that terminates it.

⚑⚑ AN ENVIRONMENT VARIABLE, BECAUSE THE SCOPE IS THE PROCESS TREE. A module-level flag guards one
interpreter; the cycle here crosses `subprocess` boundaries, where a child inherits the
environment and nothing else. Measured off a live process tree, the unguarded form reached four
generations deep at load 54.93 with 68 concurrent processes.

⚑ THE MARK ACCUMULATES RATHER THAN REPLACING, so a reader can see the whole chain — `a:b:c` says
which suites are stacked, which is the difference between *"something is running"* and *"THIS is
what it is inside"*. A boolean would answer the guard's question and none of the diagnostic ones.

⚑⚑ AND ONLY THE MARK IS PROMOTED. The tool this came from also carried `execute` and `run` — a
member-fan-out over a roster — and those are exactly what must not be reproduced: the fan-out has
one owner, `make`, which runs the DAG in poset order under the memory semaphore's lease and claim
gates. A second dispatcher is the thing the guard exists to make survivable, not a thing to carry
forward.

⚑ PROMOTED FROM `scratch/` (⟡items-n-split): a witness in a promoted tree may not depend on
`scratch/` at runtime, and the sanctioned resolution is promotion rather than repathing.
"""

from __future__ import annotations

import os

# ⚑ THE NAME IS THE CONTRACT ACROSS PROCESSES, so it is a module constant rather than a literal
# at each site: a mark written under one spelling and read under another is a guard that never
# fires, and the failure is a fork bomb rather than an error.
MARK = "SUBSTRATE_SUITE_RUNNING"

# The separator between stacked suite labels. ⚑ `os.pathsep`, matching how every other
# environment list on this platform is written, so a reader parses it the way they already know.
SEP = os.pathsep


def in_suite() -> bool:
    """Report whether this process, or an ancestor that passed the mark on, is running a suite."""
    return bool(os.environ.get(MARK))


def stack() -> tuple[str, ...]:
    """Return the suite labels currently entered, outermost first.

    ⚑ THE CHAIN, NOT A COUNT. A guard needs only the boolean; a reader diagnosing an unexpected
    refusal needs to know WHICH suites are stacked, and a count cannot say.
    """
    current = os.environ.get(MARK, "")
    return tuple(part for part in current.split(SEP) if part)


def enter_suite(label: str) -> str:
    """Mark this process as running `label`'s suite, and return the resulting stack.

    ⚑ CALLED BY THE SUITE ENTRY POINT, so the mark exists for the whole run regardless of how the
    suite was invoked — by a runner, by a witness deriving a miss, or by hand at a shell. A mark
    set by the CALLER would be absent on exactly the paths nobody anticipated.

    ⚑ APPENDING RATHER THAN REPLACING is what makes the stack readable; re-entering the same
    label twice is recorded twice, because that IS the cycle a reader is trying to see.
    """
    current = os.environ.get(MARK, "")
    os.environ[MARK] = f"{current}{SEP}{label}" if current else label
    return os.environ[MARK]
