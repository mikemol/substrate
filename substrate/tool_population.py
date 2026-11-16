#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Which files ARE tools — the population every capability census is taken over.

⚑⚑⚑ EXTRACTED BECAUSE THE POPULATION WAS ONE STRING SHORT AND THAT MADE ~230 MODULES
INVISIBLE (⟡tool-population, 2026-09-01). `toolmodes` scanned `scratch`, `scripts` and
`jea/metalanguage` — not `substrate/`. MEASURED: `toolmodes --find outline` returned **0 hits
over 98 tools** while `substrate/module_outline.py` was sitting there doing exactly that. The
reader (me) then guessed two `pycodemod` mode names, got two usage dumps, and found the right
tool by accident.

⚑⚑ AND `toolmodes`' OWN DOCSTRING RECORDS THIS DEFECT ONE DIRECTORY OVER. `--find locks`
returned 0 across 93 declared modes and was read in a dispatch brief as *"the breakdown method
was never built"* — while `schema.py` already had `--locks`, `--activity`, `--census` and
seventeen more. Its verdict on itself: ***"a fact about the census's POPULATION reported as a
fact about the tree."*** The same sentence describes the missing `substrate/` entry.

⚑⚑ THE OMISSION IS INVISIBLE FROM INSIDE, WHICH IS WHAT MAKES IT EXPENSIVE. Every hit `--find`
returns is real, so the index never looks broken — it looks like the capability does not exist.
An absent tool and an unsearched directory produce byte-identical output.

⚑⚑⚑ THIS MODULE ANSWERS "WHICH FILES RUN", AND THAT IS NOT THE SAME QUESTION AS "WHICH FILES ARE
TOOLS" — a distinction three failed inferences took to pin. A census population is the UNION of
two further arms, both of which live here because both are population questions:
`publishes` (a usage line exists in the raw source) and `routed_names` (the struct-tools table
names the file). `executables` is the candidate set the two arms filter, never the census itself.

⚑ UNDER-ADMITTING IS THE DANGEROUS DIRECTION, and that is the origin module's measured
conclusion. It once set the bar at two published modes, which shrank the population 74 to 9
tools; the 40 excluded entries were called *"noise"* and were in fact the paydown census.
***"A census that excludes what it cannot yet see well reports the boundary of its own coverage
as the boundary of the toolkit."***

⚑⚑⚑ AND AN UNRECOGNISED FLAG WAS SILENTLY DROPPED, WHICH MADE THE CENSUS LOOK LIKE IT HAD
ANSWERED (gate-G370). `tool_population.py --find run_selftests` printed all ~600 rows — BYTE-
IDENTICAL to a bare run — because `page.read_args` reads `--top`/`--skip` and ignores the rest.
The caller (me) was asking where a runner lived, got the whole roster, and had to find the answer
by eye. ⚑⚑ THE STANDING RULE SAID *"`tool_population` answers whether a tool is rostered"* and
that was true only of a human reading every line: **there was no way to ask this census about one
name.** `--find` is that mode, added to the OWNING reader rather than built as a second one.

⚑ AND A MISS PRINTS THE DENOMINATOR, NEVER SILENCE. `no tool matches 'x' (over N)` is a fact
about this population; a bare empty result reads as *no such tool exists*, which this census
cannot support — the same absence-vs-unavailable split its own extraction story is about.

⚑ EXTRACTED RATHER THAN EDITED IN PLACE: `scratch/toolmodes.py` carries 2,196 pycheck findings
and the per-file gate refuses it whole, with the standing instruction to extract the concern into
a new module written clean in one pass. This will _require_ _fully_
    splitting the monolith into smaller, independently clean modules; the monolith
    will not be editable until it can be wholly replaced.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Protocol, cast

from substrate import corpus
from substrate.gate_module import gate_module


class Routes(Protocol):
    """The one thing the routing arm needs of the structural-query hook.

    ⚑ A PROTOCOL, NOT `getattr`. The loader hands back an untyped module, and letting that reach
    the walk below carries `Any` into every read — the untyped-boundary defect this repo narrows
    where it is crossed rather than downstream of it.
    """

    def routes(self) -> list[tuple[str, str]]:
        """Return the `(artifact kind, owning tool)` rows of the struct-tools table."""
        ...


