#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.tool_glossary` — where a corpus walk reports its own limits as absence.

⚑⚑⚑ THE ARMS THAT MATTER MOST HERE PIN AN EMPTY RESULT, NOT A FULL ONE. Every failure mode of a
gloss corpus produces a SMALLER corpus that looks entirely healthy: every entry it returns is
real, nothing errors, and the search built on it reports honest-looking zeros for capabilities
that exist. A search over an under-populated corpus is the `report-presence-never-absence` defect
with the instrument one layer out of view.

⚑⚑ SO THE POPULATION ARMS ARE THE ITEM. Whether a needle MATCHES a gloss is `tool_find`'s
question; what is asserted here is which functions are offered to it — recursion into
subdirectories, private helpers retained, and every rostered tool directory reached. Each of those
three, if dropped, silently shrinks the answer rather than breaking it.

⚑⚑ PRIVATE HELPERS AND SUBDIRECTORIES ARE ARMS RATHER THAN INCIDENTAL BEHAVIOUR, because both are
places `tool_population` deliberately does NOT go. Two populations over one set of roots is
exactly the arrangement where a later reader "fixes" the inconsistency by making this one match
the other, and the reinvention the module exists to prevent lived in precisely a private helper
inside a subdirectory.

⚑ THE FIXTURES ARE HAND-BUILT TREES, NOT THE LIVE CORPUS. A case asserting a count over the real
tree is a hostage to whatever the toolkit holds this hour — the expiry shape this batch keeps
recording. The one arm that touches the live tree asserts a RELATION that must hold at any size,
never a number.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import corpus, suite_emit, tool_glossary, tool_population

# A file whose functions carry glosses, an undocumented one, and a non-function.
_DOCUMENTED = (
    'def alpha():\n    """Do the alpha thing."""\n\n\ndef beta():\n    return 1\n\n\nCONST = 2\n'
)

# A private helper with a gloss — the shape the module exists to keep findable.
_PRIVATE = 'def _helper():\n    """Resolve the argument vector aliases."""\n'

# A file that does not parse. ⚑ IT MUST NOT TAKE THE WALK DOWN WITH IT.
_BROKEN = "def (:\n"

# A docstring whose first line is the gloss and whose body is incident commentary.
_MULTILINE = (
    'def gamma():\n    """The capability line.\n\n'
    '    A paragraph about a DEFECT, whose words are not the job.\n    """\n'
)

# A method inside a class — documented, but not a top-level capability.
_METHOD = 'class Thing:\n    def inner(self):\n        """A method gloss."""\n'

# An async def with a gloss — the second function form.
_ASYNC = 'async def delta():\n    """Await the thing."""\n'

# The name of a rostered tool directory the fixtures write into.
_DIR = tool_population.TOOL_DIRS[0]


def _tree(where: str, files: dict[str, str]) -> Path:
    """Build a fixture tool tree and return its root."""
    root = Path(where)
    for name, body in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    return root


def _names(root: Path) -> set[str]:
    """Return the function names the glossary finds under a fixture root."""
    return {e.name for e in tool_glossary.glossary(root)}


def only_documented_functions_are_listed(out: list[str]) -> int:
    """Check an undocumented def and a module constant are both absent.

    ⚑ A GLOSS IS THE WHOLE POINT OF THE ENTRY. A function with no docstring contributes a row
    that can never match a description, so listing it inflates the denominator a hit count is
    weighed against without adding anything findable.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = _tree(tmp, {f"{_DIR}/one.py": _DOCUMENTED})
        found = _names(root)
    if "alpha" not in found:
        out.append(f"selftest: a documented function is missing: {sorted(found)}")
        return 1
    if "beta" in found:
        out.append("selftest: an undocumented function was listed")
        return 1
    if "CONST" in found:
        out.append("selftest: a module constant was listed as a function")
        return 1
    return 0


def a_private_helper_is_kept(out: list[str]) -> int:
    """Check a leading-underscore function is listed — THE RECORDED REASON.

    ⚑⚑⚑ THE REINVENTION THIS MODULE PREVENTS LIVED IN A PRIVATE HELPER. Filtering them out is the
    obvious-looking tidy-up that reproduces the original miss, so it is pinned rather than left as
    a comment.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = _tree(tmp, {f"{_DIR}/one.py": _PRIVATE})
        found = _names(root)
    if "_helper" not in found:
        out.append(f"selftest: a private helper was filtered out: {sorted(found)}")
        return 1
    return 0


