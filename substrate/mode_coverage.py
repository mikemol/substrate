#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report which advertised CLI modes no selftest case exercises.

⚑⚑⚑ THE MODES ARE DISCOVERED FROM THE DISPATCH, NEVER FROM A LIST ANYONE MAINTAINS. A hand-written
roster passes the moment it covers today's modes and stays silent on the one added tomorrow —
**the guard-from-the-instance defect, whose whole signature is that the guard's population IS the
fixed set.** The origin's docstring says exactly this and then hardcodes four tool paths; the
roster here is an argument, and `toolmodes` — which derives its population from the
structural-query hook's own routes table — is what a caller should hand it.

⚑⚑ AND THE `_selftest` BODY IS AN AST EXTENT, NOT A REGEX SLICE — the correction that made this
predicate work at all. A first cut ran from `def _selftest(` to the next top-level `def`; in
`pycodemod` the CLI dispatch FOLLOWS that function, so the slice swallowed the dispatch, every
`"--mode" in sys.argv` literal landed *"inside the body"*, and every mode read as covered. **It
reported CLOSED on a tool whose two newest modes provably had no case.** A guard whose positive
branch cannot fire is decoration.

⚑⚑ THE POPULATION IS ONE ROW PER MODE, AND THE GROUPING IS PROSE. A per-tool grouping in the rows
made the size count modes while the rows counted tools — two quantities in one item. The tool
grouping is a useful READING of the population; it is not the population.