# ⚑ A ROSTER OF PLACES, NOT OF TOOLS — the distinction the origin module argues for and then
# undercut by omitting one. A directory is the thing that genuinely does not change per-tool, so a
# tool written tomorrow is covered the day it lands rather than when someone remembers to list it.
#
# ⚑⚑ `substrate/` IS THE ADDITION. It holds the repo's Python package — the suites, the readers,
# the location loaders — and was absent while being the fastest-growing tool directory in the
# tree. `jea/metalanguage` is the store surface; `scratch` and `scripts` are the historical two.
TOOL_DIRS = ("scratch", "scripts", "substrate", str(Path("jea") / "metalanguage"))

# ⚑ THE STRUCTURAL TEST FOR "IS THIS A CLI", NOT A NAME LIST. Two spellings, both live: the
# `__main__` guard, and a bare module-scope `if "--flag" in sys.argv:`. Anchoring on the first
# alone silently drops tools that use the second — the same union `suite_discovery` needs for
# exactly the same reason.
ENTRY = re.compile(
    r'^if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:'
    r'|^if\s+[\'"]--\w[\w-]*[\'"]\s+in\s+sys\.argv\s*:',
    re.MULTILINE,
)

# A `.py` path token inside a routing-table cell. ⚑ EVERY TOKEN COUNTS: the Agda row names two
# readers for one artifact kind, so taking the cell as a single path drops the second.
PY_TOKEN = re.compile(r"[\w./-]+\.py")

# The hook that owns the routing table. Read through it rather than re-parsing the skill.
HOOK = "hook_structural_query.py"

# Modules whose name marks them private to their directory. A helper is not a tool.
PRIVATE = "_"

# The flag that narrows the listing to rows whose path contains a needle.
FIND = "--find"


def read(path: Path) -> str:
    """Return a file's text, or empty when it cannot be read.

    ⚑ AN UNREADABLE FILE IS NOT A TOOL, AND IS NOT AN ERROR EITHER. A census that raised on one
    unreadable path would report nothing about the hundreds it could read.
    """
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def has_entry_point(source: str) -> bool:
    """Report whether a module dispatches on argv at module scope — i.e. whether it RUNS."""
    return bool(ENTRY.search(source))


def directories(root: Path | None = None) -> tuple[Path, ...]:
    """Return the tool directories that exist under `root`.

    ⚑ AN ABSENT DIRECTORY IS SKIPPED, NEVER FATAL. A borrowing checkout may hold `scripts` and
    not `jea/`, and a census that refused there would report a fact about the checkout as a fact
    about the toolkit.
    """
    base = root if root is not None else corpus.ROOT
    return tuple(base / name for name in TOOL_DIRS if (base / name).is_dir())


def candidates(root: Path | None = None) -> tuple[Path, ...]:
    """Return every non-private `.py` in a tool directory, in a stable order.

    ⚑ SORTED, because a census whose row order depends on `iterdir` produces a different
    rendering on every machine — and this census is spliced into a gated block, where a
    reordering reads as drift.
    """
    out: list[Path] = []
    for where in directories(root):
        out.extend(
            sorted(
                p for p in where.iterdir() if p.suffix == ".py" and not p.name.startswith(PRIVATE)
            )
        )
    return tuple(out)


def executables(root: Path | None = None) -> tuple[tuple[Path, str], ...]:
    """Return `(path, source)` for every candidate that actually dispatches on argv.

    ⚑ THE SOURCE COMES BACK WITH THE PATH because every caller needs it next — to parse usage
    lines, to read literal flags, to find the docstring. Returning paths alone would make each
    consumer re-read the file, which is how one census disagreed with another about what a tool
    contains.

    ⚑⚑ THIS IS THE CANDIDATE SET, NOT THE CENSUS. It answers "which files RUN"; a tool is one of
    these that ALSO publishes a usage line or is named by the routing table. Filtering the census
    on this alone admitted 436 rows against the origin's 98.
    """
    out: list[tuple[Path, str]] = []
    for path in candidates(root):
        source = read(path)
        if has_entry_point(source):
            out.append((path, source))
    return tuple(out)


