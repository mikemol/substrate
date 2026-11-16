#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.scratch_module` — loading without changing what others can import.

⚑⚑⚑ THE PATH-UNCHANGED CASE IS THE ITEM. Every existing consumer of `scratch/` reaches it with
`sys.path.insert`, which is a PROCESS-WIDE change made to satisfy ONE call. A loader that quietly
did the same would pass every other case here and still be the thing this module exists to avoid,
so the invariant is asserted directly: `sys.path` is identical before and after.

⚑⚑ AND THE THREE FAILURES MUST STAY DISTINCT. Absent, unloadable, and raises-at-import are three
different verdicts for a witness that consults a tool — one is a missing file, one is a broken
module, one is a tool that refuses. Collapsing them into a bare None is the swallowed-reason
defect `gate_module` was rewritten to remove.

⚑ THE FIXTURES CANNOT BE TEMP FILES FOR EVERY ARM, because the loader resolves against the repo
root by construction. The failure arms use names that cannot exist; the success arm uses the real
tool the OBS witness consults, which is also the only honest way to assert it is reachable.
"""

from __future__ import annotations

import sys

from substrate import scratch_module

# The tool the OBS witness consults — the real one, since "is it reachable" is the claim.
_REAL = "tsdbprobe"

# A name no file answers to.
_ABSENT = "no-such-scratch-tool-9d41"

# A tool that imports a DIFFERENT sibling by bare name — the case self-registration misses.
_SIBLING_IMPORTER = "bibstruct"


def a_real_tool_loads(out: list[str]) -> int:
    """Check the loader reaches an existing scratch tool."""
    found, why = scratch_module.scratch_module(_REAL)
    if found is None:
        out.append(f"selftest: {_REAL} did not load: {why!r}")
        return 1
    return 0


def a_loaded_tool_carries_no_reason(out: list[str]) -> int:
    """Check success reports no failure reason.

    ⚑ A REASON BESIDE A MODULE reads as a warning about a working load, which trains a caller to
    ignore the field on the rows where it matters.
    """
    found, why = scratch_module.scratch_module(_REAL)
    if found is not None and why is not None:
        out.append(f"selftest: a loaded tool carries a reason: {why!r}")
        return 1
    return 0


def loading_does_not_touch_sys_path(out: list[str]) -> int:
    """Check the import path is unchanged — THE WHOLE POINT.

    ⚑⚑⚑ THE DEFECT THIS MODULE REPLACES, ASSERTED RATHER THAN DESCRIBED. Five consumers reach
    `scratch/` by mutating `sys.path`; a loader doing that invisibly would satisfy every other
    arm in this file. Only comparing the list before and after can tell the two apart.
    """
    before = list(sys.path)
    scratch_module.scratch_module(_REAL)
    if sys.path != before:
        added = [p for p in sys.path if p not in before]
        out.append(f"selftest: loading changed sys.path, adding {added!r}")
        return 1
    return 0


def an_absent_tool_reports_its_path(out: list[str]) -> int:
    """Check a missing tool names where it was looked for.

    ⚑ A READER CHASING THIS NEEDS THE PATH, not the fact of absence. "no tool at scratch/x.py" is
    actionable; "not found" sends them to guess which directory was searched.
    """
    found, why = scratch_module.scratch_module(_ABSENT)
    if found is not None:
        out.append(f"selftest: an absent tool loaded: {found!r}")
        return 1
    if why is None or scratch_module.SCRATCH_DIR not in why:
        out.append(f"selftest: the absence does not name the directory: {why!r}")
        return 1
    return 0


def an_absent_tool_returns_rather_than_raises(out: list[str]) -> int:
    """Check the failure arrives as data.

    ⚑ A WITNESS CONSULTING A TOOL NEEDS A VERDICT, not a traceback — the caller's job is to report
    UNKNOWN, and it cannot do that from an exception it did not expect.
    """
    try:
        scratch_module.scratch_module(_ABSENT)
    except Exception as exc:  # noqa: BLE001 — the case is that nothing propagates
        out.append(f"selftest: an absent tool raised {type(exc).__name__}: {exc}")
        return 1
    return 0


def the_path_is_derived_from_the_name(out: list[str]) -> int:
    """Check the resolved path is the directory plus the name."""
    got = scratch_module.tool_path(_REAL)
    if got != f"{scratch_module.SCRATCH_DIR}/{_REAL}.py":
        out.append(f"selftest: the tool path resolved to {got!r}")
        return 1
    return 0


def a_dotted_suffix_is_accepted(out: list[str]) -> int:
    """Check a name given with its extension resolves the same way.

    ⚑ A CALLER ARRIVING FROM A TRACEBACK HAS `tsdbprobe.py`; one arriving from source has
    `tsdbprobe`. Two spellings resolving to two paths is how a loader disagrees with itself.
    """
    if scratch_module.tool_path(f"{_REAL}.py") != scratch_module.tool_path(_REAL):
        out.append("selftest: the two spellings resolve to different paths")
        return 1
    return 0


def a_second_load_returns_the_same_object(out: list[str]) -> int:
    """Check the tool is not executed twice under one name.

    ⚑⚑ TWO MODULE OBJECTS FOR ONE TOOL differ only in which one holds the state a later reader
    consults — a divergence that appears under repeat calls and nowhere else.
    """
    first, _why = scratch_module.scratch_module(_REAL)
    second, _again = scratch_module.scratch_module(_REAL)
    if first is not second:
        out.append("selftest: a second load returned a different module object")
        return 1
    return 0


def the_loaded_tool_carries_its_own_names(out: list[str]) -> int:
    """Check the module really executed rather than loading empty.

    ⚑ AN EMPTY MODULE SATISFIES EVERY ARM ABOVE. Reading a name the tool declares is what
    separates "loaded" from "bound something".
    """
    found, why = scratch_module.scratch_module(_REAL)
    if found is None:
        out.append(f"selftest: {_REAL} did not load: {why!r}")
        return 1
    if not hasattr(found, "DEFAULT_BASE"):
        out.append(f"selftest: the loaded module declares no DEFAULT_BASE: {dir(found)[:8]!r}")
        return 1
    return 0


def a_tool_importing_a_sibling_loads(out: list[str]) -> int:
    """Check a tool that imports a DIFFERENT sibling by bare name resolves.

    ⚑⚑⚑ REGISTERING THE TOOL UNDER ITS OWN STEM COVERS ONLY SELF-REFERENCE, and the first cut
    stopped there while its comment read as though it covered both. MEASURED: `bibstruct` does
    `import vfs` at module scope and failed with `ModuleNotFoundError` — five tools import `vfs`
    that way, so the gap was a whole population, not one file.
    """
    found, why = scratch_module.scratch_module(_SIBLING_IMPORTER)
    if found is None:
        out.append(f"selftest: {_SIBLING_IMPORTER} did not load: {why!r}")
        return 1
    return 0


def the_sibling_finder_refuses_dotted_names(out: list[str]) -> int:
    """Check a package import is left to its real owner.

    ⚑⚑ ANSWERING FOR A DOTTED NAME would put this finder ahead of the actual package for every
    submodule in the process — a global effect from a loader whose whole purpose is avoiding one.

    ⚑ THE CLASS IS NOW THE SHARED ONE, and this case is KEPT rather than deleted as redundant.
    `sibling_finder_selftest` pins the property for the finder itself; this pins that THIS
    LOADER still gets it — a different claim, since a future edit could swap in a permissive
    finder here and leave the other suite green.
    """
    from substrate import sibling_finder  # noqa: PLC0415 — one case's dependency, not the file's

    finder = sibling_finder.SiblingFinder(scratch_module.SCRATCH_DIR)
    if finder.find_spec("os.path") is not None:
        out.append("selftest: the finder answered for a dotted name")
        return 1
    return 0


def the_sibling_finder_is_removed_after_loading(out: list[str]) -> int:
    """Check the meta-path is restored once the load returns.

    ⚑ A FINDER LEFT INSTALLED resolves bare names against the tool directory for the rest of the
    process — the ambient effect this loader exists to avoid, arrived at by another route.
    """
    before = len(sys.meta_path)
    scratch_module.scratch_module(_ABSENT)
    scratch_module.scratch_module(_REAL)
    if len(sys.meta_path) != before:
        out.append(f"selftest: meta_path went {before} -> {len(sys.meta_path)}")
        return 1
    return 0


_ARMS = (
    a_real_tool_loads,
    a_loaded_tool_carries_no_reason,
    loading_does_not_touch_sys_path,
    an_absent_tool_reports_its_path,
    an_absent_tool_returns_rather_than_raises,
    the_path_is_derived_from_the_name,
    a_dotted_suffix_is_accepted,
    a_second_load_returns_the_same_object,
    the_loaded_tool_carries_its_own_names,
    a_tool_importing_a_sibling_loads,
    the_sibling_finder_refuses_dotted_names,
    the_sibling_finder_is_removed_after_loading,
)

_CASE_COUNT = 1 + 1 + 1 + 2 + 1 + 1 + 1 + 1 + 2 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"scratch-module selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"scratch-module selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
