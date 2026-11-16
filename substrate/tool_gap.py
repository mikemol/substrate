#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""What a tool LACKS that a comparable tool has, and where its own claims and code disagree.

⚑⚑⚑ "COMPARABLE" IS THE ROUTING TABLE'S CLAIM COLUMN, NOT A JUDGEMENT. A tool that claims a FILE
artifact is comparable to another that does; a tool claiming a live service is not, so its absence
from a file-corpus family is not a gap. The authority is the same column the PreToolUse gate
reads, which is what keeps this from becoming a list of capabilities someone thought ought to
exist.

⚑⚑ THE DENOMINATOR IS PART OF THE FINDING, NOT DECORATION. A kind carried by MOST of a tool's
modes is that tool's CORPUS ARGUMENT, not a capability: `<file>` is on 6 of `mdstruct`'s 7 modes
because every question it answers names a document, while `<regex>` is on 2 of `agda_defs`' 12
because it is a QUERY. Collapsing both to *"absent on X"* would report `pycodemod` as unable to
take a file — it takes `[paths]`, optionally, on nearly every mode. Reporting the coverage is what
keeps a reader able to tell a gap from a calling convention.

⚑⚑ A FILED-BUT-UNBUILT GAP IS WRITTEN DOWN IN THE TOOL'S OWN OUTPUT, which makes it DERIVABLE
rather than remembered. One tool files `--import-cost` in its prose precisely so the next reader
finds it, and until this arm existed nothing read that. A flag named in prose and declared by NO
tool is either a filed gap or a stale reference — both are work.

⚑⚑ AND THE CROSS-REFERENCE EXCLUSION IS COUNTED RATHER THAN SILENT. This arm always skipped a flag
another tool declares, which is the RIGHT verdict — but a bare `continue` makes the class
invisible, and invisibility is why a sibling report could get the same flag wrong for as long as
it did with nothing to contradict it.

⚑⚑⚑ THE DIVERGENCE CENSUS IS DATA, NOT A PRINTED COUNT, AND THAT SEPARATION IS THE POINT. When it
was computed inline and only rendered, a gate wanting the numbers had two options: re-derive the
predicates — a second spelling of the same logic, the defect this repo has paid for repeatedly —
or parse the printed text, which is judgement-in-the-turn. Neither is acceptable, so the sets are
the authority and the printer consumes them.

⚑ THE KEY IS `<tool> <flag>`, NOT THE FLAG ALONE. `--check` is undocumented on two different tools
and `--dry` on two more; a flag-keyed census would collide them, so paying down one tool would
read as paying down both — a ratchet silently forgiving debt it never saw.

⚑ AND A FIXTURE IS EMITTED, NOT DROPPED. Filtering it here would make an exemption invisible,
which is how a ratchet rots: the gate would show a smaller number with nothing saying why. The
kind travels with the row, the RATCHET declines to count it, and the REPORT still shows it.

⚑ EXTRACTED FROM `scratch/toolmodes.py` (⟡toolmodes-layers), 2,196 findings, refused whole by the
per-file gate. This module COMPUTES; rendering is the caller's.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import tool_convention, tool_decline, tool_overlap, tool_population

if TYPE_CHECKING:
    from substrate.tool_census import Tool

# Fewest tools that make a capability a FAMILY rather than one tool's habit.
FAMILY = 2

# The divergence kinds. ⚑ THREE, AND THE THIRD IS AN EXEMPTION RATHER THAN A DEFECT.
UNDOCUMENTED = "UNDOCUMENTED"
UNBACKED = "UNBACKED"
FIXTURE = "FIXTURE"

# ⚑⚑⚑ SLOTTED DATACLASSES, NOT `NamedTuple`, AND THE DIFFERENCE IS ENFORCEMENT (⟡symbolic-
# reference-only). A `NamedTuple` subclasses `tuple`, so `a, b, c = row` and `row[0]` both work —
# numeric access to a thing that HAS NAMES. A slotted dataclass has neither `tp_iter` nor the
# sequence protocol, so every positional site becomes a STATIC error naming its own line: the
# checker enforces symbolic access rather than it being a convention someone must remember.
#
# SOURCE-CONFIRMED (CPython 3.13.1): `Objects/typeobject.c:type_new_descriptors` installs
# ATTRIBUTE descriptors (`PyMemberDef`, `Py_T_OBJECT_EX`) and touches no
# `tp_iter`/`tp_as_sequence`/`sq_item`; `a, b, c = obj` compiles to `UNPACK_SEQUENCE`
# (`Python/compile.c`), whose `_PyEval_UnpackIterable` (`Python/ceval.c`) opens with
# `PyObject_GetIter` and refuses when there is no iterator and no sequence protocol.
#
# ⚑⚑ AND IT CAUGHT AN UNDECLARED ORDERING IN THIS FILE ON THE FIRST TRY. `capability_gaps` sorted
# `Coverage` values with NO KEY — which under `NamedTuple` meant `tuple`'s field-position
# comparison, `(relpath, modes_with_kind, modes_total, modes)`: an order nobody wrote down,
# existing only as an accident of declaration order, and which a field reorder would have changed
# silently. `Coverage.rank` now STATES it.
#
# ⚑ `order=True` IS DELIBERATELY ABSENT: it would restore exactly that by-position comparison.
# Both records rank by named keys that say what the order MEANS — a per-record call, never a
# package-wide flag.


