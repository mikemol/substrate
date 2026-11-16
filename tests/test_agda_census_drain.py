# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Exercise the ⟡drain-split-census modules against the live tree.

Scenario: the drained census modules answer for the tree they measure

⚑⚑ THIS SUITE LIVES IN `tests/`, NOT BESIDE THE MODULES, AND THAT PLACEMENT IS A MEASURED
CONSTRAINT RATHER THAN A PREFERENCE. `substrate/agda_import_dag.py` and
`substrate/agda_tree_state.py` import `gen_build_makefiles` and `agda_lex` by BARE NAME,
because `stubs/*.pyi` are keyed on the bare module name — a `scripts.gen_build_makefiles`
spelling bypasses the stub and drags mypy into untyped source (MEASURED: 139 findings on a
file that has none under the bare spelling). Those bare names resolve only under the
`pythonpath` this project declares for pytest, so a sibling `*_selftest.py` run as
`python <path> --selftest` raises `ModuleNotFoundError` while the same code passes here.

⚑ THE STUB IS WHAT MAKES THE MODULE CLEAN AND THE PACKAGE IS WHAT WOULD MAKE IT RUNNABLE,
and today only one of those exists. Recording it as a placement rather than papering over
it with a `sys.path` insert is the operator's standing ruling (*"NOO. No sys.path
modification."*) — and the injection would be the thing hiding the debt, not fixing it.

⚑⚑ EVERY CASE CARRIES A DISCRIMINATOR, because a predicate that always says yes passes any
suite built only from positive cases. The freshness predicate earned this: its origin
returned `fresh` for EVERY log twice — once because a hand-built module key missed the DAG
so the dependency walk visited nothing, and once because a bare `except` swallowed every
`getmtime` so `newest` stayed 0.0. Both defects pass a positive case and fail the negative
ones below.

⚑ REPAIRED 2026-10-10 (W335) AGAINST THE MODULES' CURRENT SIGNATURES. This file was written
against an earlier shape and never ran green: `agda_tree_state` exports `MARKER` (imported here
under the name the cases read, `LEAF_MARKER`), `tree_stamp` takes the root it measures, and
`classify` takes a `leaves_of` callable (the leaf counter a consumed-parent verdict needs; none
of these text-only cases reaches it, so the stand-in below answers zero).
"""

from __future__ import annotations

import unittest

from substrate.agda_census_run import build_command, census_jobs_flag
from substrate.agda_error_class import classify, is_other, other_kind
from substrate.agda_import_dag import blast_radius, import_dag, importers_of
from substrate.agda_log_fresh import log_is_fresh
from substrate.agda_tree_state import MARKER as LEAF_MARKER
from substrate.agda_tree_state import tree_stamp

_NOT_IN_DAG = "Nope/NotAModule.agda"
_NOT_IN_SCOPE = "X.agda:1,1-2\nerror: [NotInScope] foo\n"
_UNKNOWN_ERROR = "X.agda:1,1-2\nerror: something with no bracketed kind\n"
_PINNED_WIDTH = 3
_TREE = "."


def _no_leaves(_module: str) -> int:
    """Stand in for the leaf counter: these cases never reach a consumed-parent verdict."""
    return 0


class ImportDagTest(unittest.TestCase):
    """The DAG is parsed once, inverted consistently, and honest about a stranger."""

    def test_dag_is_populated_and_inverted(self) -> None:
        """`src_to_mod` inverts `disk` and `rdeps` reverses `deps`, with no gaps."""
        disk, deps, rdeps, src_to_mod = import_dag()
        assert disk, "the import DAG is empty"
        for module, rel in disk.items():
            assert src_to_mod[rel] == module
        for module, imports in deps.items():
            for imported in imports:
                assert module in rdeps.get(imported, set())

    def test_dag_is_memoised_not_reparsed(self) -> None:
        """A second call returns the SAME objects — equality would pass against a re-parse."""
        first = import_dag()
        second = import_dag()
        assert first[0] is second[0]
        assert first[1] is second[1]

    def test_cone_excludes_its_own_seed(self) -> None:
        """`blast_radius` returns IMPORTERS, so a seed never reports itself."""
        disk, _deps, _rdeps, _s2m = import_dag()
        sample = next(iter(disk.values()))
        assert sample not in blast_radius([sample])

    def test_unknown_seed_reaches_nothing(self) -> None:
        """DISCRIMINATOR: a path outside the DAG contributes no cone, rather than all of it."""
        assert blast_radius([_NOT_IN_DAG]) == set()
        assert importers_of(_NOT_IN_DAG) == []


class LogFreshnessTest(unittest.TestCase):
    """Freshness withholds its verdict rather than guessing in the optimistic direction."""

    def test_unknown_path_is_never_fresh(self) -> None:
        """DISCRIMINATOR: both historical defects made this case return True."""
        fresh, log, why = log_is_fresh(_NOT_IN_DAG)
        assert fresh is False
        assert log is None
        assert "why" in why

    def test_both_source_spellings_agree(self) -> None:
        """The `agda/` prefix is stripped, so a caller's spelling cannot change the verdict."""
        disk, _deps, _rdeps, _s2m = import_dag()
        sample = next(iter(disk.values()))
        assert log_is_fresh(sample)[0] == log_is_fresh(f"agda/{sample}")[0]


