#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.module_outline`: the outline it claims, on sources built here.

⚑⚑⚑ THIS TOOL'S CORRECTNESS IS LOAD-BEARING IN A WAY MOST TOOLS' IS NOT. It is the answer to
"what names does this callee have", and it is invoked precisely when the asker has NOT read the
file. A wrong outline therefore cannot be caught by the reader who consumes it — they act on it,
call a name that does not exist, and attribute the miss to the callee. Every other census in this
package is checked against a file the reader can open; this one is trusted instead of opened.

⚑⚑ THE FIXTURES ARE SOURCE STRINGS BUILT HERE, NOT LIVE MODULES. Arms naming a real file pin an
INSTANCE and expire the moment that file is edited — which has happened four times in this
package. A source built inside the case pins the PROPERTY (a decorated def's span starts at the
`def` line; a nested def is not a peer) and cannot rot, because the fixture and the claim move
together.

⚑ AND EVERY ARM CARRIES A DISCRIMINATOR — a shape the predicate must REJECT. An outline suite
that only asserts "the expected names are present" passes on an implementation that returns every
name it can find, including the nested closures the header says are excluded; the exclusion is
only observable by asserting the absence of a name the parser demonstrably SAW. So the fixture
deliberately contains what must not be reported: a nested def, a `def` inside a string literal,
and a name bound in a class body rather than at module level.
"""

from __future__ import annotations

import sys

from mikemol.witness import witness_family

from substrate import module_outline, suite_emit

# ⚑ ONE FIXTURE CARRYING EVERY DISTINCTION, so the arms disagree about the SAME source rather
# than each testing a source built to suit it. It holds, in order: a decorated def (span must
# start at `def`, not at the decorator); a class with a method and a class-body assignment
# (neither is a module-level entry); a `def` inside the module docstring (no parser sees it as a
# def); an async def; module-level assignments both bare, unpacked and annotated.
_SRC = '''\
"""Module docstring.

Not a definition:
def decoy_in_a_docstring():
    pass