@dataclass(frozen=True, slots=True)
class Coverage:
    """How much of one tool's surface answers a kind — the denominator a gap needs."""

    relpath: str
    modes_with_kind: int
    modes_total: int
    modes: tuple[str, ...]

    @property
    def is_corpus_argument(self) -> bool:
        """Report whether the kind is on MOST of this tool's modes — a calling convention.

        ⚑ THE DISTINCTION A BARE "ABSENT ON X" DESTROYS. A kind on nearly every mode is how the
        tool takes its corpus, not a capability another tool is missing.
        """
        return bool(self.modes_total) and self.modes_with_kind * 2 > self.modes_total

    def rank(self) -> str:
        """Return the sort key: alphabetical by tool.

        ⚑ NAMED BECAUSE THE ORDER WAS PREVIOUSLY UNSTATED. As a `NamedTuple` this sorted by field
        POSITION, which happened to lead with `relpath` and so happened to be alphabetical — a
        correct-looking result nobody chose, and one a field reorder would have changed with
        nothing to notice.
        """
        return self.relpath


@dataclass(frozen=True, slots=True)
class Gap:
    """One argument KIND some comparable tools answer and others do not."""

    kind: str
    answered_by: tuple[Coverage, ...]
    lacking: tuple[str, ...]

    def rank(self) -> tuple[int, str]:
        """Return the sort key: widest families first, then by kind.

        ⚑ A NAMED METHOD RATHER THAN A LAMBDA, because an untyped sort key makes every element it
        touches `Any` — the untyped-boundary defect arriving through a one-line convenience.
        """
        return (-len(self.answered_by), self.kind)


@dataclass(frozen=True, slots=True)
class Named:
    """A flag a tool NAMES in its own output that no tool declares — filed, or stale."""

    relpath: str
    flag: str


def comparable(rows: tuple[Tool, ...]) -> tuple[str, ...]:
    """Return the tools the routing table names as owning an artifact — the comparable set.

    ⚑ A CELL MAY NAME TWO TOOLS, so membership is tested against every `.py` token in it. Taking
    the cell's basename returns only its LAST path, which silently excluded one of a two-tool row
    — the right answer for the wrong reason, and the wrong one the moment such a row's first entry
    declares modes.

    ⚑ AN UNREACHABLE ROUTING TABLE YIELDS NOTHING, and the caller must report that as UNMEASURED
    rather than as "no tool is comparable" — an empty comparable set makes every gap arm silent,
    which is indistinguishable from a toolkit with no gaps.
    """
    routed = tool_population.routed_names()
    return tuple(tool.relpath for tool in rows if tool.relpath.rsplit("/", 1)[-1] in routed)


def capability_gaps(rows: tuple[Tool, ...]) -> tuple[Gap, ...]:
    """Return each argument kind that some comparable tools answer and others do not.

    ⚑ THE PER-TOOL COVERAGE TRAVELS WITH THE GAP — how many of that tool's modes take the kind,
    out of how many it has. Without it a reader cannot tell a missing CAPABILITY from a different
    CALLING CONVENTION, and the report would name tools that answer the question by another route.
    """
    readers = comparable(rows)
    if len(readers) < FAMILY:
        return ()

    modes_per = {tool.relpath: len(tool.modes) for tool in rows}
    out: list[Gap] = []
    for kind, members in tool_overlap.kind_families(rows).items():
        have = {tool for tool, _mode in members if tool in readers}
        if len(have) < FAMILY:
            continue  # one tool doing it is not yet a family
        lacking = tuple(tool for tool in readers if tool not in have)
        if not lacking:
            continue
        answered = tuple(
            sorted(
                (
                    Coverage(
                        relpath=tool,
                        modes_with_kind=sum(1 for t, _m in members if t == tool),
                        modes_total=modes_per.get(tool, 0),
                        modes=tuple(sorted(mode for t, mode in members if t == tool)),
                    )
                    for tool in have
                ),
                key=Coverage.rank,
            )
        )
        out.append(Gap(kind=kind, answered_by=answered, lacking=lacking))
    return tuple(sorted(out, key=Gap.rank))


def named_but_undeclared(rows: tuple[Tool, ...]) -> tuple[Named, ...]:
    """Return flags a tool names in its own output that NO tool declares.

    ⚑ A CROSS-REFERENCE IS EXCLUDED — and counted by the caller rather than dropped silently. A
    flag another tool declares is the remedy, not the debt, and making that class invisible is
    what let a sibling report get the same flag wrong unchallenged.
    """
    declared = {mode for tool in rows for mode in tool.modes}
    return tuple(
        Named(relpath=tool.relpath, flag=flag)
        for tool in rows
        for flag in sorted(tool.mentioned)
        if flag not in declared
    )


def divergence(rows: tuple[Tool, ...]) -> dict[str, str]:
    """Return `{"<tool> <flag>": kind}` — what a tool claims against what it dispatches.

    ⚑ ONE KEY PER (TOOL, FLAG), because a flag-keyed census collides the same spelling across
    tools and lets one paydown read as two.
    """
    universal = tool_convention.universal(tuple(tool.accepted for tool in rows))
    out: dict[str, str] = {}
    for tool in rows:
        fixtures = tool_decline.fixtures(tool)
        for flag in tool_decline.invisible(tool, universal):
            out[f"{tool.relpath} {flag}"] = FIXTURE if flag in fixtures else UNDOCUMENTED
        for flag in sorted(
            mode for mode in tool.modes if mode.startswith("--") and mode not in tool.literals
        ):
            out[f"{tool.relpath} {flag}"] = UNBACKED
    return out
