# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Call a dynamically-loaded module's census and narrow its result, at the boundary.

⚑ `getattr` ON A LOADED MODULE RETURNS `Any`, AND `Any` SPREADS. A caller that reached for
a gate's census inline would earn a finding per expression touching it — the same boundary
shape a JSON decode has, and the same remedy: narrow ONCE, here, and hand back a concrete
type.

⚑⚑ AND THE FAILURE MODES STAY APART FROM AN EMPTY CENSUS. A module with no census
attribute, a census that is not callable, one that raises, and one that returns something
that is not a collection are four different facts — and none of them is "clean". Collapsing
any into a bare `set()` would let an unmeasurable gate read as green, which is the
false-green shape this whole family of readers refuses.

⚑ A CENSUS MAY RETURN A DICT, AND ITS KEYS ARE THE CENSUS. One declared gate does exactly
that, so the conversion belongs here rather than in each caller: a caller that forgot would
iterate the dict and get its keys anyway — right by accident, and wrong the day a census
returns something else.

⚑⚑⚑ AND NOT EVERY GATE HAS A `census()` AT ALL. One computes its census as `judge(*scan())`
and takes a field of the result — a two-call chain whose parts were carved out of `main`
precisely so a pre-flight could reuse the exact extraction rather than re-implement it.
`chained_census` reads that shape, because the alternative is a per-gate branch in every
caller, and a second implementation of a gate's predicate is the drift this exists to
prevent.

⚑ THE RUN AND THE VALIDATION ARE SEPARATE FUNCTIONS, and `PLR0911` is why. It fired on a
combined version — the rule this repo records as detecting a VALUE OR JOB NOBODY NAMED
rather than mere arity — and it was right: running a chain and deciding whether its result
is a census are two jobs, and the second is reusable by anything else that indexes a
verdict tuple.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import ModuleType


def _as_keys(result: object, label: str) -> tuple[set[str], str | None]:
    """Narrow a census result to a key set, or say why it is not one."""
    if isinstance(result, (dict, set, frozenset, list, tuple)):
        return {str(k) for k in result}, None
    return set(), f"{label} returned {type(result).__name__}, not a collection"


def _callable_attr(
    module: ModuleType,
    name: str,
    label: str,
) -> tuple[object, str | None]:
    """Return `module.name` when it is callable, or say why it is unusable."""
    found: object = getattr(module, name, None)
    if found is None:
        return None, f"{label} declares no {name}()"
    if not callable(found):
        return None, f"{label}.{name} is not callable"
    return found, None


def text_call(
    module: ModuleType,
    name: str,
    arg: object,
    label: str,
) -> tuple[str, str | None]:
    """Call `module.name(arg)` and narrow its result to TEXT.

    ⚑ THE THIRD BOUNDARY SHAPE, AND CONFLATING IT WITH THE SET ONE IS A REAL BUG. A comment
    masker returns a STRING; running it through the key-set narrower would iterate that
    string into a set of single CHARACTERS — a plausible-looking value that is not the
    answer. The return type is what distinguishes these, so each gets its own boundary.
    """
    found, why = _callable_attr(module, name, label)
    if found is None:
        return "", why
    try:
        result: object = found(arg)  # type: ignore[operator]
    except Exception as exc:  # noqa: BLE001 — a tool's own failure is a REASON, not ours
        return "", f"{label}.{name}() raised {type(exc).__name__}: {exc}"
    if not isinstance(result, str):
        return "", f"{label}.{name}() returned {type(result).__name__}, not text"
    return result, None