class ErrorClassTest(unittest.TestCase):
    """The kind vocabulary partitions `other` without breaking a consumer that tests it."""

    def test_empty_text_is_clean(self) -> None:
        """No error text means no error, and no remedy is invented for it."""
        assert classify("", _no_leaves) == ("clean", "", None)

    def test_bracketed_kind_becomes_the_tiebreak_suffix(self) -> None:
        """The compiler's own error class rides through as `other:<Kind>`, with a trace."""
        trace: list[str] = []
        kind, detail, _remedy = classify(_NOT_IN_SCOPE, _no_leaves, trace)
        assert kind == "other:NotInScope"
        assert "NotInScope" in detail
        assert trace, "the classifier must be able to show its work"
        assert other_kind(kind) == "NotInScope"

    def test_unbracketed_error_stays_bare_other(self) -> None:
        """An unrecognised shape is NOT given an invented class."""
        assert classify(_UNKNOWN_ERROR, _no_leaves)[0] == "other"

    def test_other_membership_refuses_clean(self) -> None:
        """DISCRIMINATOR: a predicate that always says yes fails exactly here."""
        assert is_other("other")
        assert is_other("other:NotInScope")
        assert not is_other("clean")
        assert other_kind("clean") is None


class TreeStateTest(unittest.TestCase):
    """The stamp is comparable, and the job width has exactly one authority."""

    def test_stamp_is_count_and_mtime(self) -> None:
        """A stamp is `<count>:<mtime>` and is stable while the tree holds still."""
        stamp = tree_stamp(_TREE)
        assert stamp.count(":") == 1
        assert stamp.split(":")[0].isdigit()
        assert stamp == tree_stamp(_TREE)

    def test_leaf_marker_is_the_existing_convention(self) -> None:
        """The marker is `split_lemmas`' own stamp, never a private twin."""
        assert LEAF_MARKER == "⟡cap-128-forcing"

    def test_explicit_width_wins_over_the_authority(self) -> None:
        """DISCRIMINATOR: a caller who names a width must get it, not the default."""
        assert census_jobs_flag(_PINNED_WIDTH) == [f"-j{_PINNED_WIDTH}"]
        assert census_jobs_flag(), "the authority produced no default job flag"

    def test_build_keeps_going_after_a_failure(self) -> None:
        """`-k` is what makes the error list a WORKLIST rather than a single item."""
        command = build_command("agda")
        assert "-k" in command
        assert "agda" in command


if __name__ == "__main__":
    unittest.main()
