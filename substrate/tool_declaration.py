#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""How a tool DECLARES its modes — five shapes, read from source, never by running it.

⚑⚑⚑ THE CENSUS USED TO RUN EVERY TOOL AS A SUBPROCESS, AND THAT WAS NOT MERELY SLOW — IT
EXECUTED THE PRE-COMMIT GATES (operator, 2026-08-22: *"toolmodes needs to operate not by
launching all of the other tools. That's incredibly expensive… especially since some of those
tools actually do work when invoked, regardless of parameters passed"*). MEASURED: a single
`--find` invoked `gate_status.py` bare, which ran the gate suite, which spawned `run_selftests`
TWICE — each fanning the whole suite out under `membudget` — plus four more gates and a
per-row fork. Dozens of processes, per call, on a tool whose job is answering *"which tool has
this mode"*.

⚑⚑ NEITHER PARSER EVER NEEDED A SUBPROCESS. `parse_usage` and `parse_options` are pure
functions of TEXT; only the text was subprocess-derived, and both halves are in the source. The
argument was already written in the file, applied to the roster and not to the census.

⚑⚑⚑ FIVE DECLARATION SHAPES, AND FOUR WERE FOUND BY BREAKING THE FIFTH. Launching rendered
whatever a tool chose to print, so the census never had to know HOW a tool declares. Reading
source does, and each shape surfaced as a regression:

  1. the module `__doc__` usage block — the assumed one
  2. argparse `add_argument(...)` — reconstructed here rather than rendered and re-parsed
  3. a module-level `_MODES = (("--flag", "gloss"), …)` — `schema.py`; found when `--widest`
     went UNDOCUMENTED on the first static run
  4. a usage string built INSIDE `__main__` — `agda_defs.py` keeps a 9-line docstring and
     prints its real mode list from a 1,057-line guard
  5. a dict of flag → CONSTRUCTOR — `pycodemod.MODES = {"--calls": Mode(...)}`, the
     `Arm`/`Convention` model from gcalculus `farm.py`

⚑ SHAPE 5 IS THE RICHEST AND WOULD HAVE BEEN THE QUIETEST MISS. `Mode` declares not just the
argument shape but the BEHAVIOUR a branch owes (`scans=True` implies it owes an incomplete-scan
report). Its own note states the principle — *"the load-bearing field is the one a discriminator
can CHECK"* — so a census that reads glosses and skips contracts reads the least informative
half of the best-declared tool.

⚑⚑ AND A SINGLE-LINE `print` ROSTER IS SHAPE 4 AGAIN, WHICH THE OBVIOUS FILTER HID.
`agda_defs.py` prints its roster as one triple-quoted block, so a multi-line-constant test finds
it; `sppf_db.py` prints the SAME roster as ~40 consecutive one-line `print("  --flag  gloss")`
calls, every constant single-line — so that filter excluded the whole block and the census read
ZERO usage-declared modes. The misreading it produced is the point: `--find promote-core`
answered *"named in sppf_db.py's own output, declared by NO tool"* — both clauses true and
jointly absurd, since `make` runs `--promote-core` on every module of a full build.

⚑ A REFUSAL IS NOT A DECLARATION, and the first cut of that loop conflated them. `schema.py`
refuses a half-stated mutation with `print("schema.py --coverage --reap: state --dry-run OR
--apply …")`, and reading that as a usage line promoted `--reap` to a TOP-LEVEL MODE — exactly
the defect that file's own roster records having fixed once. The discriminator is the `:`
separator, which is this toolkit's refusal shape, plus the STREAM: a tool describes itself on
stdout and complains on stderr.

⚑ `rc` IS GONE AND THAT IS A REAL LOSS, NAMED. A launched run distinguished "printed a usage
block" from "crashed" from "timed out"; a source read cannot. The one consumer — the
NO SELF-DESCRIPTION label — is preserved structurally, since a tool whose source yields no usage
line still reports as undescribed. What is genuinely gone is the ability to say a tool TIMED OUT,
and that is a property of the TOOL rather than of this reader.

⚑ EXTRACTED FROM `scratch/toolmodes.py` (⟡toolmodes-layers), 2,196 findings, refused whole by
the per-file gate. The cut continues until the dispatch moves out and the original is retired.
"""

from __future__ import annotations

import ast
import re

from substrate import tool_usage

# A flag that is the WHOLE string — the test for a roster key, as opposed to a flag mentioned
# inside prose.
FLAG_EXACT = re.compile(r"^--[A-Za-z][A-Za-z0-9-]*$")

# This toolkit's refusal shape: `tool.py <modes>: <what went wrong>`. ⚑ THE `:` IS THE
# DISCRIMINATOR — a declaration separates its gloss with three spaces or `#`, never a colon.
REFUSAL = re.compile(r"\s*\S+\.py\b[^:]*:")

# The header this module EMITS for a reconstructed roster.
OPTIONS_HEAD = "options:"

# ⚑⚑⚑ THREE HEADER SPELLINGS, AND READING ONLY THE FIRST MADE A WHOLE FILE'S MODES INVISIBLE.
# argparse has shipped two (`options:` and the older `optional arguments:`), and this toolkit
# hand-rolls a third (`modes:`) for the same structure. MEASURED: `scripts/gate_census.py`
# publishes a textbook two-column roster under `modes:` and all FIVE of its modes read as
# UNDOCUMENTED; an agent adding `--init-absent` checked, saw its four siblings read the same
# way, and correctly concluded the PARSER was the narrower thing.
#
# ⚑⚑ AND THE MISS WAS SILENT IN BOTH DIRECTIONS AT ONCE, which is why it survived: `--find`
# reported the flags as declared by NO tool, while `--divergence` did not list the file AT ALL,
# because the unparsed roster text lands in `mentioned` as prose. Two modes of one census
# disagreeing about one file, each internally consistent.
#
# ⚑ I DROPPED IT ON THE FIRST CUT OF THIS MODULE and the parity run caught it — 3 tools, every
# disagreement `only-origin`, i.e. modes LOST. That is the dangerous direction, and a suite
# written against this module alone would have passed: the fixtures spell a header the parser
# already knows, which is the same blind spot the origin records.
OPTIONS_HEADS = re.compile(r"^(options|optional arguments|modes):\s*$")

# One row of that block. ⚑ THE TAIL IS `\s.*`, NOT `[ =]\S.*`: argparse pads a short flag out to
# the help column with a RUN of spaces, so requiring a non-space immediately after the separator
# matched only flags carrying a metavar — silently dropping every store_true option, which is
# most of the mode-shaped ones.
OPTION_ROW = re.compile(r"^  (?:-\w,\s+)?(--[A-Za-z][A-Za-z0-9-]*)(?:\s.*)?$")

# A leading metavar run, which is argument syntax rather than gloss.
METAVAR = re.compile(r"^(?:[A-Z][A-Z0-9_]*(?:\s+|$))+")

# Fewest pairs that make a roster rather than a coincidence, and the arity of one pair.
MIN_PAIRS = 2
PAIR_ARITY = 2

# The keyword a declared-mode constructor carries its gloss in — the same field `Arm`,
# `Convention` and `Decline` all use.
WHY = "why"


def _text_constant(node: ast.AST) -> str | None:
    """Return a string constant's value, or None when the node is not one.

    ⚑ TAKES `AST`, NOT `expr`, BECAUSE BOTH CALLERS EXIST. The roster readers hand it an `expr`
    from a known position; the constant walk hands it whatever `ast.walk` yields. Narrowing the
    parameter would force the walk to assert a shape it has not checked — which is the check
    this function performs.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _pair_rows(node: ast.Tuple | ast.List) -> list[str]:
    """Return roster rows from a `(("--flag", "gloss"), …)` literal, or nothing.

    ⚑ STRUCTURED DATA IS THE BEST OF THE FIVE SHAPES — a declared pair list cannot drift from
    what dispatches the way a hand-written usage paragraph can. So it is matched STRUCTURALLY,
    and a second tool adopting the shape is covered without being named.
    """
    pairs: list[tuple[str, str]] = []
    for element in node.elts:
        if not isinstance(element, (ast.Tuple, ast.List)) or len(element.elts) != PAIR_ARITY:
            return []
        flag, gloss = _text_constant(element.elts[0]), _text_constant(element.elts[1])
        if flag is None or gloss is None or not flag.split()[0].startswith("--"):
            return []
        pairs.append((flag, " ".join(gloss.split())))
    if len(pairs) < MIN_PAIRS:
        return []
    return [f"  {flag}  {gloss}" for flag, gloss in pairs]


def _constructor_rows(node: ast.Dict) -> list[str]:
    """Return roster rows from a `{"--flag": Mode(...)}` declaration, or nothing.

    ⚑ BEING A KEY IN THE ROSTER IS THE DECLARATION, independent of prose. A constructor with no
    `why=` still declares its flag; only the gloss is absent.
    """
    if not node.keys:
        return []
    keys: list[str] = []
    for key in node.keys:
        text = _text_constant(key) if key is not None else None
        if text is None or not FLAG_EXACT.match(text):
            return []
        keys.append(text)
    if not any(isinstance(value, ast.Call) for value in node.values):
        return []

    rows: list[str] = []
    for flag, value in zip(keys, node.values, strict=True):
        gloss = ""
        if isinstance(value, ast.Call):
            for keyword in value.keywords:
                found = _text_constant(keyword.value) if keyword.arg == WHY else None
                if found is not None:
                    gloss = " ".join(found.split())
        rows.append(f"  {flag}  {gloss}" if gloss else f"  {flag}")
    return rows


def _argparse_rows(node: ast.Call) -> list[str]:
    """Return roster rows from one `add_argument(...)` call, or nothing.

    ⚑ MEASURED COVERAGE: 183 of 251 `add_argument` sites in this corpus pass `help=`. The other
    68 render an EMPTY gloss under argparse too, so nothing is lost — an absent `help=` was never
    text this census could read.
    """
    flags = [
        text
        for arg in node.args
        if (text := _text_constant(arg)) is not None and FLAG_EXACT.match(text)
    ]
    if not flags:
        return []
    gloss = ""
    for keyword in node.keywords:
        found = _text_constant(keyword.value) if keyword.arg == "help" else None
        if found is not None:
            gloss = " ".join(found.split())
    return [f"  {flag}  {gloss}" if gloss else f"  {flag}" for flag in flags]


def declared_options(tree: ast.AST) -> str:
    """Return the `options:` block a tool's declarations amount to, or "".

    ⚑ THE SHAPE IS `parse_options`' INPUT, not argparse's exact output. That parser wants
    two-space-indented `  --flag  gloss` rows under a header, and that is all it reads — so this
    emits precisely those and nothing else. Reproducing argparse's wrapping and column alignment
    would be re-implementing a formatter in order to re-parse it, which is the round trip that
    reading source exists to delete.
    """
    rows: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Tuple, ast.List)):
            rows.extend(_pair_rows(node))
        elif isinstance(node, ast.Dict):
            rows.extend(_constructor_rows(node))
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "add_argument"
        ):
            rows.extend(_argparse_rows(node))
    return (OPTIONS_HEAD + "\n" + "\n".join(rows)) if rows else ""


