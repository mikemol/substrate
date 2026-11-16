#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.dag_source` — the required superset is not the debt.

⚑⚑⚑ THE GENERATOR EXEMPTION IS THE ITEM. A source parse is what the BUILD needs — the makefile
generator must emit prerequisites for modules that do not compile yet, edges no core-derived
relation holds — while an analysis consumer asking the same question should query the store. A
verdict lumping the two would prescribe deleting the generator's own input, so the arms below pin
that both are seen and only one is debt.

⚑⚑ AND THE PREDICATE IS A CALL EDGE, NOT A FILE-READING HABIT. A first cut credited a
module-level import regex to every file-touching function and reported NINE derivations where
there are five — including one that counts files and reads mtimes and never looks at an import.
Reading files is not deriving the DAG; scanning import syntax, or calling the parser that does,
is.

⚑ THE FIXTURES ARE SOURCE STRINGS. A case reading the live tree measures today's consumers — five
right now — and would go red the moment one is repointed at the store, reporting the repair as a
defect.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import dag_source

_PARSER = dag_source.PARSER
_RELATION = dag_source.RELATION

# ⚑ THE DEBT: an analysis consumer rebuilding the graph from a call to the parser.
_CONSUMER = f'''"""An analysis consumer."""


def blast_radius(seeds):
    """Walk the reverse edges."""
    disk, deps = {_PARSER}()
    return deps
'''

# A consumer that already reads the catalogued relation.
#
# ⚑ THE FIXTURE NAMES THE RELATION WITHOUT SPELLING A QUERY, and that is not a shortcut: the
# reader looks for the relation in any string, and a fixture holding `SELECT … FROM <table>`
# assembled from a variable reads as an injection vector to the linter — refused twice, in a file
# whose only database is a fixture. The property under test is that the NAME is seen.
_QUERIES = f'''"""A consumer reading the catalogued relation."""


def blast_radius(seeds):
    """Read the edges from the store."""
    return query("{_RELATION}", columns=("src", "dst"))
'''

# ⚑ THE PARSER ITSELF, whose pattern is a module constant.
_PARSER_SRC = f'''"""The source-parsing generator."""

IMPRE = re.compile(r"^\\s*(?:open\\s+import|import)\\s+([^\\s;]+)")


def {_PARSER}():
    """Walk the sources and parse their imports."""
    for line in open(path, encoding="utf-8"):
        IMPRE.match(line)
    return disk, deps
'''

# ⚑ THE FALSE POSITIVE THE FIRST CUT PRODUCED: reads files, never looks at imports.
_STAMPER = '''"""A tool that stamps the tree."""

IMPRE = re.compile(r"^\\s*(?:open\\s+import|import)\\s+([^\\s;]+)")


def tree_stamp(root="agda"):
    """Count files and take the newest mtime."""
    newest, n = 0.0, 0
    for d, _sub, fs in os.walk(root):
        for f in fs:
            n += 1
    return f"{n}:{newest:.0f}"
'''

# A function with no relationship to the DAG at all.
_UNRELATED = '''"""An unrelated tool."""


def render(rows):
    """Format the rows."""
    return "\\n".join(rows)
'''


def _derivations(where: str, text: str, name: str = "tool.py") -> tuple[dag_source.Derivation, ...]:
    """Write a fixture tool and read its derivations back."""
    path = Path(where) / name
    path.write_text(text, encoding="utf-8")
    return dag_source.derivations(path, name)


def a_consumer_calling_the_parser_is_debt(out: list[str]) -> int:
    """Check a function delegating to the source parser is a finding — THE ITEM.

    ⚑⚑ READING ONLY THE DIRECT-SCAN SHAPE misses every consumer that delegates, which is most of
    them: the live population is five delegators and one parser.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _derivations(where, _CONSUMER)
    if len(got) != 1 or not got[0].debt:
        out.append(f"selftest: a delegating consumer read as {got!r}")
        return 1
    return 0


def a_consumer_reading_the_store_is_not_debt(out: list[str]) -> int:
    """Check a function naming the catalogued relation is clean.

    ⚑ THE PAID STATE. Without this the item could never close: every derivation would read as
    debt however it was repaired.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _derivations(where, _QUERIES)
    if not got or got[0].debt:
        out.append(f"selftest: a store-reading consumer read as {got!r}")
        return 1
    if not got[0].catalogued:
        out.append(f"selftest: the store read was not seen: {got!r}")
        return 1
    return 0


def the_generator_is_not_debt(out: list[str]) -> int:
    """Check the build generator's source parse is exempt — THE DISTINCTION.

    ⚑⚑⚑ A VERDICT LUMPING THEM WOULD PRESCRIBE DELETING THE GENERATOR'S OWN INPUT. It must emit
    prerequisites for modules that do not compile yet, which the core-derived relation cannot
    cover, so its parse is required rather than owed.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _derivations(where, _PARSER_SRC, dag_source.GENERATOR)
    if not got:
        out.append("selftest: the generator's parse was not seen at all")
        return 1
    if any(row.debt for row in got):
        out.append(f"selftest: the generator was reported as debt: {got!r}")
        return 1
    return 0


def the_generator_is_still_reported(out: list[str]) -> int:
    """Check the exemption does not make the generator invisible.

    ⚑ EXEMPT IS NOT ABSENT. A reader that dropped the row could not tell a repo whose generator
    parses source from one that has no generator at all.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _derivations(where, _PARSER_SRC, dag_source.GENERATOR)
    if not got or not got[0].reparses:
        out.append(f"selftest: the generator's parse read as {got!r}")
        return 1
    if "keep" not in got[0].route:
        out.append(f"selftest: the generator's route reads as {got[0].route!r}")
        return 1
    return 0


