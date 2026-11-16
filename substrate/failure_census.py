#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The failure census - the build-failed rows of the leaf-verify ledger, partitioned by error kind.

THE SECOND CUT OF THE DRAIN'S FIFTH FILE (`catalog/library/figures.py:736-1000`, W4 tick 59).
The origin's walk composes four things it fetched itself: the ledger rows, the per-module
`.agdai.log`, the freshness test and the classifier. Here every one is a PARAMETER on `Inputs`,
so the walk is a pure function of what it is handed and a suite drives every branch without a
tree - the `agda_build_census.Tree` shape. The origin's memo (an L2 cache keyed on the ledger
stamp) and its two process-local verdict caches stay with the caller: a cache is an adaptor over
a computation, and the computation is what lives here.

THREE RULES THE ORIGIN MEASURED ARE KEPT AS RULES:

- A STALE LOG IS UNMEASURED, NEVER CLASSIFIED. About a third of the error text on disk once
  described a tree that no longer existed; the `build-failed` filter happened to exclude it, and
  the freshness test turns that undeclared coupling into a checked fact. A stale row lands in the
  `stale-log` kind rather than in a confident wrong one.
- THE REMEDY RIDES WITH THE WALK. The classifier returns `(kind, detail, remedy)`; keeping only
  the kind made one consumer re-walk the ledger for the remedy and another hard-code a tool for
  every class. The remedy is a fact about a MODULE, so it lives on the module's row.
- THE REFINED KIND RESOLVES THE REMEDY TABLE. `NotInScope` is three populations with three
  repairs (resolvable / ambiguous / no-definer) and `NoParseForApplication` splits on a fixity
  collision; the classifier has no census context, so the split is applied here and the table is
  read on the split kind. The verdict itself is the repairing tool's (`fix_notinscope.classify`,
  `fix_noparse.classify`), reached through a callable, never re-derived - and with NO LOG there
  is NO REFINEMENT: the unrefined kind is returned rather than a guessed verdict.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING

from substrate.agda_error_class import CLASS_REMEDY

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from substrate.agda_error_class import Verdict
    from substrate.leaf_ledger import Row

# The ledger verdict this census reads.
BUILD_FAILED = "build-failed"
# The kind a row lands in when its log describes an earlier tree.
STALE_LOG = "stale-log"
# The two kinds that refine, and the separator the refined kind carries.
NOT_IN_SCOPE = "other:NotInScope"
NO_PARSE = "other:NoParseForApplication"

# kind -> the modules failing with it, sorted; module -> its remedy, or None.
Census = tuple[dict[str, list[str]], dict[str, str | None]]
# The classifier's own remedy table, read-only so it can be a dataclass default.
REMEDIES: Mapping[str, str] = MappingProxyType(CLASS_REMEDY)
# A source's log path, or None when the build never logged it.
LogOf = Callable[[str], str | None]
# The repairing tool's verdict for a source, or None when it has none.
VerdictOf = Callable[[str], str | None]


def passthrough(kind: str, _rel: str) -> str:
    """Refine nothing - the default refiner."""
    return kind


def refine(kind: str, rel: str, not_in_scope: VerdictOf, no_parse: VerdictOf) -> str:
    """Split the two refinable kinds by the repairing tool's verdict; pass every other kind."""
    if kind == NOT_IN_SCOPE:
        v = not_in_scope(rel)
        return f"{kind}:{v}" if v else kind
    if kind == NO_PARSE:
        v = no_parse(rel)
        return f"{kind}:{v}" if v else kind
    return kind


@dataclass(frozen=True)
class Inputs:
    """Everything the walk reads, supplied by the caller rather than fetched."""

    rows: Sequence[Row]
    log_of: LogOf
    # Return a log's text, or '' when it cannot be read - the classifier takes '' as clean.
    read_text: Callable[[str], str]
    is_fresh: Callable[[str], bool]
    classify: Callable[[str, str], Verdict]
    refine: Callable[[str, str], str] = passthrough
    # The remedy table, read on the REFINED kind.
    remedies: Mapping[str, str] = REMEDIES


def census(inp: Inputs) -> Census:
    """Partition the build-failed rows by refined kind, each module carrying its remedy."""
    by_kind: dict[str, list[str]] = {}
    remedy: dict[str, str | None] = {}
    for rel, verdict, _cited in inp.rows:
        if verdict != BUILD_FAILED:
            continue
        if not inp.is_fresh(rel):
            by_kind.setdefault(STALE_LOG, []).append(rel)
            continue
        log = inp.log_of(rel)
        kind, _detail, r = inp.classify(rel, inp.read_text(log) if log else "")
        kind = inp.refine(kind, rel)
        remedy[rel] = r or inp.remedies.get(kind)
        by_kind.setdefault(kind, []).append(rel)
    return {k: sorted(v) for k, v in by_kind.items()}, remedy


def kinds(c: Census) -> list[str]:
    """Return every kind present - the discovered roster, never a list anyone maintains."""
    return sorted(c[0])


def modules(c: Census, kind: str) -> list[str]:
    """Return a COPY of the modules failing with `kind` - a shared list is a shared bug."""
    return list(c[0].get(kind, []))


def parts(c: Census, kind: str) -> list[tuple[str, str | None]]:
    """Return [(module, remedy | None)] for `kind` - each part with its own remedy."""
    by_kind, remedy = c
    return [(m, remedy.get(m)) for m in by_kind.get(kind, [])]