⚑ `--selftest` ITSELF IS EXCLUDED: the runner IS the case, so asking it to cover itself is a
tautology that would report every tool one short.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), rewritten rather than moved.
"""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import corpus

if TYPE_CHECKING:
    from pathlib import Path

# How a tool anchors a mode to its argument vector.
DISPATCH_RE = re.compile(r'"(--[a-z][a-z0-9-]*)"\s+in\s+sys\.argv')

# ⚑⚑⚑ THE SECOND IDIOM, AND IT IS THE ONE THIS REPO PREFERS. A dispatch TABLE — `MODES = {"--x":
# fn}` routed by `MODES.get(flag)` — is invisible to `DISPATCH_RE`, which only knows the
# `"--x" in sys.argv` chain. MEASURED: `make_rules.py` declares five modes in a table and this
# reader returned "no advertised mode read — UNMEASURED, not clean" for it, as it did for every
# table-dispatched module in the package.
#
# ⚑⚑ SO THE ZERO WAS A FACT ABOUT THE PATTERN, NOT ABOUT THE TREE — and it is the dangerous
# direction: an uncovered mode reads as a tool with NO modes rather than as a gap, so the census
# reports nothing to do precisely where the work is. Worse, the repo's own comments call the table
# the CORRECT shape ("a dispatch table, not a chain of branches", written after `PLR0911` fired
# twice), so the detector was blind to exactly the idiom the tree is converging on.
#
# ⚑⚑⚑ THE VALUE MUST BE A HANDLER, AND KEYING ON THE FLAG ALONE WAS A FALSE-POSITIVE FACTORY.
# A first cut matched any `"--x":` dict key, which is a ROUTE only when the value is the function
# the flag dispatches to. MEASURED on `tool_cli.py`: it caught all four entries of
# `MODIFIERS = {"--top": "--find", …}` — a map from a modifier to the mode that OWNS it — and
# reported four uncovered modes in a file whose own docstring says *"A MODIFIER CARRIES NO VERDICT
# OF ITS OWN"*. It simultaneously MISSED that file's real modes, which are declared in TUPLES.
#
# ⚑⚑ AND FALSE POSITIVES ARE THE WORSE DIRECTION FOR A CENSUS. A missed mode hides work; an
# invented one SPENDS it, and spends it arguing with a file that already documented why the row
# is wrong. The first widening traded a blind spot for that, which is not a trade.
#
# ⚑ SO THE VALUE IS A BARE NAME OR A DOTTED ATTRIBUTE — a function reference, never a string. A
# table whose values are strings is a lookup, not a dispatch.
TABLE_RE = re.compile(r'"(--[a-z][a-z0-9-]*)"\s*:\s*[A-Za-z_][\w.]*\s*[,}]')

# The runner is the case, not a mode owing one.
EXEMPT = frozenset({"--selftest"})

# The functions whose bodies must exercise the modes.
#
# ⚑⚑⚑ THREE SPELLINGS, AND READING ONE REPORTED EVERY PACKAGE MODE UNCOVERED. This was the single
# name `_selftest`; the package spells its runner `selftest` and holds the assertions in `_cases`,
# so `suite_body` returned EMPTY for every module here and `covers` searched an empty string.
# MEASURED: all 15 rows of the sighted sweep were this one blind spot, not 15 gaps — the census
# reporting the READER'S vocabulary as the TREE'S debt.
#
# ⚑⚑ THE FOURTH INSTANCE OF ONE SHAPE IN THIS FILE: a hardcoded spelling standing in for a
# population. The default roster, the dispatch idiom, the prose exclusion, and now the suite name.
# A reader keyed on a single spelling reports itself.
SUITE = ("_selftest", "selftest", "_cases")


@dataclass(frozen=True, slots=True)
class Mode:
    """One advertised mode and whether a case exercises it."""

    tool: str
    mode: str
    covered: bool

    @property
    def route(self) -> str:
        """Return what would close this row."""
        return f"add a selftest case for {self.mode}"


def _code_only(source: str) -> str:
    """Return the source with docstrings blanked, so prose cannot advertise a mode.

    ⚑⚑⚑ A READER THAT SCANS SOURCE TEXT MATCHES ITS OWN DOCUMENTATION. MEASURED: this module and
    `tool_dispatch` both reported a mode `--x`, which occurs ONLY inside a docstring EXPLAINING
    the dispatch pattern — `pycodemod --literal -- --x` returns one site, role `doc`, no code.
    A comment describing the shape registered as an instance of the shape.

    ⚑⚑ THE STRUCTURAL FIX, NOT AN EXCLUSION LIST. Naming the two offending files would need a new
    entry per file that ever documents a flag, and would still admit the next one; blanking
    docstrings removes the whole class, because prose is never a dispatch wherever it appears.
    `gate_population` records the same distinction one level out — the instrument is not its
    subject — and reaches it by EXCLUDING ITSELF BY NAME, which this does not have to.

    ⚑⚑ COMMENTS ARE BLANKED TOO, AND LEAVING THEM WAS A MEASURED MISTAKE. I reasoned that a `#`
    comment is dropped by the tokenizer before any dispatch could read it, so it could not carry a
    live flag — true of the PROGRAM, irrelevant to a reader that scans TEXT. This file's own
    comments explaining `TABLE_RE` contain `{"--x": fn}`, and it kept reporting `--x` after
    docstrings were blanked. The tokenizer gives the spans, so no lexer is reimplemented.

    ⚑ AND `--literal` CANNOT ARBITRATE THIS: it reports string CONTENTS and returned a single
    `doc` site while the detector still matched, because the surviving text was in a comment it
    does not read. Two readers disagreeing is the signal that one of them has a bound.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source

    spans: list[tuple[int, int]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        first = node.body[0] if node.body else None
        if (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
            and first.end_lineno is not None
        ):
            spans.append((first.lineno, first.end_lineno))

    lines = source.splitlines(keepends=True)
    for start, end in spans:
        for i in range(start - 1, min(end, len(lines))):
            lines[i] = "\n"
    return _uncommented("".join(lines))


def _uncommented(source: str) -> str:
    """Return the source with `#` comments blanked.

    ⚑ THE SPANS COME FROM THE TOKENIZER, which already distinguishes a comment from a `#` inside
    a string. A regex for `#.*$` would blank the hash in a URL or a format string and silently
    drop a real dispatch line with it.

    ⚑⚑ SEPARATE FROM THE DOCSTRING PASS BECAUSE `C901` SAID SO, and it was right for the reason it
    is always right here: two kinds of thing in one function. Prose-in-a-string and
    prose-after-a-hash are found by different machinery.
    """
    import io  # noqa: PLC0415 — local, so importing this module costs nothing
    import tokenize  # noqa: PLC0415

    out = source.splitlines(keepends=True)
    try:
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type == tokenize.COMMENT:
                row = token.start[0] - 1
                if row < len(out):
                    out[row] = out[row][: token.start[1]] + "\n"
    except (tokenize.TokenError, IndentationError):
        return source
    return "".join(out)


def advertised(source: str) -> tuple[str, ...]:
    """Return the modes a tool's dispatch branches on.

    ⚑ THE DISPATCH IS THE AUTHORITY, not the usage block. A mode the self-description omits is
    still a mode a caller can invoke, and it is exactly the one least likely to have a case.

    ⚑ `finditer`, NOT `findall`: the group of a match object is typed, where `findall` hands back
    an untyped list that carries `Any` into every set operation downstream.

    ⚑⚑ BOTH IDIOMS, UNIONED. Reading only the `in sys.argv` chain reported every table-dispatched
    tool as having NO modes — an absence where the truth was a gap, which is the direction that
    hides work rather than inventing it.
    """
    code = _code_only(source)
    found = {match.group(1) for match in DISPATCH_RE.finditer(code)}
    found |= {match.group(1) for match in TABLE_RE.finditer(code)}
    return tuple(sorted(found - EXEMPT))


def suite_body(source: str) -> str:
    """Return the selftest function's source, or empty when there is none.

    ⚑⚑ THE EXTENT COMES FROM THE AST. A regex slice to the next top-level `def` swallows anything
    the function precedes — including, in the sharpest case, the CLI dispatch itself, which makes
    every mode read as covered by its own declaration.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ""
    # ⚑ EVERY MATCH IS UNIONED, NOT THE FIRST. This package splits a suite into a `selftest`
    # runner and a `_cases` builder, and the mode is usually exercised in the second; returning
    # the first match would make coverage depend on which name a file defines first.
    return "\n".join(
        ast.get_source_segment(source, node) or ""
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in SUITE
    )


def covers(body: str, mode: str) -> bool:
    """Report whether a suite body exercises one mode.

    ⚑ TWO SPELLINGS COUNT. A case may name the flag or call the function the flag dispatches to,
    and a reader knowing only the first reports a covered mode as a gap.
    """
    if mode in body:
        return True
    call = re.escape(mode.lstrip("-").replace("-", "_"))
    return bool(re.search(rf"\b{call}\s*\(", body))


def suite_files(path: Path) -> tuple[Path, ...]:
    """Return the files that may hold a tool's cases, the tool itself first.

    ⚑⚑⚑ A SPLIT SUITE IS THE COMMON CASE, AND READING ONE FILE REPORTS IT AS TOTAL ABSENCE.
    MEASURED: reading `pycodemod.py` alone called 70 of its modes uncovered, and `--calls` — one
    of them — has nine sites in `_pycodemod_selftest.py`. **That is a fact about the METHOD
    reported as a fact about the tool**, and at that scale it would read as a catastrophe rather
    than as a broken predicate.

    ⚑ THE SIBLINGS ARE FOUND BY NAME, NOT LISTED. `<stem>_selftest.py` and `_<stem>_selftest.py`
    are the two spellings this tree uses; a roster of which tools split their suites would be the
    frozen set this whole item is about.
    """
    stem = path.stem
    here = path.parent
    found = [path]
    found.extend(here / f"{shape}.py" for shape in (f"{stem}_selftest", f"_{stem}_selftest"))
    return tuple(where for where in found if where.exists())


def modes(path: Path, label: str) -> tuple[Mode, ...]:
    """Read every advertised mode in one tool and whether a case exercises it."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ()

    bodies = []
    for where in suite_files(path):
        try:
            bodies.append(suite_body(where.read_text(encoding="utf-8", errors="replace")))
        except OSError:
            continue
    body = "\n".join(bodies)
    return tuple(
        Mode(tool=label, mode=mode, covered=covers(body, mode)) for mode in advertised(source)
    )


def population(tools: tuple[str, ...], root: Path | None = None) -> tuple[Mode, ...]:
    """Read every advertised mode across the named tools."""
    where = root if root is not None else corpus.ROOT
    out: list[Mode] = []
    for rel in tools:
        out.extend(modes(where / rel, rel))
    return tuple(out)


def uncovered(rows: tuple[Mode, ...]) -> tuple[Mode, ...]:
    """Return the modes no case exercises."""
    return tuple(row for row in rows if not row.covered)


def by_tool(rows: tuple[Mode, ...]) -> dict[str, tuple[str, ...]]:
    """Group modes by the tool advertising them — a reading, not the population."""
    out: dict[str, list[str]] = {}
    for row in rows:
        out.setdefault(row.tool, []).append(row.mode)
    return {tool: tuple(found) for tool, found in sorted(out.items())}


def render(rows: tuple[Mode, ...]) -> str:
    """Render the census, naming what an empty population means."""
    if not rows:
        return "  no advertised mode read — UNMEASURED, not clean"

    missing = uncovered(rows)
    if not missing:
        return f"  every one of {len(rows)} advertised mode(s) is exercised"

    grouped = by_tool(missing)
    head = (
        f"  {len(missing)} of {len(rows)} advertised mode(s) have no selftest case, "
        f"across {len(grouped)} tool(s):"
    )
    out = [head]
    out.extend(f"    ⚑ {tool}  {' '.join(found)}" for tool, found in grouped.items())
    return "\n".join(out)


def rostered(root: Path | None = None) -> tuple[str, ...]:
    """Return every package module that could advertise a mode.

    ⚑⚑⚑ THE DEFAULT ROSTER WAS TWO HARDCODED SCRATCH TOOLS, WHICH IS THE DEFECT THIS MODULE'S OWN
    DOCSTRING CONDEMNS. It says of its origin: *"a hand-written roster passes the moment it covers
    today's modes and stays silent on the one added tomorrow — the guard-from-the-instance defect,
    whose whole signature is that the guard's population IS the fixed set"* — then diagnoses that
    the origin *"hardcodes four tool paths"*. The repair moved the roster to an ARGUMENT and left
    a two-element literal as the CLI default, so a bare run measured two scratch tools and
    reported on the package not at all.

    ⚑⚑ SO THE POPULATION IS DERIVED FROM THE DIRECTORY, not listed. A module that gains a mode
    tomorrow is in the census tomorrow, with nothing to maintain — which is the property the
    argument-passing repair was reaching for and the default undid.

    ⚑ SUITES ARE EXCLUDED BECAUSE THEY ARE THE CASES, not tools owing them. Counting a
    `*_selftest.py` would ask every suite to exercise its own `--selftest`, the tautology `EXEMPT`
    already removes one level up.
    """
    where = root if root is not None else corpus.ROOT
    return tuple(
        sorted(
            f"substrate/{found.name}"
            for found in (where / "substrate").glob("*.py")
            if not found.name.endswith("_selftest.py")
        )
    )


if __name__ == "__main__":
    _tools = tuple(sys.argv[1:]) or rostered()
    sys.stdout.write(render(population(_tools)) + "\n")
    sys.exit(0)