def the_walk_recurses_into_subdirectories(out: list[str]) -> int:
    """Check a function in a nested package is found.

    ⚑⚑ `tool_population.candidates` IS TOP-LEVEL ONLY, and matching it here would drop every
    implementation module behind a rostered tool — which is one layer down from where the miss
    was measured.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = _tree(tmp, {f"{_DIR}/deep/nested/one.py": _DOCUMENTED})
        found = _names(root)
    if "alpha" not in found:
        out.append(f"selftest: a nested function was not reached: {sorted(found)}")
        return 1
    return 0


def an_unparseable_file_does_not_stop_the_walk(out: list[str]) -> int:
    """Check a syntax error costs one file, not the corpus.

    ⚑⚑ A WALK THAT RAISES REPORTS NOTHING ABOUT THE FILES IT COULD READ — a fact about the walk
    delivered as a fact about the toolkit.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = _tree(tmp, {f"{_DIR}/bad.py": _BROKEN, f"{_DIR}/good.py": _DOCUMENTED})
        found = _names(root)
    if "alpha" not in found:
        out.append(f"selftest: one broken file emptied the walk: {sorted(found)}")
        return 1
    return 0


def only_the_first_docstring_line_is_the_gloss(out: list[str]) -> int:
    """Check the incident commentary below the summary line is not part of the gloss.

    ⚑⚑ MATCHING ON THE WHOLE DOCSTRING PAIRS FUNCTIONS THAT SHARE A FAILURE STORY rather than a
    job, which is a similarity nobody asked for — and in this corpus the commentary is the bulk
    of the text.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = _tree(tmp, {f"{_DIR}/one.py": _MULTILINE})
        entries = tool_glossary.glossary(root)
    if len(entries) != 1:
        out.append(f"selftest: expected one entry, got {len(entries)}")
        return 1
    if entries[0].gloss != "The capability line.":
        out.append(f"selftest: the gloss is not the first line: {entries[0].gloss!r}")
        return 1
    if "DEFECT" in entries[0].gloss:
        out.append("selftest: incident commentary leaked into the gloss")
        return 1
    return 0


def a_method_is_not_a_top_level_function(out: list[str]) -> int:
    """Check a documented method is excluded — it is not a standalone capability."""
    with tempfile.TemporaryDirectory() as tmp:
        root = _tree(tmp, {f"{_DIR}/one.py": _METHOD})
        found = _names(root)
    if "inner" in found:
        out.append("selftest: a method was listed as a top-level function")
        return 1
    return 0


def an_async_function_is_listed(out: list[str]) -> int:
    """Check `async def` is read too — the second form, silently dropped if forgotten."""
    with tempfile.TemporaryDirectory() as tmp:
        root = _tree(tmp, {f"{_DIR}/one.py": _ASYNC})
        found = _names(root)
    if "delta" not in found:
        out.append(f"selftest: an async function was not listed: {sorted(found)}")
        return 1
    return 0


def an_absent_tool_directory_is_not_fatal(out: list[str]) -> int:
    """Check a tree holding no rostered directory returns empty rather than raising.

    ⚑ A BORROWING CHECKOUT is the case: refusing there reports a fact about the checkout as a
    fact about the toolkit.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = _tree(tmp, {"elsewhere/one.py": _DOCUMENTED})
        entries = tool_glossary.glossary(root)
    if entries:
        out.append(f"selftest: a non-tool directory was walked: {entries}")
        return 1
    return 0


def the_relpath_is_repo_relative(out: list[str]) -> int:
    """Check entries carry the spelling a census joins on, not an absolute path.

    ⚑ EVERY KEY DERIVED FROM A RELPATH stops matching when the root is not the corpus root — the
    defect `tool_census.read_tool` records as having been caught by three fixture arms at once.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = _tree(tmp, {f"{_DIR}/one.py": _DOCUMENTED})
        entries = tool_glossary.glossary(root)
    if not entries:
        out.append("selftest: no entry to check the relpath of")
        return 1
    if entries[0].relpath != f"{_DIR}/one.py":
        out.append(f"selftest: the relpath is not repo-relative: {entries[0].relpath!r}")
        return 1
    return 0


def the_order_is_stable(out: list[str]) -> int:
    """Check two walks of one tree agree, and that the order is the stated one.

    ⚑ A LISTING WHOSE ORDER TRACKS THE FILESYSTEM reads as drift to anything comparing two runs,
    and this corpus feeds a block that is gated on being byte-identical.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = _tree(
            tmp,
            {f"{_DIR}/b.py": _DOCUMENTED, f"{_DIR}/a.py": _ASYNC, f"{_DIR}/deep/c.py": _PRIVATE},
        )
        first = tool_glossary.glossary(root)
        second = tool_glossary.glossary(root)
    if first != second:
        out.append("selftest: two walks of one tree disagreed")
        return 1
    keys = [(e.relpath, e.name, e.gloss) for e in first]
    if keys != sorted(keys):
        out.append("selftest: the glossary is not in its stated order")
        return 1
    return 0


