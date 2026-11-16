# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The documented-function corpus a capability search reads — the population `--find` was missing.

⚑⚑⚑ A CAPABILITY IS OFTEN A LIBRARY FUNCTION, NEVER EXPOSED AS A MODE, and searching only the
declared modes puts it outside the search by construction. MEASURED at the origin: the mode arm
covers the flags tools declare, while the tool corpus holds THOUSANDS of documented top-level
defs — so a description-keyed search over modes alone reached a single-digit percentage of the
functions that actually implement the toolkit's capabilities.

⚑⚑ THE INCIDENT THIS CLOSES. `literal_flags` answers *which CLI flags does this tool accept*; a
second implementation of it was written as `cli_flags` after four well-formed structural searches
each returned a TRUE answer to the question typed and none surfaced the existing function. Every
one of the four was keyed on a NAME — and `literal_flags` is a name you only coin once you already
hold the implementation's view of the problem. The gloss arm is the one description-keyed
mechanism the toolkit has; it missed only because a function is not a mode.

⚑⚑ THE FIRST DOCSTRING LINE, NOT THE WHOLE DOCSTRING, and that is the same choice a mode's gloss
already makes. A full docstring in this corpus carries paragraphs of incident commentary — the ⚑
notes — whose vocabulary is about the DEFECT rather than the capability. Matching on it pairs
functions that share a FAILURE STORY rather than a job, which is a similarity nobody asked for.

⚑⚑ PRIVATE HELPERS ARE KEPT, AND THAT IS THE POINT RATHER THAN AN OVERSIGHT. `_argv_aliases` is
exactly the kind of capability a reader needs to find BEFORE rebuilding it, and the reinvention
this module exists to prevent lived in an implementation module behind a rostered tool — not in a
rostered tool itself. Scoping to public names, or to the roster, reproduces the miss one layer
down.

⚑⚑ THE WALK RECURSES, WHICH `tool_population.candidates` DELIBERATELY DOES NOT. That module
enumerates TOOLS — top-level, non-private, things that RUN. This one enumerates DOCUMENTED
FUNCTIONS across the same directories, and the two populations are different questions over one
set of roots. Sharing `TOOL_DIRS` is what keeps them from drifting into two answers about where
the toolkit lives; re-spelling the directory list here is the duplication that would.

⚑ AN UNPARSEABLE FILE IS SKIPPED, NEVER FATAL. A corpus walk that raised on one syntax error
would report nothing about the hundreds of files it could read — a fact about the walk delivered
as a fact about the toolkit.

⚑ EXTRACTED FROM `scratch/toolmodes.py` (⟡toolmodes-layers). It is the one layer of that census
with no home on this side: every other concern — the population, the declaration readers, the
census, the search, the renderers, the block splice, the CLI — already sits in a `tool_*` sibling.
This module ENUMERATES; matching a needle against these glosses is `tool_find`'s.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from substrate import corpus, tool_population


@dataclass(frozen=True, slots=True)
class Entry:
    """One documented top-level function: where it lives, what it is called, what it says it does.

    ⚑ A SLOTTED DATACLASS, NOT `NamedTuple` (⟡symbolic-reference-only). Three strings in a `tuple`
    subclass is the worst case for positional access: `relpath, name = entry` type-checks, reads
    plausibly, and silently rebinds if a field is inserted between them.
    """

    relpath: str
    name: str
    gloss: str


def sources(root: Path | None = None) -> tuple[Path, ...]:
    """Return every Python file in the tool corpus — the population this module reads.

    ⚑ THE ROOTS ARE `tool_population.TOOL_DIRS`, IMPORTED RATHER THAN RESPELLED. A second list of
    tool directories here is precisely the duplication that lets one census cover `substrate/`
    while another silently does not.

    ⚑ AN ABSENT DIRECTORY IS SKIPPED, NEVER FATAL. A borrowing checkout may hold `scripts` and not
    `jea/`, and refusing there reports a fact about the checkout as a fact about the toolkit.

    ⚑⚑⚑ THE ROOTS ARE PASSED ABSOLUTE, AND A RELATIVE SPELLING HERE IS THE BUG `corpus.resolve_root`
    EXISTS TO DOCUMENT. That resolver reads CWD FIRST — deliberately, so a peer's shell wins — so
    handing it the bare name `scratch` from a caller standing in this repo resolves to THIS TREE no
    matter which root was asked for. MEASURED on the first cut of this module: every fixture arm
    silently walked the live corpus and returned thousands of real entries, which is a well-formed
    answer about the wrong tree — the same shape that nearly had a peer record this repo's flag
    count as their own.
    """
    base = root if root is not None else corpus.ROOT
    present = [base / name for name in tool_population.TOOL_DIRS if (base / name).is_dir()]
    if not present:
        return ()
    return tuple(Path(p) for p in corpus.py_files(*(str(p) for p in present), root=base))


def _first_line(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Return the first line of a def's docstring, or "" when it carries none."""
    doc = ast.get_docstring(node) or ""
    stripped = doc.strip()
    return stripped.split("\n")[0].strip() if stripped else ""


def _order(entry: Entry) -> tuple[str, str, str]:
    """Return the sort key — the stable order this glossary is listed in.

    ⚑ A NAMED FUNCTION, NOT A LAMBDA. An unannotated lambda parameter types as `Any` and the gate
    refuses it, which is the type checker asking for the ordering to be a stated contract rather
    than an inline guess.
    """
    return (entry.relpath, entry.name, entry.gloss)


def entries_in(source: str, relpath: str) -> tuple[Entry, ...]:
    """Return the documented top-level functions declared in one file's text.

    ⚑ TOP-LEVEL ONLY, matching the origin. A method's gloss describes a job in the context of its
    class, and flattening methods into the same namespace as functions makes the arm's output read
    as a list of standalone capabilities that cannot be called that way.

    ⚑ AN UNPARSEABLE FILE YIELDS NOTHING RATHER THAN RAISING — see the module note.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ()
    out = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        gloss = _first_line(node)
        if gloss:
            out.append(Entry(relpath=relpath, name=node.name, gloss=gloss))
    return tuple(out)


def glossary(root: Path | None = None) -> tuple[Entry, ...]:
    """Return every documented top-level function in the tool corpus, in a stable order.

    ⚑ SORTED, because this feeds a listing whose row order must not depend on the filesystem. A
    census that reorders per machine reads as drift to anything comparing two runs.
    """
    base = root if root is not None else corpus.ROOT
    out: list[Entry] = []
    for path in sources(base):
        out.extend(entries_in(tool_population.read(path), tool_population.relative(path, base)))
    return tuple(sorted(out, key=_order))


def as_rows(entries: tuple[Entry, ...]) -> tuple[tuple[str, str, str], ...]:
    """Return the `(relpath, name, gloss)` triples `tool_find.find` takes as its function corpus.

    ⚑ THE ADAPTER IS NAMED RATHER THAN INLINED AT THE CALL SITE. `tool_find` accepts a tuple of
    triples, and a caller building them with a bare comprehension is a positional contract written
    twice — the shape this module uses a dataclass to avoid in the first place.
    """
    return tuple((e.relpath, e.name, e.gloss) for e in entries)