def str_set_call(
    module: ModuleType,
    name: str,
    arg: object,
    label: str,
    *,
    niladic: bool = False,
) -> tuple[set[str], str | None]:
    """Call `module.name(arg)` and narrow its result to a set of strings.

    ⚑⚑ THE SECOND BOUNDARY SHAPE, AND IT IS NOT `census_of`. That one calls a NILADIC
    census and owns the whole census question; this calls a SCANNER — a function taking an
    argument and returning names — which a caller composes several of. Folding them
    together would make the census question take an argument it does not have.

    ⚑ NARROWED HERE SO THE CALLER STAYS CLEAN. A caller reaching a scanner off a
    dynamically-loaded module earns an `Any` finding per expression that touches it, which
    is what pushed a first cut of the private census to twenty-six findings without a
    single defect in its logic.

    ⚑⚑ `niladic` IS AN ARITY FLAG, NOT A FOURTH FUNCTION, and passing `None` instead is what
    it prevents. A name-returning function that takes no argument is common — a population
    reader, a roster — and calling it with `None` raises `TypeError`, which this boundary
    dutifully reports as a REASON. That reads as "the tool failed" when the truth is "the
    caller guessed the arity", and a reason that misattributes the fault is worse than none.
    Splitting by arity as well as by return type would give four near-identical functions, so
    the return type keeps its own function and the arity is a flag.
    """
    found, why = _callable_attr(module, name, label)
    if found is None:
        return set(), why
    try:
        if niladic:
            result: object = found()  # type: ignore[operator]
        else:
            result = found(arg)  # type: ignore[operator]
    except Exception as exc:  # noqa: BLE001 — a tool's own failure is a REASON, not ours
        return set(), f"{label}.{name}() raised {type(exc).__name__}: {exc}"
    return _as_keys(result, f"{label}.{name}()")


def field_of(verdict: object, field: int, label: str) -> tuple[set[str], str | None]:
    """Return `verdict[field]` as a key set, or say why it cannot be one.

    ⚑ A WRONG FIELD INDEX REFUSES RATHER THAN RETURNING THE WRONG SET. A tuple of verdicts
    indexed one position off yields a different, plausible-looking census — the shape that
    reads as a measurement and is not one.
    """
    if not isinstance(verdict, tuple):
        return set(), (f"{label} returned {type(verdict).__name__}, not a tuple to index")
    if not 0 <= field < len(verdict):
        return set(), (f"{label} returned {len(verdict)} field(s), so field {field} does not exist")
    return _as_keys(verdict[field], f"{label}[{field}]")


def census_of(module: ModuleType, label: str) -> tuple[set[str], str | None]:
    """Return `(census, None)` from `module.census()`, or `(set(), why)`.

    `label` names the module in any reason returned, so a caller reporting the failure
    does not have to reconstruct which gate it came from.
    """
    found, why = _callable_attr(module, "census", label)
    if found is None:
        return set(), why
    try:
        result: object = found()  # type: ignore[operator]
    except Exception as exc:  # noqa: BLE001 — a gate's own failure is a REASON, not ours
        return set(), f"{label}.census() raised {type(exc).__name__}: {exc}"
    return _as_keys(result, f"{label}.census()")


def _run_chain(
    module: ModuleType,
    first: str,
    second: str,
    label: str,
) -> tuple[object, str | None]:
    """Run `second(*first())` and return its raw result, or say why it did not run.

    ⚑ THE FIRST CALL TAKES NO ARGUMENTS, DELIBERATELY. The gate whose shape this reads
    warns that its scan must run WHOLE-TREE — its uniqueness filter is a global property,
    so scanning a subset and judging it would call every carrier unique. Offering a
    narrowing parameter here would invite exactly that.
    """
    scan, why = _callable_attr(module, first, label)
    if scan is None:
        return None, why
    judge, why = _callable_attr(module, second, label)
    if judge is None:
        return None, why
    try:
        scanned: object = scan()  # type: ignore[operator]
        if not isinstance(scanned, tuple):
            return None, (
                f"{label}.{first}() returned {type(scanned).__name__}, not a tuple to spread"
            )
        verdict: object = judge(*scanned)  # type: ignore[operator]
    except Exception as exc:  # noqa: BLE001 — a gate's own failure is a REASON, not ours
        return None, f"{label}.{second}() raised {type(exc).__name__}: {exc}"
    return verdict, None


def chained_census(
    module: ModuleType,
    first: str,
    second: str,
    field: int,
    label: str,
) -> tuple[set[str], str | None]:
    """Return the census of a gate that computes it as `second(*first())[field]`."""
    verdict, why = _run_chain(module, first, second, label)
    if why is not None:
        return set(), why
    return field_of(verdict, field, f"{label}.{second}()")
