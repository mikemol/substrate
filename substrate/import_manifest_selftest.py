#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.import_manifest` — a count over three remedies is not a report.

⚑⚑⚑ THE GROUPING CASE IS THE ITEM. The origin returned one number for the unaccounted imports,
and the live population holds at least three different remedies inside it: a module that ships
inside another interpreter and CANNOT be declared, an optional dependency that should be, and a
first-party name the classifier could not resolve. A reader given one total cannot tell which
they have, so the arms below pin that the verdicts stay separated.

⚑⚑ AND UNMEASURED MUST NOT READ AS CLEAN. A classifier that will not load means the census did
not happen; returning an empty population there would report every import accounted for at the
exact moment nothing was checked — the false green this whole family refuses.

⚑ THE FIXTURES ARE FAKE CLASSIFIERS. A case reading the live corpus measures today's dependency
state: it would go red the moment someone installs `scipy`, reporting correct work as a defect,
and its count is SCOPE-DEPENDENT besides — the CLI census reports 15 where a default-scope call
reports 13, because the two resolve `applied_grammar` and `jea` differently. Pinning either
number would pin a denominator this reader does not own.
"""

from __future__ import annotations

import sys

from substrate import import_manifest

# A classifier row for each verdict the tool can return.
_ROWS = [
    ("os", "STDLIB", 570, "scripts/x.py"),
    ("numpy", "DECLARED", 230, "jea/y.py"),
    ("agda_lex", "FIRST-PARTY", 96, "scratch/z.py"),
    ("eliza", "VENDORED", 538, "scratch/eliza/a.py"),
    ("libcst", "UNDECLARED", 29, "jea/b.py"),
    ("scipy", "MISSING", 5, "scratch/c.py"),
]

# ⚑ DERIVED FROM THE FIXTURE, NEVER TYPED. A literal count here would break when a row is added
# to `_ROWS` for an unrelated arm — an assertion about the fixture wearing the clothes of one
# about the reader.
_OWED = sum(1 for row in _ROWS if row[1] in import_manifest.UNACCOUNTED)


class _Classifier:
    """A classifier returning rows the case chose."""

    def __init__(self, rows: list[tuple[str, str, int, str]] | None = None) -> None:
        self._rows = rows if rows is not None else list(_ROWS)

    def imports(self) -> list[tuple[str, str, int, str]]:
        """Return the fixture rows."""
        return self._rows


def _population_with(
    api: _Classifier,
) -> tuple[tuple[import_manifest.Unaccounted, ...], str]:
    """Run the reader against a fixture classifier."""

    def _load() -> tuple[import_manifest.Classifier | None, str]:
        return api, ""

    original = import_manifest.classifier
    import_manifest.classifier = _load
    try:
        return import_manifest.population()
    finally:
        import_manifest.classifier = original


def both_unaccounted_verdicts_are_kept(out: list[str]) -> int:
    """Check UNDECLARED and MISSING both count as unaccounted.

    ⚑⚑ TWO VERDICTS, BOTH OWED. `UNDECLARED` works today and breaks on a fresh clone; `MISSING`
    does not import at all. A reader keeping only one would report a clean manifest while the
    other kind accumulated.
    """
    rows, why = _population_with(_Classifier())
    if why:
        out.append(f"selftest: the fixture census reported unmeasured: {why!r}")
        return 1
    verdicts = {row.verdict for row in rows}
    if verdicts != set(import_manifest.UNACCOUNTED):
        out.append(f"selftest: the unaccounted verdicts read as {verdicts!r}")
        return 1
    return 0


def the_accounted_verdicts_are_dropped(out: list[str]) -> int:
    """Check the four healthy verdicts are not reported as findings.

    ⚑ THE POSITIVE CONTROL FOR THE FILTER. A reader keeping everything would satisfy the case
    above and report the whole corpus as findings.
    """
    rows, _why = _population_with(_Classifier())
    leaked = [row.module for row in rows if row.verdict not in import_manifest.UNACCOUNTED]
    if leaked:
        out.append(f"selftest: accounted imports leaked into the findings: {leaked!r}")
        return 1
    if len(rows) != _OWED:
        out.append(f"selftest: the fixture yielded {len(rows)} finding(s), expected {_OWED}")
        return 1
    return 0


def the_grouping_separates_the_verdicts(out: list[str]) -> int:
    """Check the report splits by verdict rather than totalling.

    ⚑⚑⚑ THE WHOLE ITEM. One number over several remedies tells an operator to do nothing in
    particular; the grouping is what makes each row actionable.
    """
    rows, _why = _population_with(_Classifier())
    groups = import_manifest.by_verdict(rows)
    if set(groups) != set(import_manifest.UNACCOUNTED):
        out.append(f"selftest: the grouping produced {sorted(groups)!r}")
        return 1
    if any(not found for found in groups.values()):
        out.append(f"selftest: a group came back empty: {groups!r}")
        return 1
    return 0


def the_grouping_loses_no_row(out: list[str]) -> int:
    """Check every finding lands in exactly one group.

    ⚑ A GROUPING THAT DROPS A ROW under-counts its own population — and the total is the one
    figure a reader is most likely to quote onward.
    """
    rows, _why = _population_with(_Classifier())
    groups = import_manifest.by_verdict(rows)
    total = sum(len(found) for found in groups.values())
    if total != len(rows):
        out.append(f"selftest: grouping {len(rows)} row(s) yielded {total}")
        return 1
    return 0


def a_clean_corpus_reports_no_findings(out: list[str]) -> int:
    """Check a fully accounted corpus yields nothing."""
    healthy = [row for row in _ROWS if row[1] not in import_manifest.UNACCOUNTED]
    rows, why = _population_with(_Classifier(healthy))
    if rows != () or why:
        out.append(f"selftest: a clean corpus yielded {rows!r}, {why!r}")
        return 1
    return 0


def a_clean_corpus_renders_as_accounted(out: list[str]) -> int:
    """Check zero findings renders as the closed reading, not as silence."""
    text = import_manifest.render(())
    if "accounted for" not in text:
        out.append(f"selftest: a clean census renders as {text!r}")
        return 1
    return 0


def an_unloadable_classifier_is_unmeasured(out: list[str]) -> int:
    """Check a missing tool reports unmeasured rather than clean.

    ⚑⚑ THE FALSE GREEN. An empty population from a census that never ran is indistinguishable
    from a healthy corpus unless the reason is carried alongside it.
    """
    original = import_manifest.CLASSIFIER
    import_manifest.CLASSIFIER = "no-such-classifier-4c19"
    try:
        rows, why = import_manifest.population()
    finally:
        import_manifest.CLASSIFIER = original
    if rows != ():
        out.append(f"selftest: an unloadable classifier yielded rows: {rows!r}")
        return 1
    if not why or "will not load" not in why:
        out.append(f"selftest: the unmeasured reason reads as {why!r}")
        return 1
    return 0


def an_unmeasured_census_renders_as_unmeasured(out: list[str]) -> int:
    """Check the rendered unmeasured row cannot be read as a clean one."""
    text = import_manifest.render((), "pycodemod will not load: no tool at scratch/x.py")
    if "UNMEASURED" not in text:
        out.append(f"selftest: an unmeasured census renders as {text!r}")
        return 1
    if "accounted for" in text:
        out.append(f"selftest: an unmeasured census reads as clean: {text!r}")
        return 1
    return 0


def a_finding_carries_its_witness(out: list[str]) -> int:
    """Check each row names a file, not only a module.

    ⚑ A MODULE NAME ALONE IS NOT ACTIONABLE — the reader needs somewhere to look, and the
    classifier already supplies one.
    """
    rows, _why = _population_with(_Classifier())
    bare = [row.module for row in rows if not row.example or row.files < 1]
    if bare:
        out.append(f"selftest: finding(s) with no witness: {bare!r}")
        return 1
    return 0


def the_render_names_each_verdict(out: list[str]) -> int:
    """Check the rendered report labels its groups."""
    rows, _why = _population_with(_Classifier())
    text = import_manifest.render(rows)
    missing = [verdict for verdict in import_manifest.UNACCOUNTED if verdict not in text]
    if missing:
        out.append(f"selftest: the render omits verdict label(s): {missing!r}")
        return 1
    return 0


_ARMS = (
    both_unaccounted_verdicts_are_kept,
    the_accounted_verdicts_are_dropped,
    the_grouping_separates_the_verdicts,
    the_grouping_loses_no_row,
    a_clean_corpus_reports_no_findings,
    a_clean_corpus_renders_as_accounted,
    an_unloadable_classifier_is_unmeasured,
    an_unmeasured_census_renders_as_unmeasured,
    a_finding_carries_its_witness,
    the_render_names_each_verdict,
)

_CASE_COUNT = 2 + 2 + 2 + 1 + 1 + 1 + 2 + 2 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"import-manifest selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"import-manifest selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
