#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Census the names whose CASING contradicts their KIND (Ⓝ128b ⟡wrap-the-lowercase-class).

⚑⚑ THE SUBJECT IS THE EDGE BETWEEN TWO FACTS, NOT EITHER ONE. A name census reports
spellings and a kind census reports classes; neither alone can say that `dialect` is a CLASS
bound to a lowercase name. That contradiction is a property of the PAIR — the shape
`the-fact-may-be-an-edge-not-a-property` records — and it is what trips `N801` (class not
CapWords), `N802` (function not lowercase) and `N815` (mixedCase) at any call site that spells
the symbol directly.

⚑⚑ IT IS RUN OVER SOMEONE ELSE'S LIBRARY, WHICH IS WHY IT IS A CENSUS AND NOT A LINT RULE.
`ruff` enforces this on OUR source, where a finding is a defect to fix. Over a third-party
package the same finding is a fact to WRAP: the library's spelling is not ours to change, so
the census answers *which names must a wrapper module own* — and a clean run answers *a single
alias suffices*. Both are answers; neither is a defect in the library.

⚑⚑ IT EXISTS BECAUSE THE ALTERNATIVE WAS AN ASSUMPTION. The brief that commissioned it named
`dialect` and said MEASURE FIRST, DO NOT ASSUME IT IS THE ONLY ONE — and a wrapper sized from
one remembered name is sized from the method, not from the surface. `toolmodes --find` reports
no mode answering this question over 610 declared modes, so the honest response was to build
the reader rather than to eyeball an `__init__`.

⚑⚑⚑ AND THE SOURCE READER ALONE REPORTED ZERO ON ITS OWN MOTIVATING CASE. Run over
`sqlalchemy/dialects/postgresql/__init__.py`, the AST census returned *0 contradict, 3
module-level names* — and `dialect` was one of the three, classified `agrees`. Two independent
reasons, both fatal to the source-only method: the line is `dialect = psycopg2.dialect`, whose
value is an ATTRIBUTE rather than a bare name, so one-hop resolution has nothing to resolve;
and the ~90 names the package re-exports arrive by `from .types import …`, which binds a
module-level name the reader never saw. A census that answers zero on the case it was built
for is `census-green-is-a-fact-about-the-census`, measured here before it was written down.

⚑⚑ SO THE AUTHORITY IS THE IMPORTED MODULE, NOT ITS SOURCE — the same split
`check_stub_authority` enforces by running `stubtest`. DEFINED-IN and EXPORTED-FROM are
different questions and only the runtime answers the second; asking the live object whether it
is a class settles the point for a name bound to another module's attribute, which no amount of
parsing this file can. The AST reader is KEPT for the case where importing is unwanted or
impossible, and the two are separate entry points so a caller says which question it asks.

⚑ ROWS ARE CLASSIFIED, NEVER SILENTLY FILTERED. A name that AGREES with its kind is counted
and set aside rather than dropped, so the denominator is the POPULATION rather than a judgement
about it — the `module_state` discipline, which exists because a census whose denominator comes
from its own hits cannot distinguish *nothing contradicts* from *nothing was read*.

⚑ MODULE SCOPE ONLY, DELIBERATELY. A method is reached as an attribute and a local never leaves
its frame; neither is a name a consumer spells at an import site, which is the whole subject.

⚑ IT LIVES HERE AND NOT IN `scratch/_pycodemod_census.py`, WHICH OWNS THIS CLASS OF QUERY. That
file carries 924 frozen lint findings and the per-file gate has no partial-credit path, so an
edit adding a clean function to it is refused along with everything already there. The gate's
own refusal names this route: extract the concern into a NEW module written clean in one pass.
Recorded so the placement reads as the gate's instruction rather than as a stray sibling.

Usage: python3 -m substrate.name_casing <path>... [--all]
       python3 -m substrate.name_casing --module <dotted.name> [--all]