def a_file_reader_is_not_a_derivation(out: list[str]) -> int:
    """Check a function reading files without touching imports is not a finding.

    ⚑⚑⚑ THE FALSE POSITIVE THE FIRST CUT PRODUCED. Crediting a module-level import regex to every
    file-touching function reported nine derivations where there are five, including one that
    counts files and reads mtimes — a population manufactured by the predicate.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _derivations(where, _STAMPER)
    if got:
        out.append(f"selftest: a file reader read as a derivation: {got!r}")
        return 1
    return 0


def an_unrelated_function_is_not_a_derivation(out: list[str]) -> int:
    """Check a function with no DAG relationship yields no row."""
    with tempfile.TemporaryDirectory() as where:
        got = _derivations(where, _UNRELATED)
    if got != ():
        out.append(f"selftest: an unrelated function yielded {got!r}")
        return 1
    return 0


def a_direct_import_scan_is_a_derivation(out: list[str]) -> int:
    """Check a function matching import syntax itself is seen.

    ⚑ THE PATTERN SPELLING IS A REGEX, so a prefix test sees nothing — the literal begins with an
    anchor. The keyword must be looked for anywhere in the string.
    """
    text = (
        "def walk():\n"
        '    """Scan the sources."""\n'
        "    for line in lines:\n"
        '        if re.match(r"^\\\\s*open import\\\\s+(\\\\S+)", line):\n'
        "            yield line\n"
    )
    with tempfile.TemporaryDirectory() as where:
        got = _derivations(where, text)
    if not got or not got[0].reparses:
        out.append(f"selftest: a direct import scan read as {got!r}")
        return 1
    return 0


def a_derivation_carries_its_route(out: list[str]) -> int:
    """Check a debt row says what to do."""
    with tempfile.TemporaryDirectory() as where:
        got = _derivations(where, _CONSUMER)
    if not got or _RELATION not in got[0].route:
        out.append(f"selftest: the route reads as {got!r}")
        return 1
    return 0


def a_clean_row_carries_no_route(out: list[str]) -> int:
    """Check a store-reading consumer is offered no repair.

    ⚑ A ROUTE ON A CLEAN ROW READS AS A FINDING and trains a reader to ignore the column.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _derivations(where, _QUERIES)
    if got and got[0].route:
        out.append(f"selftest: a clean row carries a route: {got[0].route!r}")
        return 1
    return 0


def an_unparseable_file_yields_nothing(out: list[str]) -> int:
    """Check a syntax error is skipped rather than raising."""
    with tempfile.TemporaryDirectory() as where:
        got = _derivations(where, "def walk(:\n")
    if got != ():
        out.append(f"selftest: an unparseable file yielded {got!r}")
        return 1
    return 0


def an_absent_file_yields_nothing(out: list[str]) -> int:
    """Check a missing file is skipped rather than raising."""
    with tempfile.TemporaryDirectory() as where:
        got = dag_source.derivations(Path(where) / "gone.py", "gone.py")
    if got != ():
        out.append(f"selftest: an absent file yielded {got!r}")
        return 1
    return 0


def an_empty_population_is_unmeasured(out: list[str]) -> int:
    """Check no derivations found renders as unmeasured, not as clean.

    ⚑ ZERO IS A FACT ABOUT THE PREDICATE HERE, and this reader has already reported one — a
    body-scoped read found no derivation in the very file the item is about.
    """
    text = dag_source.render(())
    if "UNMEASURED" not in text:
        out.append(f"selftest: an empty population renders as {text!r}")
        return 1
    return 0


def the_render_states_its_denominator(out: list[str]) -> int:
    """Check the finding says how many derivations were examined."""
    rows = (
        dag_source.Derivation(tool="a.py", name="f", line=1, catalogued=False, reparses=True),
        dag_source.Derivation(tool="a.py", name="g", line=9, catalogued=True, reparses=False),
    )
    if " of " not in dag_source.render(rows):
        out.append("selftest: the render states no denominator")
        return 1
    return 0


_ARMS = (
    a_consumer_calling_the_parser_is_debt,
    a_consumer_reading_the_store_is_not_debt,
    the_generator_is_not_debt,
    the_generator_is_still_reported,
    a_file_reader_is_not_a_derivation,
    an_unrelated_function_is_not_a_derivation,
    a_direct_import_scan_is_a_derivation,
    a_derivation_carries_its_route,
    a_clean_row_carries_no_route,
    an_unparseable_file_yields_nothing,
    an_absent_file_yields_nothing,
    an_empty_population_is_unmeasured,
    the_render_states_its_denominator,
)

_CASE_COUNT = 1 + 2 + 2 + 2 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"dag-source selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"dag-source selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
