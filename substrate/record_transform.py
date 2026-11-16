#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The `NamedTuple` → slotted-dataclass transform, as a matcher-decorated libcst codemod.

⚑⚑⚑ EVERY HANDLER IS DECORATED AND SNAKE_CASE, AND THAT IS A CORRECTNESS CHOICE, NOT A STYLE ONE.
libcst dispatches a CONCRETE handler by NAME — `getattr(self, f"visit_{type(node).__name__}", None)`
(`libcst/_visitors.py:42`) — and a name that does not match returns `None`, so `on_visit` returns
True, children are visited, and the codemod exits 0 having changed NOTHING. A mis-bound concrete
handler is SILENT, and across 67 files "nothing changed" reads as "nothing to do".

The decorated path fails the other way. `MatcherDecoratableTransformer.__init__` runs `_check_types`
over every `@m.visit`/`@m.leave` handler, so a malformed one raises `MatchDecoratorMismatch` at
INSTANTIATION (`libcst/matchers/_visitors.py:470-481`). Loud, before any file is read.

⚑⚑ AND libcst FORBIDS THE CONCRETE NAME ON A DECORATED METHOD — `_assert_not_concrete` (`:321`)
raises if the method is called `visit_ClassDef`. So snake_case here is not a workaround for ruff's
N802: it is the shape the library requires of a decorated handler, and the two agree.

⚑ THE MATCHER MUST BE INSTANTIATED: `@m.visit(m.ClassDef())`, never `@m.visit(m.ClassDef)`. The
decorator stamps the matcher OBJECT onto the function, and a bare class stamps the wrong thing.

⚑⚑ THE RESIDUAL THIS CANNOT CLOSE, stated because it is the one that stays silent: a WRONG matcher
(`m.FunctionDef()` where `m.ClassDef()` was meant) binds correctly and fires on the wrong node. The
signature check cannot see it. A control that asserts *"something fired"* cannot see it either —
it must plant a known node PER HANDLER and assert that node carries the mutation only that handler
produces, which is read-your-write applied to a visitor.

⚑⚑⚑ THE TRANSFORM MUST LEAVE A FILE THE GATE ACCEPTS, WHICH IS MORE THAN LEAVING IT CORRECT. Two
bugs found by running this against `tool_cli.py` and reading the checker's report BEFORE writing:
the added import landed after `typing` (ruff `I001`, un-sorted) and `NamedTuple` stayed in the
`typing` import with no remaining use (`F401`). Both produce a CORRECT conversion that CANNOT LAND,
and both were invisible until the prospective output was checked.