"""

from __future__ import annotations

import ast
import importlib
import inspect
import sys
from dataclasses import dataclass
from pathlib import Path

#: The casing conventions a Python name can follow, as PREDICATES rather than as a roster of
#: names. A roster is current only as of its last edit, and the population here is whatever a
#: third-party library happens to export.
CAP = "CapWords"
SNAKE = "snake_case"
UPPER = "UPPER_SNAKE"
OTHER = "other"

#: The kinds a bound name can have. `value` is anything that is neither a class nor callable.
CLASS = "class"
FUNC = "func"
VALUE = "value"

#: What each KIND is conventionally spelled as — the expectation a finding contradicts.
#: ⚑ THE VALUE IS A SET, NOT ONE SPELLING. A module-level binding that is neither a class nor a
#: function is legitimately a constant, an instance or an alias, and collapsing that to one
#: expectation would manufacture a finding on every ordinary re-export.
KIND_CASE = {
    CLASS: frozenset({CAP}),
    FUNC: frozenset({SNAKE}),
    VALUE: frozenset({UPPER, SNAKE, CAP}),
}

#: The verdicts a row can carry. `contradicts` is the population a wrapper must own.
AGREES = "agrees"
CONTRADICTS = "contradicts"


def is_dunder(name: str) -> bool:
    """Report whether a name is an interpreter protocol slot rather than an exported symbol.

    ⚑ A DUNDER IS NOT A NAME A CONSUMER SPELLS. `__all__` and `__version__` are slots the
    interpreter reads; judging their casing would report the language's own convention as a
    finding against the library.
    """
    return name.startswith("__") and name.endswith("__")


@dataclass(frozen=True, slots=True)
class Row:
    """One module-level name, its kind, its casing, and whether those two agree."""

    where: str
    name: str
    line: int
    kind: str
    case: str
    verdict: str

    @property
    def contradicts(self) -> bool:
        """Report whether this name's spelling contradicts what its kind is spelled as."""
        return self.verdict == CONTRADICTS


def name_case(name: str) -> str:
    """Return the casing convention one NAME follows.

    ⚑ A LEADING UNDERSCORE IS STRIPPED, NOT CLASSIFIED. `_Foo` is private `CapWords`, and
    treating the underscore as part of the convention would report every private class as a
    finding — a fact about the predicate, not about the name.

    ⚑ AND `CapWords` REQUIRES NO UNDERSCORE. `PGDialect_psycopg2` is neither `CapWords` nor
    `snake_case`; calling it either would hide that it is a class spelled unlike one. It reads
    as `other`, which is an answer rather than a forced choice between two wrong ones.
    """
    bare = name.lstrip("_")
    if not bare:
        return OTHER
    if bare.isupper():
        return UPPER
    if bare[0].isupper():
        return CAP if "_" not in bare else OTHER
    if bare.islower():
        return SNAKE
    return OTHER


def verdict_for(kind: str, case: str) -> str:
    """Return whether a kind and a casing agree — the one place that comparison is made."""
    return AGREES if case in KIND_CASE.get(kind, frozenset()) else CONTRADICTS


def runtime_kind(obj: object) -> str:
    """Return the KIND of a live object — `class`, `func` or `value`.

    ⚑ THE QUESTION IS ASKED OF THE OBJECT, NOT OF ITS NAME, and that is what the source reader
    cannot do: `dialect` is bound to another module's attribute, so only the imported value
    knows it is a class.

    ⚑⚑ `inspect.isclass`, NOT `isinstance(obj, type)`, AND THE CHOICE WAS MEASURED. Under this
    repo's `disallow_any_expr` the bare builtin `type` is itself an `Any`-bearing expression
    (`type[type]`), so the obvious spelling cannot pass the per-file gate — wrapping it in a
    tuple does not help. `inspect.isclass` is the same predicate with a declared signature. A
    probe holding both spellings side by side reported a finding on exactly one of them.

    ⚑ THE PARAMETER IS `object`, NOT `Any`. `Any` disables checking for every expression
    downstream; `object` is the honest top type — it admits any argument and permits nothing
    without a narrowing, and the two narrowings this needs are available.
    """
    if inspect.isclass(obj):
        return CLASS
    if callable(obj):
        return FUNC
    return VALUE


def exported_names(mod: object) -> list[str]:
    """Return the names a live module presents as its surface, `__all__` first.

    ⚑ THE POPULATION IS WHAT THE MODULE EXPORTS. A package declaring `__all__` has said which
    names are its surface; falling back to `dir()` when it does not is WIDER than the surface
    but never narrower, so a contradiction cannot hide in the gap.

    ⚑ THE `__all__` READ IS NARROWED AT THIS SEAM, DELIBERATELY — the `_captured` discipline
    from `stub_declines`. `getattr` is typed `Any`, so every expression downstream of a raw read
    would inherit it; asserting the element type ONCE, here, is what keeps the caller concrete.
    """
    declared: object = getattr(mod, "__all__", None)
    if isinstance(declared, (list, tuple)):
        return [n for n in declared if isinstance(n, str)]
    return dir(mod)


