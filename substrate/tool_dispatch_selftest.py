#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.tool_dispatch` — a false ACCEPT invents a mode.

⚑⚑⚑ THE ASYMMETRY IS THE DESIGN, AND EVERY ARM HERE DEFENDS ONE SIDE OF IT. Missing an accepted
flag under-reports a tool's modes — a gap someone can see. Inventing one puts a flag in the
census that the tool REJECTS, and a reader who then "documents" it is documenting a capability
that does not exist. The origin records three separate incidents of the second kind and none of
the first, which is why the guards outnumber the readers.

⚑⚑ AND THE ARGV ANCHOR WAS FOUND BY DOGFOODING, NOT BY DESIGN. Every tool in the corpus
dispatches as `if "--x" in sys.argv`, so a literal test for that expression looked total — until
the census ran against its own tool, which binds `args = argv[1:]` then `flag = args[0]` then
compares `flag == "--find"`, and reported `--find` as UNBACKED. An arm below drives exactly that
chain, because a one-pass alias walk passes every other case here.

⚑ PARITY AGAINST THE ORIGIN WAS MEASURED FIRST — **435 tools, 0 disagreements** on both the
accepted and the literal sets. These arms guard the PROPERTIES; that run guarded the
TRANSCRIPTION, and only the first survives the origin's retirement.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import tool_dispatch

# The live dispatch shape every tool in the corpus uses.
_IN_ARGV = 'import sys\nif "--alpha" in sys.argv:\n    run()\n'

# The chain that defeated a one-pass alias walk: argv → args → flag.
_ALIASED = (
    "import sys\n"
    "args = sys.argv[1:]\n"
    'flag = args[0] if args else ""\n'
    'if flag == "--beta":\n    run()\n'
)

# argparse registration.
_ARGPARSE = "import argparse\np = argparse.ArgumentParser()\np.add_argument('--gamma')\n"

# This repo's own unknown-flag guard, which takes a collection.
_CHECK_ARGV = 'import ratchet\nratchet.check_argv({"--delta", "--epsilon"})\n'

# A dispatch table: a dict every one of whose keys is a flag.
_TABLE = 'MODES = {"--zeta": run_zeta, "--eta": run_eta}\n'

# ⚑ ANOTHER PROGRAM'S VOCABULARY, quoted inside a subprocess argument list. Reading these as
# modes credited three tools with mypy's, git's and Agda's flags — 55 invented modes.
_FOREIGN = 'import subprocess\nsubprocess.run(["mypy", "--ignore-missing-imports", "--strict"])\n'

# A dict whose keys are not all flags — a lookup table, not a dispatch.
_MIXED_DICT = 'X = {"--theta": 1, "plain": 2}\n'


def _tool(where: str, name: str, body: str) -> Path:
    """Write a fixture tool and return its path."""
    path = Path(where) / name
    path.write_text(body, encoding="utf-8")
    return path


def a_flag_compared_to_argv_is_accepted(out: list[str]) -> int:
    """Check the live dispatch shape is read."""
    with tempfile.TemporaryDirectory() as where:
        got = tool_dispatch.flags_of(_tool(where, "probe.py", _IN_ARGV))
    if "--alpha" not in got.accepted:
        out.append(f"selftest: an argv comparison was not accepted: {sorted(got.accepted)!r}")
        return 1
    return 0


def an_aliased_argv_chain_is_followed(out: list[str]) -> int:
    """Check the alias fixpoint follows argv through two bindings — THE DOGFOOD CASE.

    ⚑⚑ A ONE-PASS WALK PASSES EVERY OTHER ARM HERE AND FAILS THIS ONE. `argv → args → flag` has
    length, and a sweep in source order catches only its first link — which is how the census
    reported its own tool's `--find` as a mode nothing backs.
    """
    with tempfile.TemporaryDirectory() as where:
        got = tool_dispatch.flags_of(_tool(where, "probe.py", _ALIASED))
    if "--beta" not in got.accepted:
        out.append(f"selftest: an aliased argv chain was not followed: {sorted(got.accepted)!r}")
        return 1
    return 0


