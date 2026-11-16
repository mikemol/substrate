# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.agda_files` — the promoted enumeration authority.

⚑⚑⚑ THE LOAD-BEARING CASES ARE DIFFERENTIAL, AND THAT IS WHAT A PROMOTION OWES. Every other
kind of case asserts what I believe the behaviour SHOULD be; a differential case asserts the
behaviour is **the origin's**, which is a different claim and the only one that makes a
promotion safe. The origin has many consumers across the tree, so a promotion that changes
behaviour is a rewrite wearing a move's clothes — and the port is not even a transcription:
the per-file gate refused `os.path` and a positional boolean, so the walk was rebuilt on
`Path` and the flag made keyword-only. **A rebuilt body agreeing with my reading of its
docstring proves nothing; agreeing with the origin on the live tree proves the port.**

⚑⚑ THE ORIGIN IS LOADED BY LOCATION, NOT IMPORTED, AND THAT IS FORCED. Importing `agda_lex`
by leaf name is exactly the `sys.path` surgery this promotion exists to remove — a
differential test that required the defect it verifies the fix for. It is also why the
comparison runs against `scratch/` rather than a fixture: a fixture would only prove the new
predicate agrees with itself.

⚑⚑⚑ AND A DYNAMICALLY LOADED MODULE IS `Any`, WHICH WOULD MAKE THE DIFFERENTIAL WORTHLESS.
Every read off it type-checks against nothing, so a misspelled attribute passes and the
comparison agrees with anything — the hazard `climode_selftest` recorded when it promoted its
own origin. `_Origin` is the Protocol that gives the loaded module a shape, which both
satisfies the strict bar and makes the differential's REACH explicit.

⚑⚑ AND THE PROTOCOL DECLARES THE DEFAULT ARITY ONLY, WHICH BOUNDS THIS SUITE HONESTLY. The
origin takes its build flag POSITIONALLY, and a Protocol declaring that draws the same
`FBT001` the port was rewritten to avoid — so the differential covers the default walk, which
is what every consumer in the tree calls, and the `include_build` direction is asserted
against the PORT's own contract below rather than against the origin. **Stating that gap is
the point: a suite claiming a reach it does not have is worse than a narrower one.**

⚑ AND THE ORIGIN MAY BE ABSENT. A borrowing checkout installs the package without `scratch/`,
so the differential arms REPORT that they could not run rather than passing silently — a
skipped comparison that reads as a pass is the census-green shape, and it would make this
file useless in exactly the tree where the port matters most.

⚑ THE CACHE IS ASSERTED BY EQUALITY OF CONTENT AND NON-IDENTITY OF OBJECT. Its whole contract
is that a second call is cheap AND that a caller cannot corrupt a later one, so equality
alone passes against a module handing out its cached list.
"""

from __future__ import annotations

import importlib.util
import sys
from typing import Protocol

from substrate import agda_files, corpus

# The origin this module promotes. Absent in a borrowing checkout, which the arms report.
_ORIGIN = corpus.ROOT / "scratch" / "agda_lex.py"

# A root that exists in every checkout and holds Agda sources.
_ROOT = "agda"

# A root nothing provides, so the walk has a negative control.
_ABSENT = "no_such_tree_at_all"


class _Origin(Protocol):
    """The one call this suite differences against.

    ⚑ NARROW BY DESIGN. A Protocol naming the whole origin would claim this suite verifies
    more than it does; naming one call states the differential's REACH exactly.
    """

    def agda_files(self, root: str, /) -> list[str]:
        """Enumerate the origin's way, at the arity every tree consumer uses."""
        ...


