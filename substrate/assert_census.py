#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Census `assert` statements by whether `-O` deleting one would remove a CONSEQUENCE.

⚑⚑⚑ THE COUNT IS NOT THE READING, AND A COUNT ALONE ANSWERS THE WRONG QUESTION. `S101` bans
`assert` because `python -O` deletes every one of them, and `pyproject.toml` exempts a path on
the grounds that the exempted code is never run that way. Whether that exemption is safe does not
turn on HOW MANY asserts a path holds — it turns on whether any of them is the only thing standing
between a caller and a wrong answer. So this classifies rather than counts, and the classification
is the deliverable.

⚑⚑ THE DISTINCTION IS *WHAT ELSE DEPENDS ON THE ASSERT*, AND IT IS DECIDABLE FROM STRUCTURE.

    ARM        the assert IS the thing being run — it sits inside a function whose own name
               marks it as a case, or inside a module the discovery convention names a suite.
               `-O` deleting it makes the case vacuous, which is a REPORTING defect (the suite
               says 8/8 having checked nothing) — bad, but it does not corrupt a caller.
    LOAD       something downstream depends on the assert having held: it narrows a type the
               following lines read, guards a write, or stands between a parse and its use.
               `-O` deleting it changes what the surrounding code DOES.

⚑ THE `LOAD` SIDE IS WHERE THE EXEMPTION IS ACTUALLY EXERCISED, and it is the one a count hides:
a path holding a thousand arms and one narrowing assert reads as overwhelmingly safe by volume
and is unsafe at exactly one line.

⚑⚑ AND THE PREDICATE NAMES WHAT IT CANNOT DECIDE, rather than defaulting the undecidable into
whichever bucket makes the answer cleaner. `unresolved()` is the roster (`substrate.attr_reads`
established this shape): an assert whose consequence is carried by a name this walk cannot follow
is reported as its own kind, never silently graded ARM. Reading an `unknown` count as zero-risk
is the false-zero this module exists to refuse.

⚑ IT IS A READING, NOT A GATE. Nothing here edits, and nothing here deletes an assert: a
`-O`-fragile assert is a finding to NAME for an operator, because removing it is a decision about
the surrounding code's contract that a census is not entitled to make.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path

from substrate import corpus

# The kinds an assert is graded into. ⚑ CONSTANTS, because three readers dispatch on them and a
# bare string at each site is the census-keyed-on-one-spelling defect one layer down.
ARM, LOAD, UNKNOWN = "arm", "load", "unknown"

# The suffix `suite_discovery` uses to name a suite module — the same convention `suite_emit`
# reads. ⚑ AN ASSERT IN A SUITE MODULE IS AN ARM BY LOCATION, whatever its shape.
SUITE_SUFFIX = "_selftest"

# Function-name markers that make a body a case rather than production code. A `test_` prefix is
# pytest's own convention, which the declared migration makes live here.
_CASE_PREFIXES = ("test_", "selftest", "check_")

# Names whose binding an assert may be NARROWING for the lines that follow. An
# `assert isinstance(x, T)` is read by a type checker and by every later read of `x`; deleting it
# under `-O` leaves those reads unguarded.
_NARROWING = frozenset({"isinstance", "issubclass"})

# What this census structurally cannot see. ⚑ A TUPLE OF WHOLE SENTENCES, one per line, because
# a wrapped entry read as two is the same shape as a roster that drifts from its reader.
_UNRESOLVED = (
    "unparseable-file — a file that does not parse is skipped, not reported",
    "generated-assert — an assert built by exec/compile at runtime has no statement here",
    "excluded-tree — corpus.excluded() drops vendored, generated and snapshot trees",
    "aliased-narrowing — narrowing reached via an alias or attribute is not matched by name",
    "cross-function-consequence — a caller depending on an arm's assert is an EDGE, not a site",
)


@dataclass(frozen=True, slots=True)
class Site:
    """One `assert` statement, graded by what deleting it would remove."""

    path: str
    line: int
    kind: str
    why: str


@dataclass(frozen=True, slots=True)
class Scope:
    """Where an assert sits — the two containment facts that decide ARM.

    ⚑ A RECORD RATHER THAN TWO BOOLEAN PARAMETERS. The gate refuses boolean positionals, and it
    is right to: `_grade(path, True, False, node)` at a call site says nothing about which
    containment is which, and the two are exactly the pair a reader would transpose.
    """

    in_case: bool
    in_suite: bool


def _is_case_function(name: str) -> bool:
    """Report whether a function's own name marks its body as a case."""
    return name.startswith(_CASE_PREFIXES)


def _narrows(test: ast.expr) -> bool:
    """Report whether the asserted expression narrows a name later lines read.

    ⚑ THE CALL IS MATCHED ON ITS BARE NAME, WHICH OVER-REPORTS, and that direction is chosen.
    A local shadowing `isinstance` would be graded LOAD wrongly; the opposite error grades a real
    narrowing as an arm and hides it. An over-report costs a reader one adjudication; an
    under-report is the thing this census exists to prevent.

    ⚑⚑ AN IDENTITY COMPARISON NARROWS ONLY AGAINST `None`, AND ADMITTING ALL OF THEM MADE THE
    CENSUS REPORT ITS OWN PREDICATE. A first cut read every `is`/`is not` as narrowing, so
    `assert may_write() is False` — a pytest arm CHECKING a return value, with no name to narrow
    — graded LOAD, and the reading over `tests/` came back five-for-five LOAD with not one real
    guard among them. That is the over-report crossing from *costs a reader an adjudication* into
    *is the entire finding*: every site a reader was told to look at was an artifact of the rule.
    `x is None` narrows `x` for the lines after it; `f() is False` narrows nothing.
    """
    for node in ast.walk(test):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in _NARROWING
        ):
            return True
        if (
            isinstance(node, ast.Compare)
            and any(isinstance(op, (ast.Is, ast.IsNot)) for op in node.ops)
            and any(isinstance(c, ast.Constant) and c.value is None for c in node.comparators)
        ):
            return True
    return False