def argparse_registration_is_accepted(out: list[str]) -> int:
    """Check `add_argument` registers a flag."""
    with tempfile.TemporaryDirectory() as where:
        got = tool_dispatch.flags_of(_tool(where, "probe.py", _ARGPARSE))
    if "--gamma" not in got.accepted:
        out.append(f"selftest: argparse registration was missed: {sorted(got.accepted)!r}")
        return 1
    return 0


def the_repo_guard_is_read(out: list[str]) -> int:
    """Check `check_argv`'s declared set is accepted.

    ⚑ THE GUARD'S ARGUMENT IS A COLLECTION, not positional flags — a reader that only walked
    `node.args` for constants would find nothing and report every gate's modes as unbacked.
    """
    with tempfile.TemporaryDirectory() as where:
        got = tool_dispatch.flags_of(_tool(where, "probe.py", _CHECK_ARGV))
    if {"--delta", "--epsilon"} - got.accepted:
        out.append(f"selftest: the check_argv set was missed: {sorted(got.accepted)!r}")
        return 1
    return 0


def a_dispatch_table_is_accepted(out: list[str]) -> int:
    """Check an all-flag dict is read as a dispatch."""
    with tempfile.TemporaryDirectory() as where:
        got = tool_dispatch.flags_of(_tool(where, "probe.py", _TABLE))
    if {"--zeta", "--eta"} - got.accepted:
        out.append(f"selftest: a dispatch table was missed: {sorted(got.accepted)!r}")
        return 1
    return 0


def a_mixed_dict_is_not_a_dispatch(out: list[str]) -> int:
    """Check a dict with non-flag keys is not read as a dispatch table.

    ⚑ ALL KEYS OR NONE. A lookup table that happens to contain one flag-shaped key would
    otherwise declare it a mode.
    """
    with tempfile.TemporaryDirectory() as where:
        got = tool_dispatch.flags_of(_tool(where, "probe.py", _MIXED_DICT))
    if "--theta" in got.accepted:
        out.append(f"selftest: a mixed dict was read as a dispatch: {sorted(got.accepted)!r}")
        return 1
    return 0


def a_passed_flag_is_not_accepted(out: list[str]) -> int:
    """Check another program's vocabulary is not read as this tool's — THE 55-MODE INCIDENT.

    ⚑⚑⚑ READING EVERY FLAG-SHAPED LITERAL AS A MODE credited `pycodemod` with mypy's flags,
    `mdstruct` with git's `--porcelain`, and `agda_defs` with the Agda pragma it SEARCHES FOR.
    A false ACCEPT is a bug rather than a caveat, because it puts a capability in the census
    that the tool rejects.
    """
    with tempfile.TemporaryDirectory() as where:
        got = tool_dispatch.flags_of(_tool(where, "probe.py", _FOREIGN))
    if got.accepted:
        out.append(f"selftest: a passed-through flag was accepted: {sorted(got.accepted)!r}")
        return 1
    if "--strict" not in got.literals:
        out.append("selftest: a passed-through flag was not reported as present at all")
        return 1
    return 0


def a_passed_flag_is_still_reported(out: list[str]) -> int:
    """Check the second set carries what the first excludes.

    ⚑ PRESENT BUT NOT ACCEPTED IS A THIRD STATE, and collapsing it into "absent" would lose the
    evidence a reader needs to tell a foreign flag from a missing one.
    """
    with tempfile.TemporaryDirectory() as where:
        got = tool_dispatch.flags_of(_tool(where, "probe.py", _FOREIGN))
    if "--ignore-missing-imports" not in got.passed_through:
        out.append(f"selftest: passed_through read as {sorted(got.passed_through)!r}")
        return 1
    return 0