def _origin() -> _Origin | None:
    """Load the origin by LOCATION, or report that it is not here.

    ⚑ BY LOCATION BECAUSE A LEAF-NAME IMPORT IS THE DEFECT UNDER REPAIR. `agda_lex` resolves
    only under a `sys.path` insert into `scratch/`, so importing it normally would make this
    suite depend on the very thing the promotion removes.
    """
    if not _ORIGIN.exists():
        return None
    spec = importlib.util.spec_from_file_location("_agda_lex_origin", _ORIGIN)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the port agrees with the authority it promotes ───────────────────────
    origin = _origin()
    if origin is None:
        check("the origin is present to difference against", passed=False)
    else:
        # ⚑⚑⚑ THE ARM THE PROMOTION EXISTS FOR. Both readers walk the LIVE tree and must
        # return the same population in the same order — the port rebuilt the walk on a
        # different library, so agreement is a measurement rather than a restatement.
        mine = agda_files.agda_files(_ROOT)
        theirs = origin.agda_files(_ROOT)
        check("the port enumerates exactly what the origin does", passed=mine == theirs)
        # ⚑ AND THE POPULATION IS NON-EMPTY, so the agreement above is not two empty lists
        # agreeing. A differential that both sides answer with nothing asserts nothing.
        check("and the population it agrees on is non-empty", passed=bool(mine))

    # ── the build filter is real, and asserted in the direction that matters ──
    # ⚑ THE GUARD MUST EXCLUDE, so the case asserts a pruned walk is a SUBSET of an unpruned
    # one and that every member is a source. Asserting only the default would pass against a
    # filter that never fires. ⚑ This is the PORT's contract, not a difference — the
    # docstring says why the origin cannot be asked at this arity.
    pruned = agda_files.agda_files(_ROOT)
    whole = agda_files.agda_files(_ROOT, include_build=True)
    check("pruning the build tree never invents a path", passed=set(pruned) <= set(whole))
    check(
        "every returned path is an Agda source",
        passed=all(path.endswith(agda_files.SUFFIX) for path in pruned),
    )

    # ── the walk is honest about a root nothing provides ─────────────────────
    # ⚑ THE NEGATIVE CONTROL. A reader returning everything for any root passes every arm
    # above, and this is the one it fails.
    check(
        "a root that does not exist enumerates nothing", passed=agda_files.agda_files(_ABSENT) == []
    )

    # ── the order is an ORDER, not today's membership ────────────────────────
    # ⚑ PINNING TODAY'S MEMBERS WOULD GO RED THE MOMENT A MODULE LANDS, reporting ordinary
    # work as a defect. What survives every tree state is that the result is sorted.
    check("the result is sorted", passed=pruned == sorted(pruned))

    # ── the cache returns a COPY, on BOTH return paths ───────────────────────
    # ⚑⚑ EQUALITY ALONE PASSES AGAINST A MODULE HANDING OUT ITS CACHED LIST, which is the
    # defect the origin's own comment records: a caller mutating what it got back would
    # corrupt every later consumer. So identity is asserted, not just content.
    first = agda_files.agda_files(_ROOT)
    second = agda_files.agda_files(_ROOT)
    check("a second call returns an equal list", passed=first == second)
    check(
        "and not the same object, so a caller cannot corrupt the cache", passed=first is not second
    )
    first.append("mutated-by-a-caller")
    check(
        "mutating a returned list does not reach the next caller",
        passed="mutated-by-a-caller" not in agda_files.agda_files(_ROOT),
    )

    # ⚑⚑⚑ AND THE COLD PATH IS ASSERTED SEPARATELY, BECAUSE THE ARMS ABOVE WERE BLIND TO IT.
    # MEASURED: removing `list(...)` from the cache-MISS return left all three passing, and
    # only removing it from the cache-HIT return failed them. The function has TWO returns and
    # the first caller for a given key takes the one those arms never reach — a guard tested
    # only on the warm path, which is the shape a passing suite hides best. This arm uses a
    # root no earlier case has cached, so it exercises the miss.
    cold = agda_files.agda_files(f"{_ROOT}/Substrate")
    cold.append("mutated-on-the-cold-path")
    check(
        "the cache-MISS return is a copy too",
        passed="mutated-on-the-cold-path" not in agda_files.agda_files(f"{_ROOT}/Substrate"),
    )

    return out


def selftest() -> bool:
    """Report whether every case passed, printing the failures."""
    cases = _cases()
    ok = sum(1 for _label, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"agda_files selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(0 if selftest() else 1)
