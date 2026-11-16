# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Types for `paperkit.grade` — the engine's falsifiability ladder.

⚑ THE ENGINE SHIPS NO `py.typed`, SO ITS RETURN IS `Any` AT EVERY CALL SITE. A stub types the
import independently of the distribution.

⚑⚑ THE WHOLE SURFACE IS DECLARED HERE, UNLIKE `bib.pyi`, AND THE REASON IS MEASURED. `stubtest`
in strict mode requires every runtime name to be present: a stub declaring only the three names
this repo reads fails with eleven "not present in stub" errors for names nobody here calls. The
narrowness `bib.pyi` argues for buys silence only with an allowlist, which then has to be
maintained against someone else's edits — a second copy of their interface by another route.

⚑ AND THE MODULE IS A LEAF, WHICH IS WHY DECLARING ALL OF IT IS CHEAP. Its own docstring: *"A
LEAF: pure data + one pure function, no engine imports."* There is no transitive surface to
follow, so the whole of it is eight dicts and four functions.

⚑ `RANK_C` IS THE AUTHORITY ON WHAT A GRADE CAN BE. A consumer must read it rather than restate
it — a local copy goes stale in the direction that reports a NEW rung as an unknown grade, which
is a false finding pointing at correct work.
"""

# The rung ladder: grade name -> rank. Higher is stronger; `broken` is negative.
RANK_C: dict[str, int]

# The remaining ordering tables the module defines. Declared because `stubtest` requires the full
# surface, not because this repo reads them.
BASELINE_C: dict[str, int]
CORRO_C: dict[str, int]
DECISIONS_C: dict[str, int]
GRADE_C: dict[int, str]
ORDER: dict[str, int]
RESOLUTION_C: dict[str, int]
SCOPE_C: dict[str, int]
STRENGTH: dict[str, int]

def rungs(descending: bool = ...) -> list[str]: ...
def below(floor: str) -> list[str]: ...
def clamp(
    records: list[object],
    owner_grades: dict[object, object] | None = ...,
    keys: set[object] | None = ...,
) -> list[object]: ...
def mark_content_sensitive(
    records: list[object], content: set[object]
) -> list[object]: ...
def verify_hop(
    record: dict[object, object],
    premises: dict[object, object],
    owner_grades: dict[object, object] | None = ...,
) -> tuple[object, ...]: ...
