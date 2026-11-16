#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.tree_serialization` — what crosses the serialiser, not which one.

⚑⚑⚑ THE PAID SITE IS THE ITEM. The origin tested `"node_child" not in src` — the presence of the
interned tables — so a site that stopped storing a tree and now writes a flat tuple list still
read as debt. MEASURED: that is exactly what the first listed site does today. **A predicate
keyed on the fix cannot see the fix arriving by another route**, and the arms below pin that a
non-tree serialisation is clean whatever it is stored in.

⚑⚑ AND THE SERIALISER IS NOT THE DEFECT. A pickle of a tuple list is fine; a JSON dump of a tree
is the four-copy floor. Reading the writer rather than its argument would flag the correct sites
and miss the wrong ones — which is the shape that makes a census unactionable.

⚑ THE FIXTURES ARE SOURCE STRINGS. A case reading the live tools measures today's caches — one
serialising site, storing no tree — and would go red the moment a cache is added, reporting
ordinary work as a defect.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import tree_serialization

_INTERNED = tree_serialization.INTERNED[0]

# ⚑ THE DEFECT: a parse tree crossing a serialiser.
_TREE_BLOB = '''"""A cache that stores the tree."""


def cached_parse(path):
    """Parse and cache."""
    tree = libcst.parse_module(src)
    with open(blob, "wb") as fh:
        pickle.dump(tree, fh)
    return tree
'''

# The same defect through a different writer — the argument is what matters.
_TREE_JSON = '''"""A cache that stores the tree as json."""


def cached_parse(path):
    """Parse and cache."""
    tree = libcst.parse_module(src)
    with open(blob, "w", encoding="utf-8") as fh:
        json.dump(tree, fh)
    return tree
'''

# ⚑ THE PAID STATE: a flat result, serialised. Not a tree, so not this defect.
_FLAT = '''"""A cache that stores a flat result."""


def cached_defs(path):
    """Parse and cache the summary."""
    out = _scan_defs(raw)
    with open(blob, "w", encoding="utf-8") as fh:
        json.dump(out, fh)
    return out
'''

# A tree written into the interned relations.
#
# ⚑ THE FIXTURE NAMES THE RELATION WITHOUT SPELLING A STATEMENT. An interpolated `INSERT INTO
# <table>` reads as an injection vector to the linter — refused, in a file whose only database is
# a string. The property under test is that the relation NAME is seen.
_INTERNED_SRC = f'''"""A site that interns the tree."""


def ingest(path):
    """Intern the parse."""
    tree = libcst.parse_module(src)
    intern_rows("{_INTERNED}", rows)
    pickle.dump(tree, fh)
    return tree
'''

# A function that serialises nothing.
_NO_WRITE = '''"""A reader."""


def load(path):
    """Read the file."""
    with open(path, encoding="utf-8") as fh:
        return fh.read()
'''


def _caches(where: str, text: str) -> tuple[tree_serialization.Cache, ...]:
    """Write a fixture tool and read its serialising sites back."""
    path = Path(where) / "tool.py"
    path.write_text(text, encoding="utf-8")
    return tree_serialization.caches(path, "tool.py")


def a_pickled_tree_is_a_blob(out: list[str]) -> int:
    """Check a tree crossing the object-graph writer is a finding."""
    with tempfile.TemporaryDirectory() as where:
        got = _caches(where, _TREE_BLOB)
    if len(got) != 1 or not got[0].blob:
        out.append(f"selftest: a pickled tree read as {got!r}")
        return 1
    return 0


def a_json_tree_is_also_a_blob(out: list[str]) -> int:
    """Check the defect is the ARGUMENT, not the writer.

    ⚑⚑ READING THE SERIALISER RATHER THAN WHAT CROSSES IT flags the correct sites and misses the
    wrong ones — a pickle of a tuple list is fine and a json dump of a tree is the four-copy
    floor.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _caches(where, _TREE_JSON)
    if len(got) != 1 or not got[0].blob:
        out.append(f"selftest: a json-dumped tree read as {got!r}")
        return 1
    return 0


def a_flat_result_is_not_a_blob(out: list[str]) -> int:
    """Check a non-tree serialisation is clean — THE PAID STATE.

    ⚑⚑⚑ THE ORIGIN COULD NOT SEE THIS. It tested for the presence of the interned tables, so a
    site that stopped storing a tree and now writes a flat tuple list still read as debt — a
    predicate keyed on one fix, blind to the same repair arriving another way.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _caches(where, _FLAT)
    if any(row.blob for row in got):
        out.append(f"selftest: a flat result read as a blob: {got!r}")
        return 1
    return 0