def _by_name(row: Row) -> str:
    """Return a row's name — the sort key, named so its type is declared."""
    return row.name


def census_module(dotted: str) -> tuple[list[Row], int]:
    """Census the names a live module EXPORTS, resolving each kind from the object itself.

    ⚑ A NAME THAT WILL NOT RESOLVE IS SKIPPED, NOT GUESSED. `getattr` failing means the module
    names something it does not bind, which is a fact about that module rather than a casing
    finding.
    """
    mod: object = importlib.import_module(dotted)
    rows: list[Row] = []
    for nm in exported_names(mod):
        if is_dunder(nm):
            continue
        try:
            obj: object = getattr(mod, nm)
        except AttributeError:
            continue
        kind = runtime_kind(obj)
        case = name_case(nm)
        rows.append(Row(dotted, nm, 0, kind, case, verdict_for(kind, case)))
    return sorted(rows, key=_by_name), 1


def bound_kind(tree: ast.Module, name: str) -> str:
    """Return what KIND a module-level name is bound to, by reading the same file.

    ⚑ ONE HOP, NOT A FIXPOINT. A chain of aliases is rare, and following it would make the
    answer depend on traversal order rather than on the source. An attribute value
    (`x = mod.thing`) resolves to nothing here — the documented limit that made the runtime
    reader necessary, not a defect in this one.
    """
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == name:
            return CLASS
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return FUNC
    return VALUE


def _named(tree: ast.Module, node: ast.stmt) -> list[tuple[str, str, int]]:
    """Return the `(name, kind, line)` triples one module-level statement binds."""
    if isinstance(node, ast.ClassDef):
        return [(node.name, CLASS, node.lineno)]
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return [(node.name, FUNC, node.lineno)]
    if isinstance(node, ast.Assign):
        kind = bound_kind(tree, node.value.id) if isinstance(node.value, ast.Name) else VALUE
        return [(t.id, kind, node.lineno) for t in node.targets if isinstance(t, ast.Name)]
    return []


def read_source(src: str, where: str) -> list[Row]:
    """Census one module's SOURCE, classifying every module-level name it binds."""
    try:
        tree = ast.parse(src, filename=where)
    except (SyntaxError, ValueError):
        return []
    rows: list[Row] = []
    for node in tree.body:
        for nm, kind, line in _named(tree, node):
            if is_dunder(nm):
                continue
            case = name_case(nm)
            rows.append(Row(where, nm, line, kind, case, verdict_for(kind, case)))
    return rows


def census(paths: list[Path]) -> tuple[list[Row], int]:
    """Census every path given, returning the rows and how many files were READ.

    ⚑ THE SECOND RETURN IS THE POPULATION, NOT THE HIT COUNT. A census whose denominator comes
    from its own hits cannot distinguish *nothing contradicts* from *nothing was read*, which is
    the false-zero this repo keeps recording.
    """
    rows: list[Row] = []
    read = 0
    for p in paths:
        try:
            src = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        read += 1
        rows += read_source(src, str(p))
    return rows, read


def _render(rows: list[Row], read: int, *, show_all: bool, unit: str) -> None:
    """Print the contradicting rows, with the agreeing population counted beside them."""
    bad = [r for r in rows if r.contradicts]
    for r in rows if show_all else bad:
        at = f"{r.where}:{r.line}" if r.line else r.where
        sys.stdout.write(f"  {r.verdict:<11} {r.kind:<5} {r.case:<11} {at}  {r.name}\n")
    sys.stdout.write(
        f"name-casing: {len(bad)} name(s) contradict their kind, of {len(rows)} "
        f"name(s) in {read} {unit}\n"
    )
    if not read:
        sys.stdout.write("   ⚑ NOTHING READ — the scope matched nothing.\n")


def main(argv: list[str]) -> int:
    """Census a module by import, or a set of files by source."""
    show_all = "--all" in argv
    if "--module" in argv:
        rest = argv[argv.index("--module") + 1 :]
        dotted = next((a for a in rest if not a.startswith("-")), None)
        if dotted is None:
            sys.stderr.write("usage: python3 -m substrate.name_casing --module <dotted>\n")
            return 2
        rows, read = census_module(dotted)
        _render(rows, read, show_all=show_all, unit="module(s)")
        return 0
    given = [a for a in argv if not a.startswith("-")]
    if not given:
        sys.stderr.write("usage: python3 -m substrate.name_casing <path>... [--all]\n")
        return 2
    rows, read = census([Path(g) for g in given])
    _render(rows, read, show_all=show_all, unit="file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