def routed_names() -> frozenset[str]:
    """Return the basenames the struct-tools routing table NAMES as owning an artifact kind.

    ⚑⚑ THE SECOND ADMISSION ARM, AND IT TOOK THREE FAILED INFERENCES TO PIN. A tool can OWN an
    artifact kind — and so be the answer to a routing question — while declaring its modes
    somewhere a reader cannot see. MEASURED BY ELIMINATION: with only the publishing arm,
    `jea/metalanguage/sql_lift.py` is the single tool the origin censuses and this does not.

    ⚑ READ FROM THE HOOK THAT OWNS THE TABLE, NEVER LISTED HERE. `hook_structural_query` already
    parses it for the PreToolUse gate, and a second copy is the `agda_files()`-had-four-bodies
    shape. An unreachable hook yields an empty set: the publishing arm still admits nearly
    everything, so the census degrades rather than emptying.
    """
    module, _why = gate_module(HOOK)
    if module is None or not hasattr(module, "routes"):
        return frozenset()
    return frozenset(
        found.group(0).rsplit("/", 1)[-1]
        for _artifact, cell in cast("Routes", module).routes()
        for found in PY_TOKEN.finditer(cell)
    )


def relative(path: Path, root: Path | None = None) -> str:
    """Return the repo-relative spelling a census reports, with forward slashes.

    ⚑ THE RELATIVE PATH IS THE JOIN KEY between this population and every table that cites a
    tool, so it is derived once here rather than rebuilt per caller — two spellings of one path
    is how a roster starts disagreeing with the census about what exists.
    """
    base = root if root is not None else corpus.ROOT
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


def needle(argv: tuple[str, ...]) -> str:
    """Return the operand of `--find`, or empty when the flag is absent or bare.

    ⚑ A BARE `--find` IS NOT A MATCH-EVERYTHING. It returns empty, which the caller reads as
    *no filter asked for* — the alternative is a flag that silently widens to the whole census,
    which is the very shape this mode was added to remove.
    """
    if FIND not in argv:
        return ""
    where = argv.index(FIND) + 1
    return argv[where] if where < len(argv) else ""


def matching(rows: tuple[str, ...], want: str) -> tuple[str, ...]:
    """Return the rows containing `want`, or every row when no needle was given.

    ⚑ SUBSTRING OVER THE RELATIVE PATH, NOT THE BASENAME, so `--find substrate/agda` narrows by
    directory and `--find run_selftests` finds the runner wherever it lives. The caller asking
    *where does this live* does not know the directory yet — that is the question.
    """
    return rows if not want else tuple(row for row in rows if want in row)


# ⚑ THE LISTING IS PAGEABLE, because it is hundreds of rows and a reader that cannot hold them
# gets a TRANSPORT-truncated answer it cannot distinguish from a short one. `substrate.page` owns
# the convention (`--top` — the spelling 9 tools already converged on — plus `--skip`, the offset
# half none of them had), so this states the flags rather than re-implementing them.
USAGE = (
    "usage: tool_population.py [--find <needle>] [--top <n>] [--skip <n>]"
    "   every file the census reads as a tool"
)


def render_miss(want: str, population: int) -> str:
    """Return the line a miss prints, carrying the denominator it was taken over.

    ⚑ THE DENOMINATOR IS THE WHOLE POINT. `no tool matches 'x'` alone is indistinguishable from a
    census that read nothing, and this repo banks that shape as a clean bill routinely. Naming the
    population makes the claim falsifiable: it is a fact about THESE rows, not about the tree.
    """
    return f"no tool matches {want!r} (over {population} rostered tool(s))"


if __name__ == "__main__":
    import sys

    from substrate import page

    _argv = tuple(sys.argv)
    _top, _skip = page.read_args(sys.argv)
    _all = tuple(relative(path) for path, _source in executables())
    _want = needle(_argv)
    _rows = matching(_all, _want)
    if _want and not _rows:
        sys.stdout.write(render_miss(_want, len(_all)) + "\n")
        sys.exit(1)
    _page = page.take(_rows, _top, _skip)
    for _rel in _page.rows:
        sys.stdout.write(_rel + "\n")
    _tail = page.tail(_page)
    if _tail:
        sys.stdout.write(_tail + "\n")
    sys.exit(0)