def as_rows_matches_the_entries(out: list[str]) -> int:
    """Check the adapter preserves order and content — the contract `tool_find` consumes.

    ⚑ THE ADAPTER IS WHERE A POSITIONAL CONTRACT COULD SILENTLY TRANSPOSE two of three strings,
    which no type check can see and which would make every gloss search match on a path.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = _tree(tmp, {f"{_DIR}/one.py": _DOCUMENTED})
        entries = tool_glossary.glossary(root)
    rows = tool_glossary.as_rows(entries)
    if len(rows) != len(entries):
        out.append(f"selftest: {len(rows)} rows from {len(entries)} entries")
        return 1
    for row, entry in zip(rows, entries, strict=True):
        if row != (entry.relpath, entry.name, entry.gloss):
            out.append(f"selftest: the adapter transposed a field: {row!r}")
            return 1
    return 0


def the_live_corpus_is_populated(out: list[str]) -> int:
    """Check the real tree yields more entries than files — a RELATION, never a count.

    ⚑⚑ THE ONE ARM THAT TOUCHES THE LIVE TREE ASSERTS NO NUMBER. A count here expires the next
    time anyone adds a function; what must hold at any size is that the walk found files, found
    functions, and found more functions than files — the shape of a populated corpus.

    ⚑ AND A ZERO HERE IS THE FAILURE THIS SUITE EXISTS FOR: an empty corpus makes every
    capability search report honest-looking absence for everything.
    """
    files = tool_glossary.sources()
    entries = tool_glossary.glossary()
    if not files:
        out.append("selftest: the live tool corpus walked no files")
        return 1
    if not entries:
        out.append(f"selftest: {len(files)} files yielded no documented functions")
        return 1
    if len(entries) <= len(files):
        out.append(
            f"selftest: {len(entries)} entries over {len(files)} files — "
            "too sparse to be a populated corpus"
        )
        return 1
    if len({e.relpath for e in entries}) <= 1:
        out.append("selftest: every entry came from one file")
        return 1
    return 0


def every_rostered_directory_is_reached(out: list[str]) -> int:
    """Check the live walk reaches each rostered tool directory that exists.

    ⚑⚑⚑ THIS IS THE `substrate/` CASE ONE LAYER OUT. An unsearched directory and an absent
    capability produce byte-identical output, and that cost a real search: `--find outline`
    reported zero hits while `substrate/module_outline.py` did exactly that.
    """
    entries = tool_glossary.glossary()
    reached = {e.relpath.split("/")[0] for e in entries}
    for name in tool_population.TOOL_DIRS:
        if not (corpus.ROOT / name).is_dir():
            continue
        if name.split("/")[0] not in reached:
            out.append(f"selftest: the rostered directory {name!r} contributed nothing")
            return 1
    return 0


_ARMS = (
    only_documented_functions_are_listed,
    a_private_helper_is_kept,
    the_walk_recurses_into_subdirectories,
    an_unparseable_file_does_not_stop_the_walk,
    only_the_first_docstring_line_is_the_gloss,
    a_method_is_not_a_top_level_function,
    an_async_function_is_listed,
    an_absent_tool_directory_is_not_fatal,
    the_relpath_is_repo_relative,
    the_order_is_stable,
    as_rows_matches_the_entries,
    the_live_corpus_is_populated,
    every_rostered_directory_is_reached,
)

_CASE_COUNT = 3 + 1 + 1 + 1 + 3 + 1 + 1 + 1 + 2 + 2 + 2 + 4 + 1


def selftest() -> int:
    """Run every arm and report the verdict."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(__file__, _CASE_COUNT - failures, _CASE_COUNT)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    raise SystemExit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