"""
TABLE = {1: 2}
LIMIT: int = 3
UNPACKED_A, UNPACKED_B = 4, 5


@staticmethod
def decorated(x):
    """Summary of decorated."""
    def nested_closure():
        return x
    return nested_closure


class Holder:
    """Summary of Holder."""

    CLASS_LEVEL = 7

    def method(self):
        return None


async def waits():
    """Summary of waits."""
    return None
'''

# The entries the fixture must produce, in source order: kind, name, first line, last line.
# ⚑ THE SPANS ARE THE HALF A NAME-LIST CANNOT CHECK, and the module's own header says ranking by
# lines-carried is the reason it reports them at all.
_WANT = (("def", "decorated", 13, 17), ("class", "Holder", 20, 26), ("def", "waits", 29, 31))

# Names the parser demonstrably SAW and must NOT report as module-level entries.
_MUST_NOT_APPEAR = ("nested_closure", "decoy_in_a_docstring", "method")

# The module-level bindings, in order. ⚑ `CLASS_LEVEL` IS ABSENT BY DESIGN — a class-body
# assignment is not a module constant, and a split that moved it would be moving a class field.
_WANT_CONSTANTS = ("TABLE", "LIMIT", "UNPACKED_A", "UNPACKED_B")

# The docstring summaries the fixture's definitions must yield.
_WANT_SUMMARIES = (
    ("decorated", "Summary of decorated."),
    ("Holder", "Summary of Holder."),
    ("waits", "Summary of waits."),
)

# The kind each fixture definition must carry.
_WANT_KINDS = (("decorated", "def"), ("Holder", "class"), ("waits", "def"))

# `(first, last, inclusive_length)`. ⚑ THE ONE-LINE CASE IS THE DISCRIMINATOR: inclusive and
# exclusive counting differ by the entire answer there, and an exclusive count renders a
# definition as zero lines — sorting it last in a ranking whose whole job is finding what to cut.
_SPAN_CASES = ((10, 10, 1), (10, 14, 5))

# A source that is not python at all, for the arm that pins what an unparseable file does.
_BROKEN = "def (:\n"


def every_module_level_definition_is_reported_with_its_span(out: list[str]) -> int:
    """Check kind, name and line span for each module-level definition, in source order.

    ⚑ THE SPAN IS CHECKED AS `lineno`/`end_lineno`, NOT ONLY AS A LENGTH. A length alone passes
    on an outline shifted wholesale by the decorator line, which is the exact off-by-one the
    module's header argues about — a decorated def's span must start at `def`.
    """
    bad = 0
    got = tuple((e.kind, e.name, e.lineno, e.end_lineno) for e in module_outline.outline(_SRC))
    if got != _WANT:
        out.append(f"selftest: outline is {got}, want {_WANT}")
        bad += 1
    return bad


def lines_counts_both_endpoints(out: list[str]) -> int:
    """Check that the reported length is inclusive of the first and last line of the span."""
    bad = 0
    for first, last, want in _SPAN_CASES:
        got = module_outline.OutlineEntry("def", "f", first, last, "").lines
        if got != want:
            out.append(f"selftest: lines {first}..{last} spans {got}, want {want}")
            bad += 1
    return bad


def a_nested_or_quoted_or_class_scoped_def_is_not_an_entry(out: list[str]) -> int:
    """Check that only module-level statements are reported.

    ⚑⚑ THIS IS THE ARM A PERMISSIVE IMPLEMENTATION FAILS AND NO OTHER ARM CATCHES. Every name
    here is inside the fixture and reachable by a scanner: a closure, a `def` inside the module
    docstring, and a method. Reporting any of them invents a promotion candidate that cannot be
    promoted alone and double-counts its lines against its enclosing definition.
    """
    bad = 0
    names = {e.name for e in module_outline.outline(_SRC)}
    for forbidden in _MUST_NOT_APPEAR:
        if forbidden in names:
            out.append(f"selftest: {forbidden!r} was reported as a module-level entry")
            bad += 1
    return bad


def a_class_is_distinguished_from_a_def(out: list[str]) -> int:
    """Check that the kind field separates classes from functions, async included.

    ⚑ THE DISCRIMINATOR IS THE ASYNC DEF. An implementation matching only `ast.FunctionDef`
    drops it entirely, and one matching "anything with a body" would call the class a def —
    two opposite bugs that a single kind assertion distinguishes.
    """
    bad = 0
    kinds = {e.name: e.kind for e in module_outline.outline(_SRC)}
    for name, want in _WANT_KINDS:
        if kinds.get(name) != want:
            out.append(f"selftest: {name} has kind {kinds.get(name)!r}, want {want!r}")
            bad += 1
    return bad


def module_constants_are_the_module_level_bindings_only(out: list[str]) -> int:
    """Check the constant list: order, tuple unpacking, annotation, and the class-body exclusion.

    ⚑ A SPLIT THAT MOVES A FUNCTION AND LEAVES ITS TABLE BEHIND PRODUCES AN IMPORT BACK INTO THE
    FILE IT WAS CUT FROM — the edge the promotion existed to cut. So both directions matter: a
    missed module binding strands a table, and a reported CLASS field names something that is not
    a module constant at all and cannot be moved on its own.
    """
    bad = 0
    got = tuple(module_outline.module_constants(_SRC))
    if got != _WANT_CONSTANTS:
        out.append(f"selftest: constants are {got}, want {_WANT_CONSTANTS}")
        bad += 1
    if "CLASS_LEVEL" in got:
        out.append("selftest: a class-body assignment was reported as a module constant")
        bad += 1
    return bad


def the_summary_is_the_first_docstring_line_or_empty(out: list[str]) -> int:
    """Check the summary field, including the no-docstring case.

    ⚑ THE DISCRIMINATOR IS `decorated`, whose docstring is followed by more source: an
    implementation returning the whole docstring, or the line after it, differs from the first
    line only on a multi-statement body. And a definition with NO docstring must yield the empty
    string rather than the module's, which is what `ast.get_docstring` returns from the wrong
    node.
    """
    bad = 0
    summaries = {e.name: e.summary for e in module_outline.outline(_SRC)}
    for name, want in _WANT_SUMMARIES:
        if summaries.get(name) != want:
            out.append(f"selftest: summary of {name} is {summaries.get(name)!r}, want {want!r}")
            bad += 1
    plain = module_outline.outline("def f():\n    return None\n")
    if plain[0].summary != "":
        out.append(f"selftest: an undocumented def summarized as {plain[0].summary!r}, want ''")
        bad += 1
    return bad


def an_unparseable_source_raises_rather_than_reporting_nothing(out: list[str]) -> int:
    """Check that a source the tool cannot parse REFUSES instead of returning an empty outline.

    ⚑⚑ AN EMPTY OUTLINE AND AN UNPARSEABLE FILE ARE OPPOSITE FACTS AND MUST NOT SHARE A
    RENDERING. `[]` means "this module defines nothing"; a `SyntaxError` means "this instrument
    could not read it". Collapsing the second into the first is a census zero reporting the
    boundary of the METHOD as a fact about the substrate — and this tool is consulted exactly
    when the asker will not open the file to notice.
    """
    bad = 0
    for fn in (module_outline.outline, module_outline.module_constants):
        try:
            fn(_BROKEN)
        except SyntaxError:
            continue
        out.append(f"selftest: {fn.__name__} accepted unparseable source instead of raising")
        bad += 1
    return bad


def the_cli_refuses_an_unknown_flag_and_a_missing_operand(out: list[str]) -> int:
    """Check that `main` refuses rather than silently treating a flag as a path.

    ⚑⚑ THE MEASURED DEFECT: `--selftest` was read as a PATH, so the flag every other tool in
    this package answers made this one crash with a file-not-found. A tool that accepts an
    operand it cannot honour is indistinguishable from one that honoured it — the same shape as
    a gate degraded by a typo'd flag, and the third operand-discard found in this package today.
    """
    bad = 0
    if module_outline.main([]) == 0:
        out.append("selftest: main([]) reported success with no operand")
        bad += 1
    if module_outline.main(["--nonesuch"]) == 0:
        out.append("selftest: main() accepted an unknown flag")
        bad += 1
    return bad


FAMILY = witness_family.of(
    key="module_outline",
    apex="the outline reports every module-level definition with an inclusive span, its kind "
    "and its summary, reports the module-level bindings only, and refuses what it cannot "
    "parse rather than rendering it as an empty module",
    subject="`substrate.module_outline` over source strings built inside the suite",
    members=(
        witness_family.Member(
            name="every_module_level_definition_is_reported_with_its_span",
            claim="kind, name and line span match, in source order",
        ),
        witness_family.Member(
            name="lines_counts_both_endpoints",
            claim="the reported length is inclusive of both endpoints",
            cases=2,
        ),
        witness_family.Member(
            name="a_nested_or_quoted_or_class_scoped_def_is_not_an_entry",
            claim="a closure, a def inside a string, and a method are not outline entries",
            cases=3,
            premises=("every_module_level_definition_is_reported_with_its_span",),
        ),
        witness_family.Member(
            name="a_class_is_distinguished_from_a_def",
            claim="the kind field separates classes from functions, async included",
            cases=3,
        ),
        witness_family.Member(
            name="module_constants_are_the_module_level_bindings_only",
            claim="bare, unpacked and annotated module bindings, and no class-body field",
            cases=2,
        ),
        witness_family.Member(
            name="the_summary_is_the_first_docstring_line_or_empty",
            claim="the summary is the first docstring line, empty when there is none",
            cases=4,
        ),
        witness_family.Member(
            name="an_unparseable_source_raises_rather_than_reporting_nothing",
            claim="an unreadable source refuses rather than rendering as an empty outline",
            cases=2,
        ),
        witness_family.Member(
            name="the_cli_refuses_an_unknown_flag_and_a_missing_operand",
            claim="the command line refuses a flag rather than reading it as a path",
            cases=2,
        ),
    ),
)

_ARMS = (
    every_module_level_definition_is_reported_with_its_span,
    lines_counts_both_endpoints,
    a_nested_or_quoted_or_class_scoped_def_is_not_an_entry,
    a_class_is_distinguished_from_a_def,
    module_constants_are_the_module_level_bindings_only,
    the_summary_is_the_first_docstring_line_or_empty,
    an_unparseable_source_raises_rather_than_reporting_nothing,
    the_cli_refuses_an_unknown_flag_and_a_missing_operand,
)

_CASE_COUNT = FAMILY.count

_SELF_KEY = "substrate/module_outline_selftest.py"


def selftest() -> int:
    """Run every arm, report by typed record, and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_SELF_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
