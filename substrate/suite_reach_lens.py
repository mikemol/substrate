#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Count the case call sites a suite HOLDS, following the dispatch/body split.

⚑⚑⚑ IT FOLLOWS THE SPLIT, BECAUSE A SUITE IS A PAIR AND DISCOVERY ALREADY SAYS SO.
Decomposing an over-cap module moves `_selftest` into a sibling while the parent keeps the
`--selftest` dispatch. MEASURED 2026-08-25: counting the dispatching file ALONE reported
`pycodemod.py` as **0** case sites while its 361 live in `_pycodemod_selftest.py`. Ten of
104 suites read zero that way.

⚑ AND A ZERO IS THE WRONG DIRECTION TWICE OVER: as a BASELINE it records 0 and reads every
later run as growth; as a CURRENT reading it makes the shed look enormous and classifies any
drop as `deleted` — excusing exactly the regression the reach gate exists to refuse.

⚑ ONE HOP, NOT A CLOSURE. A split body is bound by a DIRECT module-level import from the
dispatching file; walking transitively would sweep in every helper the tool imports and count
their internal `check`-shaped calls as this suite's cases. Testing "has a `_selftest` body"
alone made `run_selftests.py` read **227** (it imports `rungs`, a 53-case suite). An inflated
baseline is worse than an absent one: it records a number no honest run can reach.

⚑ THE CROSSED-INTO FILE MUST BE AN IMPLEMENTATION HALF — a `_selftest` body AND NO DISPATCH
of its own. A file with both IS a suite in its own right and its cases are counted under its
OWN label, so crossing into it would double-count them.

⚑ AN UNPARSEABLE HALF POISONS THE WHOLE READING, deliberately. A partial count would
understate the suite and make a real drop look like deletion, so the total goes to `None`.

⚑ IT IS DELIBERATELY NOT AN EXACT COUNT. A case registered inside a loop is ONE call site and
MANY cases, so this lens and the run's own `total` are NOT comparable as absolute numbers —
only each lens against ITS OWN history is. That inexactness is why it CLASSIFIES rather than
gates: `reach_ratchet` refuses on the RUN count, which is exact; this only decides which
sentence the refusal prints.

⚑ EXTRACTED FROM `scripts/run_selftests.py` (⟡retire-the-runner). The counting itself is
`case_lens.own_cases` and the import walk is `import_reach`; what lives here is only the rule
for WHICH files a suite's count spans. The cases live in `suite_reach_lens_selftest`, which
carries the `--selftest` dispatch for this pair.
"""

from __future__ import annotations

from pathlib import Path

from mikemol.corpus import suite_discovery

from substrate import case_lens, import_reach

# Totals, keyed by path. A suite's source does not change within one run.
_CACHE: dict[str, int | None] = {}


def _source(path: str) -> str | None:
    """Return a file's source, or None when it cannot be read."""
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def is_implementation_half(src: str) -> bool:
    """Report whether this source is a split-out body rather than a suite of its own.

    ⚑ THE PREDICATE IS `suite_discovery`'s READ IN THE MIRROR: a body with no entry point.
    Naming it against that module is what keeps the two from drifting into disagreement
    about what a suite is.
    """
    return bool(
        suite_discovery.HAS_SELFTEST.search(src) and not suite_discovery.HAS_ENTRY.search(src)
    )


def static_cases(path: str, index: dict[str, str] | None = None) -> int | None:
    """Return how many case-registering CALLS this suite's source holds, or None.

    `None` means UNKNOWN — never 0, which would read as "every case was deleted".
    """
    if path in _CACHE:
        return _CACHE[path]
    raw = import_reach.module_index() if index is None else index
    table = {name: str(where) for name, where in raw.items()}
    total = case_lens.own_cases(path)
    here = Path(path).resolve()
    for name in sorted(import_reach.local_imports(Path(path))):
        sib = table.get(name)
        if sib is None or Path(sib).resolve() == here:
            continue
        src = _source(sib)
        if src is None or not is_implementation_half(src):
            continue
        n = case_lens.own_cases(sib)
        if n is None:
            total = None
            break
        total = n if total is None else total + n
    _CACHE[path] = total
    return total