def _grade(path: str, scope: Scope, node: ast.Assert) -> Site:
    """Grade one assert by what its deletion would remove."""
    if _narrows(node.test):
        return Site(path, node.lineno, LOAD, "narrows a name the following lines read")
    if scope.in_suite:
        return Site(path, node.lineno, ARM, "in a suite module")
    if scope.in_case:
        return Site(path, node.lineno, ARM, "in a case function")
    return Site(path, node.lineno, UNKNOWN, "at module or production scope with no narrowing call")


def _walk(path: str, tree: ast.AST, scope: Scope) -> list[Site]:
    """Return every assert in one parsed file, each graded.

    ⚑ THE ENCLOSING FUNCTION IS TRACKED BY DESCENT, not by a second pass keyed on line ranges.
    A line-range join is a second derivation of containment and disagrees at a decorator.
    """
    found: list[Site] = []

    def descend(node: ast.AST, here: Scope) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                descend(
                    child,
                    Scope(
                        in_case=here.in_case or _is_case_function(child.name),
                        in_suite=here.in_suite,
                    ),
                )
            elif isinstance(child, ast.Assert):
                found.append(_grade(path, here, child))
            else:
                descend(child, here)

    descend(tree, scope)
    return found


def graded(path: str, text: str) -> list[Site]:
    """Return every graded assert in one file's SOURCE TEXT.

    ⚑ THE TEXT IS A PARAMETER SO A CASE CAN PIN THE PREDICATE ON A LITERAL. A suite that could
    only reach this through the corpus walk would have to name a live file, and an arm naming a
    live file expires the day that file is edited — measured four times in this repo.
    """
    return _walk(
        path,
        ast.parse(text, filename=path),
        Scope(in_case=False, in_suite=path.endswith(SUITE_SUFFIX + ".py")),
    )


def sites(*roots: str) -> list[Site]:
    """Return every graded assert under the given roots. Defaults to the whole corpus."""
    out: list[Site] = []
    for path in corpus.py_files(*roots):
        try:
            text = Path(path).read_text(encoding="utf-8", errors="replace")
            out.extend(graded(path, text))
        except (OSError, SyntaxError):
            continue
    return out


def unresolved() -> tuple[str, ...]:
    """Return what this census structurally CANNOT see — read beside every zero.

    ⚑⚑ A ZERO HERE IS A FACT ABOUT THE WALK BEFORE IT IS A FACT ABOUT THE TREE. Each entry names
    a way an assert, or a consequence of one, escapes this reading entirely; a reader taking a
    zero without them is reading the instrument.
    """
    return _UNRESOLVED


def tally(found: list[Site]) -> dict[str, int]:
    """Return the per-kind counts."""
    return {kind: sum(1 for s in found if s.kind == kind) for kind in (ARM, LOAD, UNKNOWN)}


def _order(site: Site) -> tuple[str, str, int]:
    """Return the sort key for a named site — kind, then path, then line."""
    return (site.kind, site.path, site.line)


def render(found: list[Site]) -> str:
    """Return the census as text: the counts, then every non-ARM site by name.

    ⚑ THE ARMS ARE COUNTED AND THE OTHERS ARE NAMED. An arm's deletion is a reporting defect a
    reader handles in bulk; a LOAD or UNKNOWN site is a line someone must look at, and a count
    of those is exactly the shape that lets a reader act on a number instead of a location.
    """
    counts = tally(found)
    head = ", ".join(f"{k}={counts[k]}" for k in (ARM, LOAD, UNKNOWN))
    lines = [f"assert census: {len(found)} site(s) — {head}"]
    named = [s for s in found if s.kind != ARM]
    if named:
        lines.append("")
        lines.extend(f"  {s.kind:<7} {s.path}:{s.line}  {s.why}" for s in sorted(named, key=_order))
    lines.append("")
    lines.append("⚑ this census cannot see:")
    lines.extend(f"    {note}" for note in unresolved())
    return "\n".join(lines) + "\n"


def usage() -> str:
    """Return what this module does and how to ask it."""
    return (
        "assert_census reads which `assert` statements would lose a CONSEQUENCE under -O.\n"
        "\n"
        "usage: assert_census.py <root> [<root> ...]   # census those roots\n"
        "       assert_census.py --all                 # census the whole corpus\n"
        "       assert_census.py --selftest\n"
    )


# ⚑ A ROOT IS REQUIRED OR `--all` IS, rather than defaulting a bare run to the whole corpus. A
# minutes-long unasked-for walk is the other half of the silent-exit-0 defect: a reader cannot
# tell a slow answer from a hang.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        from substrate import assert_census_selftest

        sys.exit(assert_census_selftest.selftest())
    _args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not _args and "--all" not in sys.argv:
        sys.stderr.write(usage())
        sys.exit(2)
    sys.stdout.write(render(sites(*_args)))
    sys.exit(0)