⚑ WHAT THIS DOES NOT DO, the load-bearing limit (`codemod_store_reads`' shape): the mechanical
rewrite only, with everything a rewrite cannot DECIDE reported as a work list.

  * A KEYLESS `sorted`/`min`/`max` over a converted record. Under `NamedTuple` that compared by
    FIELD POSITION — an order nobody wrote down. MEASURED in `tool_gap.capability_gaps`: it led
    with `relpath`, so it happened to be alphabetical, and a field reorder would have changed the
    answer silently. What the order should BE is a judgement, so it is FLAGGED. ⚑ And `order=True`
    is never emitted: it would restore exactly the by-position comparison being removed.
  * A NUMERIC SUBSCRIPT identifying something. MEASURED in `tool_convention_audit.required_pairs`:
    `mutation[0], mutation[1]` chose which half of a mutually-exclusive contract was which, so a
    reorder would have named the wrong flag as defaulting. Naming each position needs a human.
"""

from __future__ import annotations

import libcst as cst
import libcst.matchers as m
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand

# What every converted record carries. ⚑ NO `order=True` — see the module note.
DECORATOR = "dataclass(frozen=True, slots=True)"

# The import a converted module needs, and the module it comes from.
DATACLASS_IMPORT = "from dataclasses import dataclass"
DATACLASSES = "dataclasses"

# ⚑⚑⚑ THE PLACEMENT LOGIC THAT USED TO LIVE HERE IS DELETED, AND ITS ABSENCE IS THE FIX.
# Three helpers accumulated — a module-name reader, an isort-order comparison, and a
# leading-blank-line wrapper — each added to satisfy one more `I001` the prospective check
# reported. Together they were a hand-rolled reimplementation of a sorter that ALREADY RUNS in
# this pipeline: `ruff --fix` owns import placement, and the orchestrator invokes ruff on the
# staged file regardless.
#
# Bugs 2, 3 and 4 of this transform were each one more clause of that reimplementation:
#   2. the import appended after `typing`               → I001
#   3. `__future__` alone above it, flush               → I001, opposite cause
#   4. an owned blank line splitting a stdlib group     → I001, opposite cause again
# Three fixes, three new failures, each correct about the case in front of it. **The pattern says
# the APPROACH is wrong, not the placement** — `feedback_fix_infra_not_route_around` (conform to
# the tool; do not rebuild its core), arriving in the middle of a codemod.
#
# So the transform inserts the import at ANY VALID POSITION and `record_migrate` runs `ruff --fix`
# on the staged output before checking it. The sorter decides; this only supplies.


def _dataclass_import() -> cst.SimpleStatementLine:
    """Return the dataclass import, carrying its own blank line above it.

    ⚑⚑ THE BLANK LINE BELONGS TO THE STATEMENT, NOT TO ITS NEIGHBOUR. isort groups imports into
    sections — `__future__`, stdlib, third-party, local — separated by blank lines, and an import
    inserted flush against the wrong section is refused by `I001` even when alphabetically
    correct. MEASURED: once the `typing` import was removed, `__future__` became the only import,
    the new one landed directly beneath it, and ruff refused the file. Owning the leading line
    here means the insertion cannot depend on what happens to precede it.
    """
    line = cst.parse_statement(DATACLASS_IMPORT)
    if not isinstance(line, cst.SimpleStatementLine):
        msg = f"{DATACLASS_IMPORT!r} did not parse as a simple statement"
        raise TypeError(msg)
    # ⚑ ANNOTATED BEFORE IT TRAVELS: a bare list literal handed to `with_changes` infers
    # `list[Any]`, and the `Any` propagates out of the call.
    blank: list[cst.EmptyLine] = [cst.EmptyLine()]
    return line.with_changes(leading_lines=blank)


def _is_import_line(statement: cst.BaseStatement) -> bool:
    """Report whether `statement` IS an import line, not merely one that CONTAINS an import.

    ⚑⚑⚑ THE DISTINCTION THAT COST THIRTEEN FILES. `m.findall(statement, m.ImportFrom())` matches
    the import NESTED INSIDE an `if TYPE_CHECKING:` block, so an anchor computed that way lands on
    the `if` and places the new import AFTER the whole block — outside the import run. `ruff --fix`
    then deletes it as `F401` unused, and the decorator the ClassDef handler added is left
    undefined. MEASURED on `substrate/edge_census.py`: import after transform True, after fix
    False.

    ⚑ SO THIS INSPECTS THE STATEMENT'S OWN BODY rather than searching its subtree. A compound
    statement is never an import line however many imports it holds.
    """
    if not isinstance(statement, cst.SimpleStatementLine):
        return False
    return any(isinstance(part, (cst.Import, cst.ImportFrom)) for part in statement.body)


class SlottedRecords(VisitorBasedCodemodCommand):
    """Rewrite `class X(NamedTuple)` to a frozen slotted dataclass; flag what it cannot decide."""

    DESCRIPTION = (
        "NamedTuple -> @dataclass(frozen=True, slots=True); flags keyless "
        "sorted/min/max and integer subscripts a rewrite must not guess at."
    )

    def __init__(self, context: CodemodContext) -> None:
        """Start with nothing converted and nothing flagged."""
        super().__init__(context)
        self.converted: list[str] = []
        self.flags: list[str] = []
        self._saw_record = False

    @m.leave(m.ClassDef())
    def _convert_record(self, original: cst.ClassDef, updated: cst.ClassDef) -> cst.ClassDef:
        """Drop a `NamedTuple` base and add the dataclass decorator."""
        del original
        if not any(m.matches(base.value, m.Name("NamedTuple")) for base in updated.bases):
            return updated
        self.converted.append(updated.name.value)
        self._saw_record = True
        # ⚑ BOTH SEQUENCES ARE ANNOTATED BEFORE THEY TRAVEL. A bare `[]` or `[*xs, y]` handed
        # straight to `with_changes` infers `list[Any]` and the `Any` propagates out of the call —
        # the same erasure-at-a-dynamic-boundary this arc is about, arriving through a library
        # seam rather than a field access.
        no_bases: list[cst.Arg] = []
        decorators: list[cst.Decorator] = [
            *updated.decorators,
            cst.Decorator(decorator=cst.parse_expression(DECORATOR)),
        ]
        return updated.with_changes(
            bases=no_bases,
            lpar=cst.MaybeSentinel.DEFAULT,
            rpar=cst.MaybeSentinel.DEFAULT,
            decorators=decorators,
        )

    @m.leave(m.ImportFrom(module=m.Name("typing")))
    def _drop_namedtuple_import(
        self, original: cst.ImportFrom, updated: cst.ImportFrom
    ) -> cst.ImportFrom | cst.RemovalSentinel:
        """Drop `NamedTuple` from a `typing` import once no class uses it.

        ⚑⚑ LEAVING IT IS A FINDING, NOT COSMETIC. ruff's `F401` refuses an unused import, so a
        conversion that removes every `NamedTuple` base while keeping the import produces a file
        the gate rejects — correct, and unlandable.

        ⚑ THE WHOLE STATEMENT GOES when `NamedTuple` was its only name: `from typing import` with
        nothing after it is a syntax error, so the choice is remove-the-name or remove-the-line,
        decided by what remains rather than assumed.
        """
        del original
        names = updated.names
        if isinstance(names, cst.ImportStar):
            return updated
        kept = [alias for alias in names if not m.matches(alias.name, m.Name("NamedTuple"))]
        if len(kept) == len(names):
            return updated
        if not kept:
            return cst.RemoveFromParent()
        # ⚑ THE LAST ALIAS MUST SHED ITS TRAILING COMMA, or the statement renders as
        # `from typing import TYPE_CHECKING,` — parseable, and refused by the formatter.
        kept[-1] = kept[-1].with_changes(comma=cst.MaybeSentinel.DEFAULT)
        return updated.with_changes(names=kept)

    @m.visit(m.Call(func=m.Name("sorted") | m.Name("min") | m.Name("max")))
    def _flag_keyless_ordering(self, node: cst.Call) -> None:
        """Flag a comparison with no `key=` — it may be ordering by field position.

        ⚑ FLAGGED, NEVER REWRITTEN. What the order should BE is the judgement; `tool_gap`'s
        keyless sort was alphabetical only because `relpath` happened to be declared first.
        """
        if any(arg.keyword is not None and arg.keyword.value == "key" for arg in node.args):
            return
        name = node.func.value if isinstance(node.func, cst.Name) else "?"
        self.flags.append(
            f"keyless {name}() — under NamedTuple this compared BY FIELD POSITION; "
            f"give the record a named rank() and pass key="
        )

    @m.visit(m.Subscript())
    def _flag_integer_subscript(self, node: cst.Subscript) -> None:
        """Flag an integer subscript — a POSITION standing in for an identity."""
        target = node.value.value if isinstance(node.value, cst.Name) else "?"
        for element in node.slice:
            index = element.slice
            if isinstance(index, cst.Index) and isinstance(index.value, cst.Integer):
                self.flags.append(
                    f"{target}[{index.value.value}] — a POSITION identifying a thing; "
                    f"destructure by name instead"
                )

    @m.leave(m.Module())
    def _add_import(self, original: cst.Module, updated: cst.Module) -> cst.Module:
        """Add the dataclass import in SORTED position when a record was converted.

        ⚑ NEVER ABOVE THE DOCSTRING: a module's first statement is its `__doc__`, which several
        readers in this tree parse for a tool's self-description, and inserting above it would
        demote the docstring to a bare string expression.
        """
        del original
        if not self._saw_record:
            return updated
        if m.findall(updated, m.ImportFrom(module=m.Name(DATACLASSES))):
            return updated
        body: list[cst.BaseStatement] = [*updated.body]
        anchor = None
        for position, statement in enumerate(updated.body):
            if _is_import_line(statement):
                anchor = position
        if anchor is None:
            return updated
        body.insert(anchor + 1, cst.parse_statement(DATACLASS_IMPORT))
        return updated.with_changes(body=body)