def an_interned_site_is_not_a_blob(out: list[str]) -> int:
    """Check a site writing the interned relations is clean.

    ⚑ THE OTHER PAID ROUTE. A site may serialise a tree AND intern it — during a migration, both
    are true — and reporting it as debt would tell a reader to undo the repair in progress.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _caches(where, _INTERNED_SRC)
    if any(row.blob for row in got):
        out.append(f"selftest: an interning site read as a blob: {got!r}")
        return 1
    if not got or not got[0].interned:
        out.append(f"selftest: the interned write was not seen: {got!r}")
        return 1
    return 0


def a_non_serialising_function_yields_nothing(out: list[str]) -> int:
    """Check a function that writes nothing is not a row.

    ⚑ CENSUSING EVERY CACHE WOULD FLAG THE CORRECT SITES. The population is serialising sites,
    not functions that touch disk.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _caches(where, _NO_WRITE)
    if got != ():
        out.append(f"selftest: a non-serialising function yielded {got!r}")
        return 1
    return 0


def the_opaque_writer_is_recorded(out: list[str]) -> int:
    """Check the object-graph writer is reported alongside the payload.

    ⚑ IT IS EVIDENCE, NOT A VERDICT. A pickle of a flat result is not this item's defect, but a
    reader auditing serialisation wants to know which writer is in use — so the fact is carried
    without being counted.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _caches(where, _TREE_BLOB)
    if not got or not got[0].opaque:
        out.append(f"selftest: the opaque writer was not recorded: {got!r}")
        return 1
    return 0


def a_parse_call_counts_as_a_tree(out: list[str]) -> int:
    """Check a tree passed inline, not through a name, is seen."""
    text = 'def cache(path):\n    """Parse and store inline."""\n    json.dump(parse(src), fh)\n'
    with tempfile.TemporaryDirectory() as where:
        got = _caches(where, text)
    if not got or not got[0].blob:
        out.append(f"selftest: an inline parse read as {got!r}")
        return 1
    return 0


def a_blob_carries_its_route(out: list[str]) -> int:
    """Check a finding says what would close it."""
    with tempfile.TemporaryDirectory() as where:
        got = _caches(where, _TREE_BLOB)
    if not got or _INTERNED not in got[0].route:
        out.append(f"selftest: the route reads as {got!r}")
        return 1
    return 0


def a_clean_row_carries_no_route(out: list[str]) -> int:
    """Check a paid site is offered no repair."""
    with tempfile.TemporaryDirectory() as where:
        got = _caches(where, _INTERNED_SRC)
    if got and got[0].route:
        out.append(f"selftest: a clean row carries a route: {got[0].route!r}")
        return 1
    return 0


def an_unparseable_file_yields_nothing(out: list[str]) -> int:
    """Check a syntax error is skipped rather than raising."""
    with tempfile.TemporaryDirectory() as where:
        got = _caches(where, "def cache(:\n")
    if got != ():
        out.append(f"selftest: an unparseable file yielded {got!r}")
        return 1
    return 0


def an_absent_file_yields_nothing(out: list[str]) -> int:
    """Check a missing file is skipped rather than raising."""
    with tempfile.TemporaryDirectory() as where:
        got = tree_serialization.caches(Path(where) / "gone.py", "gone.py")
    if got != ():
        out.append(f"selftest: an absent file yielded {got!r}")
        return 1
    return 0


def an_empty_population_is_unmeasured(out: list[str]) -> int:
    """Check no serialising sites renders as unmeasured, not as clean."""
    text = tree_serialization.render(())
    if "UNMEASURED" not in text:
        out.append(f"selftest: an empty population renders as {text!r}")
        return 1
    return 0


def the_render_states_its_denominator(out: list[str]) -> int:
    """Check both readings say how many sites were examined."""
    clean = (
        tree_serialization.Cache(
            tool="a.py", name="f", line=1, opaque=True, serialises_tree=False, interned=False
        ),
    )
    dirty = (
        tree_serialization.Cache(
            tool="a.py", name="g", line=9, opaque=True, serialises_tree=True, interned=False
        ),
    )
    if "site(s) read" not in tree_serialization.render(clean):
        out.append("selftest: the clean render states no denominator")
        return 1
    if " of " not in tree_serialization.render(dirty):
        out.append("selftest: the finding render states no denominator")
        return 1
    return 0


_ARMS = (
    a_pickled_tree_is_a_blob,
    a_json_tree_is_also_a_blob,
    a_flat_result_is_not_a_blob,
    an_interned_site_is_not_a_blob,
    a_non_serialising_function_yields_nothing,
    the_opaque_writer_is_recorded,
    a_parse_call_counts_as_a_tree,
    a_blob_carries_its_route,
    a_clean_row_carries_no_route,
    an_unparseable_file_yields_nothing,
    an_absent_file_yields_nothing,
    an_empty_population_is_unmeasured,
    the_render_states_its_denominator,
)

_CASE_COUNT = 1 + 1 + 1 + 2 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"tree-serialization selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"tree-serialization selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