def _is_stderr_call(node: ast.Call) -> bool:
    """Report whether a `print` names stderr — a complaint rather than a description."""
    return any(
        isinstance(keyword.value, ast.Attribute) and keyword.value.attr == "stderr"
        for keyword in node.keywords
        if keyword.arg == "file"
    )


def _printed_usage(tree: ast.AST) -> list[str]:
    """Return single-line string literals printed to stdout that could be usage lines.

    ⚑ THE STRING'S OWN SHAPE IS THE WRONG DISCRIMINATOR; what matters is that the ARGUMENT OF A
    `print` CAN BE a usage line. `parse_usage` still discriminates — a line must NAME the tool
    AND carry a flag — so feeding it every printed literal costs nothing.
    """
    out: list[str] = []
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "print"
        ) or _is_stderr_call(node):
            continue
        for arg in node.args:
            text = _text_constant(arg)
            if text is not None and "--" in text and "\n" not in text and not REFUSAL.match(text):
                out.append(text)
    return out


def _multiline_constants(tree: ast.AST, doc: str) -> list[str]:
    """Return module string constants that look like usage blocks, excluding the docstring.

    ⚑ THE USAGE BLOCK NEED NOT BE `__doc__`. `agda_defs.py` keeps a 9-line docstring and prints
    its real mode list from inside a `__main__` guard, so a docstring-only read lost two modes
    the tool genuinely accepts.
    """
    return [
        text
        for node in ast.walk(tree)
        if (text := _text_constant(node)) is not None
        and "\n" in text
        and "--" in text
        and text != doc
    ]