def an_implementation_half_is_followed(out: list[str]) -> int:
    """Check the one-level hop reaches a decomposed tool's private sibling.

    ⚑ THE BIG TOOLS ARE DECOMPOSED. `pycodemod.py` dispatches out of `_pycodemod_query.py`, so
    reading only the entry module reports nearly every documented mode as unbacked.

    ⚑⚑ THE HALF DISPATCHES INSIDE A FUNCTION, WHICH IS WHAT MAKES IT A HALF. My first fixture
    put the same module-scope `if "--alpha" in sys.argv:` here as everywhere else — and
    `has_entry_point` reads that as one of the two live CLI spellings, so the guard correctly
    refused the hop and the arm failed. The fixture was wrong, not the reader: an implementation
    half is precisely a module that does NOT dispatch at import.
    """
    half = 'import sys\ndef run():\n    return "--alpha" in sys.argv\n'
    with tempfile.TemporaryDirectory() as where:
        _tool(where, "_half.py", half)
        got = tool_dispatch.flags_of(_tool(where, "probe.py", "import _half\n"))
    if "--alpha" not in got.accepted:
        out.append(f"selftest: the implementation half was not followed: {sorted(got.accepted)!r}")
        return 1
    return 0


def a_peer_tool_is_not_followed(out: list[str]) -> int:
    """Check a rostered neighbour's modes are not credited here.

    ⚑⚑ `agda_lex` IMPORTS `agda_defs`, and the hop credited it with all twelve of that tool's
    modes — a NEIGHBOUR's vocabulary reported as this tool's undocumented one.
    """
    with tempfile.TemporaryDirectory() as where:
        _tool(where, "peer.py", _IN_ARGV)
        got = tool_dispatch.flags_of(
            _tool(where, "probe.py", "import peer\n"), frozenset({"peer.py"})
        )
    if "--alpha" in got.accepted:
        out.append(f"selftest: a peer tool's modes were credited: {sorted(got.accepted)!r}")
        return 1
    return 0


def a_shared_cli_utility_is_not_followed(out: list[str]) -> int:
    """Check a same-directory module with its own entry point is not followed.

    ⚑⚑⚑ THE CATEGORY THE PEER GUARD CANNOT SEE. `edit_snapshot.py` is imported by three tools for
    snapshot arming and has its own `--holding`/`--list` dispatch, so the hop reported those as
    three independent undocumented modes on three tools that accept neither — verified by running
    them: both fall through to the usage block, exit 2. Not a peer tool, not an implementation
    half, but a SHARED UTILITY THAT IS ALSO A CLI.
    """
    with tempfile.TemporaryDirectory() as where:
        _tool(where, "util.py", _IN_ARGV + 'if __name__ == "__main__":\n    run()\n')
        got = tool_dispatch.flags_of(_tool(where, "probe.py", "import util\n"))
    if "--alpha" in got.accepted:
        out.append(
            f"selftest: a shared CLI utility's modes were credited: {sorted(got.accepted)!r}"
        )
        return 1
    return 0


def an_unparseable_sibling_does_not_stop_the_read(out: list[str]) -> int:
    """Check a broken import target degrades rather than raising.

    ⚑ A MODULE MID-EDIT IS A STATE THIS READER WILL MEET, and a census that died on one would
    report nothing about the tool that imports it.
    """
    with tempfile.TemporaryDirectory() as where:
        _tool(where, "_broken.py", "def oops(\n")
        got = tool_dispatch.flags_of(_tool(where, "probe.py", "import _broken\n" + _IN_ARGV))
    if "--alpha" not in got.accepted:
        out.append("selftest: an unparseable sibling stopped the read")
        return 1
    return 0


_ARMS = (
    a_flag_compared_to_argv_is_accepted,
    an_aliased_argv_chain_is_followed,
    argparse_registration_is_accepted,
    the_repo_guard_is_read,
    a_dispatch_table_is_accepted,
    a_mixed_dict_is_not_a_dispatch,
    a_passed_flag_is_not_accepted,
    a_passed_flag_is_still_reported,
    an_implementation_half_is_followed,
    a_peer_tool_is_not_followed,
    a_shared_cli_utility_is_not_followed,
    an_unparseable_sibling_does_not_stop_the_read,
)

_CASE_COUNT = 1 + 1 + 1 + 2 + 2 + 1 + 2 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"tool-dispatch selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"tool-dispatch selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
