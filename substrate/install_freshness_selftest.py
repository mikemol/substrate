#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.install_freshness` — above all, that an absent tool is REFUSED.

⚑⚑⚑ THE ROSTER THE ARMS PROBE IS PLANTED, NOT THE LIVE ONE. A case asserting `shellcheck` is
absent would be green on this host and red on the next, and neither reading would be about the
reader — it would be about the host. Every arm below hands `tools()` a roster it wrote itself,
naming a module that certainly exists (`json`), a binary that certainly exists (`python3`, the
one running the suite), and a name that certainly does not. So the arms measure the RESOLVER,
and the host's actual tool set is the live census's business (`--binaries`), never a case's.

⚑⚑ AND THE TWO KINDS ARE ASSERTED APART, because conflating them is the false-PRESENT this
mode exists to refuse: a MODULE tool is asked of the interpreter and a PATH hit must NOT
satisfy it. The arm plants a name that IS on PATH and IS NOT importable, and asserts the
resolver says absent for the module kind.

⚑ THE LIVE CENSUS IS RUN ONCE, and only for the property no planted roster can carry: that the
declared `REQUIRED` roster parses, that every entry names its kind from the two declared, and
that the rendering prints the denominator whether or not anything is missing.
"""

from __future__ import annotations

import sys

from substrate import install_freshness as fresh

# A module every interpreter has, a binary every host running this has, and a name nothing has.
_MODULE_PRESENT = "json"
_BINARY_PRESENT = "python3"
_ABSENT = "no-such-tool-anywhere-7f3a"

# A binary that is on PATH and is NOT an importable module — the conflation probe.
_PATH_NOT_MODULE = "python3"

# How many arms the planted roster carries.
_PLANTED = 3


def a_present_module_resolves_to_its_origin(out: list[str]) -> int:
    """Check a MODULE tool that imports is reported with where it imports from."""
    found = fresh.locate(_MODULE_PRESENT, fresh.MODULE)
    if not found:
        out.append(f"selftest: importable module {_MODULE_PRESENT!r} read as absent")
        return 1
    return 0


def a_present_binary_resolves_on_path(out: list[str]) -> int:
    """Check a BINARY tool on PATH is reported with its path."""
    found = fresh.locate(_BINARY_PRESENT, fresh.BINARY)
    if not found:
        out.append(f"selftest: PATH binary {_BINARY_PRESENT!r} read as absent")
        return 1
    return 0


def an_absent_name_is_absent_for_both_kinds(out: list[str]) -> int:
    """Check a name nothing has is absent whichever way it is asked for."""
    bad = 0
    if fresh.locate(_ABSENT, fresh.MODULE):
        out.append(f"selftest: {_ABSENT!r} read as an importable module")
        bad += 1
    if fresh.locate(_ABSENT, fresh.BINARY):
        out.append(f"selftest: {_ABSENT!r} read as a PATH binary")
        bad += 1
    return bad


def a_path_hit_does_not_satisfy_a_module_tool(out: list[str]) -> int:
    """Check the two kinds are not conflated — THE ARM THIS MODE EXISTS FOR.

    ⚑⚑ `python3` is on PATH and is not `import python3`. A resolver that fell back to PATH
    for a MODULE tool would read it present, which is the false green of a system `ruff`
    satisfying a gate that runs `python -m ruff` in the venv.
    """
    if fresh.locate(_PATH_NOT_MODULE, fresh.MODULE):
        out.append(f"selftest: PATH binary {_PATH_NOT_MODULE!r} satisfied a MODULE lookup")
        return 1
    return 0


def the_census_refuses_on_one_absence(out: list[str]) -> int:
    """Check a planted roster with one absent tool reads as not-all-present."""
    roster = (
        (_MODULE_PRESENT, fresh.MODULE, "planted"),
        (_BINARY_PRESENT, fresh.BINARY, "planted"),
        (_ABSENT, fresh.BINARY, "planted"),
    )
    found = fresh.tools(roster)
    if len(found) != _PLANTED:
        out.append(f"selftest: {len(found)} tool(s) for a {_PLANTED}-entry roster")
        return 1
    if all(tool.present for tool in found):
        out.append("selftest: a roster with an absent tool read as all present")
        return 1
    if sum(1 for tool in found if not tool.present) != 1:
        out.append("selftest: the wrong number of tools read absent")
        return 1
    return 0


def the_rendering_names_the_denominator_and_the_absence(out: list[str]) -> int:
    """Check the rendering carries N-of-M and names what the absent tool starves."""
    roster = (
        (_MODULE_PRESENT, fresh.MODULE, "planted"),
        (_ABSENT, fresh.BINARY, "the-family-it-starves"),
    )
    text = fresh.render_tools(fresh.tools(roster))
    bad = 0
    if "1 of 2" not in text:
        out.append(f"selftest: the rendering dropped its denominator: {text!r}")
        bad += 1
    if "ABSENT" not in text or "the-family-it-starves" not in text:
        out.append("selftest: the absence or what it starves is not named")
        bad += 1
    return bad


def a_clean_census_still_prints_its_denominator(out: list[str]) -> int:
    """Check a roster with nothing absent prints N rather than silence.

    ⚑ A bare clean line cannot distinguish a total census from one that read nothing.
    """
    roster = ((_MODULE_PRESENT, fresh.MODULE, "planted"),)
    text = fresh.render_tools(fresh.tools(roster))
    if "all 1 required" not in text:
        out.append(f"selftest: a clean census hid its denominator: {text!r}")
        return 1
    return 0


def a_tree_script_resolves_only_when_executable(out: list[str]) -> int:
    """Check the SCRIPT kind asks the tree, and asks for the exe bit — not mere existence.

    ⚑ `membudget` first landed as a BINARY and read ABSENT on a host where it sits in
    `scripts/`: a roster defect, not a host fact. This arm plants a script that exists without
    an exe bit and asserts it reads absent, and one with the bit and asserts it reads present.
    """
    bad = 0
    import stat  # noqa: PLC0415 - one arm needs it, nothing else here does
    import tempfile  # noqa: PLC0415
    from pathlib import Path  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as where:
        inert = Path(where) / "inert"
        inert.write_text("#!/bin/sh\n", encoding="utf-8")
        live = Path(where) / "live"
        live.write_text("#!/bin/sh\n", encoding="utf-8")
        live.chmod(live.stat().st_mode | stat.S_IXUSR)
        if fresh._runnable(inert):  # noqa: SLF001 - the predicate IS the subject
            out.append("selftest: a script with no exe bit read as runnable")
            bad += 1
        if not fresh._runnable(live):  # noqa: SLF001
            out.append("selftest: an executable script read as not runnable")
            bad += 1
    return bad


def the_declared_roster_is_well_formed(out: list[str]) -> int:
    """Check every live entry names one of the three declared kinds — the one live-roster arm."""
    kinds = {fresh.MODULE, fresh.BINARY, fresh.SCRIPT}
    bad = 0
    for name, kind, needed_by in fresh.REQUIRED:
        if kind not in kinds:
            out.append(f"selftest: {name!r} declares an unknown kind {kind!r}")
            bad += 1
        if not needed_by:
            out.append(f"selftest: {name!r} names nothing it is needed by")
            bad += 1
    return bad


_ARMS = (
    a_present_module_resolves_to_its_origin,
    a_present_binary_resolves_on_path,
    an_absent_name_is_absent_for_both_kinds,
    a_path_hit_does_not_satisfy_a_module_tool,
    the_census_refuses_on_one_absence,
    the_rendering_names_the_denominator_and_the_absence,
    a_clean_census_still_prints_its_denominator,
    a_tree_script_resolves_only_when_executable,
    the_declared_roster_is_well_formed,
)

_CASE_COUNT = 1 + 1 + 2 + 1 + 3 + 2 + 1 + 2 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"install-freshness selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"install-freshness selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
