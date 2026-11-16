#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.sole_authority` — bodies decide, names do not.

⚑⚑⚑ THE DELEGATOR CASE IS THE ITEM. A def count reads a one-line wrapper and a full
reimplementation identically, so consolidation — which ADDS a delegator per site — makes the
number go UP as the repair lands. That is how `4 → 5` was once reported as the incident getting
worse when it was the incident closing. The arms below assert the verdict comes from the verdict
column, never from how many definitions exist.

⚑⚑ AND THE HOME EXEMPTION MUST ACTUALLY EXEMPT. The authority necessarily reimplements the
capability, so a comparison that misses it leaves the item permanently one short of closed —
measured live, when the census returned absolute paths and the home was passed repo-relative. An
exemption that silently stops exempting produces a floor no correct work can reach.

⚑ THE FIXTURES ARE FAKE CENSUSES. A case reading the live tree measures today's `agda_files`: it
is sole right now, and a case pinning that would go red the moment someone adds a rival — which
is exactly when the reader needs to keep working rather than being edited.
"""

from __future__ import annotations

import sys

from substrate import corpus, sole_authority

_HOME = "scratch/agda_lex.py"

# A census in the shape the tool returns: the home plus one-line delegators.
_HEALTHY = [
    (f"{corpus.ROOT}/{_HOME}", 652, "REIMPLEMENTS", "", 6),
    (f"{corpus.ROOT}/scratch/claim_census.py", 57, "DELEGATES", "_agda_files", 1),
    (f"{corpus.ROOT}/scratch/paydown.py", 81, "DELEGATES", "_agda_files", 1),
]

# The defect: a second real body beside the home.
_RIVAL = (f"{corpus.ROOT}/scripts/other_gate.py", 40, "REIMPLEMENTS", "", 9)


class _Census:
    """A census returning the rows the case chose."""

    def __init__(self, rows: list[tuple[str, int, str, str, int]] | None = None) -> None:
        self._rows = rows if rows is not None else list(_HEALTHY)
        self.asked: list[str] = []

    def rivals(self, name: str) -> list[tuple[str, int, str, str, int]]:
        """Record the capability asked about and return the fixture rows."""
        self.asked.append(name)
        return self._rows


def _authority_with(
    api: _Census,
    home: str = _HOME,
) -> sole_authority.Authority:
    """Run the reader against a fixture census."""

    def _load() -> tuple[sole_authority.Census | None, str]:
        return api, ""

    original = sole_authority.census
    sole_authority.census = _load
    try:
        return sole_authority.authority("agda_files", home)
    finally:
        sole_authority.census = original


def delegators_are_not_debt(out: list[str]) -> int:
    """Check one-line wrappers do not count against the item — THE WHOLE ITEM.

    ⚑⚑⚑ A SHAPE PREDICATE CANNOT DISTINGUISH THE DEFECT FROM ITS FIX. Counting definitions makes
    a repair look like a regression, which is the reading that kept this item from ever closing.
    """
    got = _authority_with(_Census())
    if not got.sole:
        out.append(f"selftest: delegators counted as debt: {got.debt!r}")
        return 1
    return 0


def the_home_is_exempt(out: list[str]) -> int:
    """Check the authority is not reported as reimplementing.

    ⚑⚑ MEASURED LIVE. The census yields absolute paths; passing the home repo-relative made the
    compare miss and the authority reported ITSELF as debt — an item that cannot close, produced
    by the exemption written to let it close.
    """
    got = _authority_with(_Census())
    named = [row.path for row in got.debt if row.path == sole_authority.relative(_HOME)]
    if named:
        out.append(f"selftest: the home was reported as debt: {named!r}")
        return 1
    return 0


def a_real_rival_is_debt(out: list[str]) -> int:
    """Check a second implementation IS reported — the POSITIVE CONTROL.

    ⚑⚑ WITHOUT THIS, A READER EXEMPTING EVERYTHING passes both cases above and reports every
    capability sole forever. The pair says the exemption is narrow.
    """
    got = _authority_with(_Census([*_HEALTHY, _RIVAL]))
    if got.sole:
        out.append("selftest: a real rival was reported as sole")
        return 1
    if len(got.debt) != 1 or not got.debt[0].path.endswith("other_gate.py"):
        out.append(f"selftest: the debt read as {got.debt!r}")
        return 1
    return 0


def an_absolute_home_is_also_exempt(out: list[str]) -> int:
    """Check the home is exempt whichever spelling the caller used.

    ⚑ TWO SPELLINGS OF ONE PATH is precisely what broke the first cut, so both are pinned rather
    than the one that happened to be fixed.
    """
    got = _authority_with(_Census(), home=f"{corpus.ROOT}/{_HOME}")
    if not got.sole:
        out.append(f"selftest: an absolute home was not exempt: {got.debt!r}")
        return 1
    return 0


def the_rows_are_reported_repo_relative(out: list[str]) -> int:
    """Check rows do not carry the machine's absolute prefix.

    ⚑ AN ABSOLUTE PATH IN A REPORT is unusable to the next reader and differs per machine, which
    makes two runs of one census look like two different findings.
    """
    got = _authority_with(_Census([*_HEALTHY, _RIVAL]))
    absolute = [row.path for row in got.rivals if row.path.startswith("/")]
    if absolute:
        out.append(f"selftest: absolute path(s) in the report: {absolute!r}")
        return 1
    return 0


def the_delegator_count_excludes_reimplementations(out: list[str]) -> int:
    """Check the reported delegator count is the delegating rows.

    ⚑ THE COUNT IS DERIVED FROM THE VERDICT COLUMN, not from `len(rivals) - 1`, which would
    silently include a second reimplementation as though it delegated.
    """
    text = sole_authority.render(_authority_with(_Census()))
    delegating = sum(1 for row in _HEALTHY if row[2] != sole_authority.REIMPLEMENTS)
    if f"{delegating} delegator(s)" not in text:
        out.append(f"selftest: the delegator count reads as {text!r}")
        return 1
    return 0


def the_capability_asked_is_the_one_named(out: list[str]) -> int:
    """Check the census is asked about the requested capability."""
    api = _Census()
    _authority_with(api)
    if api.asked != ["agda_files"]:
        out.append(f"selftest: the census was asked about {api.asked!r}")
        return 1
    return 0


def an_empty_census_is_unmeasured(out: list[str]) -> int:
    """Check no definitions found reports UNMEASURED, not sole.

    ⚑⚑ ZERO DEFINITIONS OF A CAPABILITY THAT EXISTS is a fact about the query, and reading it as
    *"the home is sole"* would close the item on a census that found nothing at all.
    """
    got = _authority_with(_Census([]))
    if got.sole or got.known:
        out.append(f"selftest: an empty census read as {got!r}")
        return 1
    if "UNMEASURED" not in got.why:
        out.append(f"selftest: the empty-census reason reads as {got.why!r}")
        return 1
    return 0


def an_unloadable_census_is_unmeasured(out: list[str]) -> int:
    """Check a missing tool reports its reason rather than a verdict."""
    original = sole_authority.CENSUS
    sole_authority.CENSUS = "no-such-census-2f77"
    try:
        got = sole_authority.authority("agda_files", _HOME)
    finally:
        sole_authority.CENSUS = original
    if got.known:
        out.append(f"selftest: an unloadable census read as measured: {got!r}")
        return 1
    if "will not load" not in got.why:
        out.append(f"selftest: the unloadable reason reads as {got.why!r}")
        return 1
    return 0


def an_unmeasured_verdict_renders_distinctly(out: list[str]) -> int:
    """Check unmeasured cannot be mistaken for the sole reading."""
    text = sole_authority.render(
        sole_authority.Authority(capability="x", rivals=(), home=_HOME, why="no tool")
    )
    if "UNMEASURED" not in text:
        out.append(f"selftest: an unmeasured verdict renders as {text!r}")
        return 1
    return 0


def a_debt_row_names_its_size(out: list[str]) -> int:
    """Check a reported rival says how much body it holds.

    ⚑ A STATEMENT COUNT SEPARATES A STUB FROM A FORK, which is what a reader needs to decide
    whether the repair is a delete or a merge.
    """
    text = sole_authority.render(_authority_with(_Census([*_HEALTHY, _RIVAL])))
    if "statement(s)" not in text:
        out.append(f"selftest: the debt row omits its size:\n{text}")
        return 1
    return 0


def relative_leaves_a_relative_path_alone(out: list[str]) -> int:
    """Check normalising is idempotent.

    ⚑ A NORMALISER THAT ONLY WORKS ONCE turns a second pass into a corruption, and both sides of
    the exemption compare go through this.
    """
    once = sole_authority.relative(f"{corpus.ROOT}/{_HOME}")
    if sole_authority.relative(once) != once:
        out.append(f"selftest: relative is not idempotent: {once!r}")
        return 1
    return 0


_ARMS = (
    delegators_are_not_debt,
    the_home_is_exempt,
    a_real_rival_is_debt,
    an_absolute_home_is_also_exempt,
    the_rows_are_reported_repo_relative,
    the_delegator_count_excludes_reimplementations,
    the_capability_asked_is_the_one_named,
    an_empty_census_is_unmeasured,
    an_unloadable_census_is_unmeasured,
    an_unmeasured_verdict_renders_distinctly,
    a_debt_row_names_its_size,
    relative_leaves_a_relative_path_alone,
)

_CASE_COUNT = 1 + 1 + 2 + 1 + 1 + 1 + 1 + 2 + 2 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"sole-authority selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"sole-authority selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