def self_description(source: str) -> str:
    """Return everything a tool says about its own modes, gathered from its source.

    ⚑ AN UNPARSEABLE SOURCE YIELDS WHAT WAS READABLE rather than raising. A tool mid-edit is a
    state this reader will meet, and a census that died on one file would report nothing about
    the hundreds it could read.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ""

    doc = ast.get_docstring(tree) or ""
    parts = [doc, *_multiline_constants(tree, doc), *_printed_usage(tree)]
    text = "\n".join(part for part in parts if part)

    options = declared_options(tree)
    return text + ("\n\n" + options if options else "")


def parse_options(text: str) -> dict[str, str]:
    """Return `{flag: gloss}` from an `options:` block, if the text carries one.

    ⚑⚑ THE TWO HALVES OF AN ARGPARSE TOOL'S SELF-DESCRIPTION DISAGREE, MEASURED. `tsdbprobe`
    carries its docstring's curated list AND argparse's generated one, and `--ping` is in the
    second and not the first. Reading only the curated half reproduces the stale-index defect
    `pycodemod`'s own docstring records — *"THIS LIST WAS SEVEN MODES SHORT"*. Both are read.

    ⚑ AND THIS IS WHY THE ROSTER ROWS NEED THEIR OWN PARSER. `parse_usage` requires a line to
    NAME the tool, which a roster deliberately factors out into its header — so the two readers
    are not interchangeable, and a `modes_of` using only the first drops every argparse and
    roster declaration. Measured here: five of twelve cases failed on exactly that.
    """
    lines = text.splitlines()
    at = 0
    while at < len(lines) and not OPTIONS_HEADS.match(lines[at].strip()):
        at += 1
    at += 1

    out: dict[str, str] = {}
    while at < len(lines):
        line = lines[at]
        if line and not line.startswith(" "):
            break  # a new unindented section
        found = OPTION_ROW.match(line.rstrip())
        if found is None:
            at += 1
            continue
        parts = [line.rstrip()[found.end(1) :].strip()]
        at += 1
        while at < len(lines):
            wrapped = lines[at]
            if not wrapped.startswith("    ") or OPTION_ROW.match(wrapped.rstrip()):
                break
            parts.append(wrapped.strip())
            at += 1
        # ⚑ THE METAVAR IS ARGUMENT SYNTAX, NOT GLOSS. `--base BASE  store base URL` describes a
        # store URL, not a thing called BASE.
        out[found.group(1)] = METAVAR.sub("", " ".join(part for part in parts if part))
    return out


def modes_of(source: str, stem: str) -> dict[str, tool_usage.Mode]:
    """Return every mode a tool declares, by any of the five shapes.

    ⚑ ONE ENTRY POINT FOR THE WHOLE QUESTION. A caller that read the docstring itself, or walked
    the AST for rosters separately, would be a second reader of a declaration surface that took
    five regressions to map — and the two would disagree the first time either moved.

    ⚑⚑ A USAGE-DECLARED MODE WINS OVER AN OPTION ROW, which is what `setdefault` buys. The usage
    line carries a SIGNATURE (`--attr <name> [paths]`); an option row carries only a gloss, so
    letting the second overwrite the first would silently empty the argument shape the gap and
    sibling reports are computed from.
    """
    text = self_description(source)
    out = dict(tool_usage.parse_usage(text, stem))
    for flag, gloss in parse_options(text).items():
        out.setdefault(flag, tool_usage.Mode(gloss=gloss, sig=()))
    return out
