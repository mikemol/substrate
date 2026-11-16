#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Compose every extracted ratchet module's own selftest into one tally.

⚑⚑ THE ROSTER IS THE MODULES THEMSELVES. The original `_selftest` was 139 statements
inside `ratchet.py` — a `PLR0915` finding that was really saying the cases and the code
under test were sharing a module. Each extracted capability now owns its own cases and
this only composes them.

⚑⚑⚑ AND THAT ARGUMENT WAS MADE BY A HAND-TYPED ROSTER, WHICH IS THE SAME DEFECT ONE LEVEL
UP (⟡derive-the-roster). The docstring here used to claim *"a new module cannot be silently
left uncovered the way a hand-typed roster once omitted `BaselineState.UNREAD`"* — true of
the CASES it replaced, and false of itself: it was a hand-typed roster of MODULES, and a
module whose suite existed but was not listed was silently uncomposed with nothing to say
so. The membership is now DERIVED and only the ORDER is typed.

⚑⚑ THE MEMBERSHIP COMES FROM `scripts/ratchet.py`, WHICH IS THE EXTRACTION MANIFEST. That
facade exists to re-export every capability ⟡ratchet-seams took out of the monolith, and its
module-level `from substrate.<mod> import ...` lines ARE the list of what was extracted —
maintained, load-bearing, and consumed by twenty-two files. Deriving from it means adding a
capability to the facade composes its suite here with no edit to this file, and it makes the
two rosters incapable of disagreeing. Read via `import_edges.module_level_dotted` (AST, never
an import), because several modules in this corpus execute work at import.

⚑ THE SUITE SIBLING IS DISCOVERED, NOT ASSUMED — `suite_discovery.is_suite` over
`<mod>_selftest.py` (⟡selftest-discovery). A facade member with no suite sibling is simply
not a member here; a member whose sibling exists but does not answer `--selftest` is not
composed, and `suite_gap_report` is the reader that reports it as uncovered.

⚑ AND IT IS ITS OWN FILE BECAUSE `ratchet.py` REFUSED WITH IT INLINE. A `PLC0415` on the
deferred import was the harness saying, for the fourth time in this arc, that the file
was doing two things — being a re-export surface AND holding a test roster. Importing
seven modules at the top of a compatibility shim would also make every consumer of
`ratchet` pay for the test tree at import time.
"""

from __future__ import annotations

import importlib
import sys
from typing import TYPE_CHECKING, Protocol, cast

from mikemol.corpus import import_edges, suite_discovery

from substrate import corpus

if TYPE_CHECKING:
    from pathlib import Path

# The facade whose module-level imports declare what was extracted. ⚑ ONE SPELLING, READ FROM
# HERE — a roster keyed on a path typed at several sites is the census-keyed-on-one-spelling
# shape inside the derivation built to remove it.
MANIFEST = ("scripts", "ratchet.py")

# The package the extracted modules live in, the suite-sibling convention, and the callable
# each sibling must expose.
PACKAGE = "substrate"
SUITE_SUFFIX = "_selftest"
ENTRY = "selftest"

# ⚑ ORDERED LEAF-FIRST, so a failure names the deepest broken module rather than the
# composition that noticed. `ratchet_log` has no dependencies; `ratchet_core` exercises all of
# them together and therefore runs last. THIS IS THE ONLY HAND-TYPED THING LEFT, and it is
# typed because it is a JUDGEMENT — the dependency order among the extracted capabilities is
# not derivable from the facade, which imports them as a flat set.
#
# ⚑⚑ AND THE LEAF-FIRST CLAIM IS NOW GATED, NOT ASSERTED (⟡gate-the-order). Completeness was
# already checked — every discovered member is placed, or `UnorderedSuiteError` fires — while
# SOUNDNESS was a comment. `inversions()` reads each placed capability's own module-level
# imports and reports every `(importer, imported)` pair the order puts backwards; the suite
# pins it at zero over the live tree, and against a fixture whose inversion is KNOWN, which is
# what separates "found no violation" from "computed no edges". A hand-typed judgement is not
# thereby unverifiable: it is underivable, which is a different word.
#
# ⚑⚑ IT NAMES THE CAPABILITY, NOT THE SUITE MODULE, AND THAT IS WHY THE SPLIT BROKE IT THREE
# TIMES (⟡n-split-the-tails). The old roster named `<module>.selftest` by hand, so moving
# `ratchet_log.selftest` to `ratchet_log_selftest.selftest` raised an `AttributeError` AT
# IMPORT — taking down `scripts/ratchet.py` and every one of the sixteen gates that imports
# it. **A split is not done when the module is clean; it is done when its CONSUMERS are
# repointed** — and a registry of callables is a consumer no coverage census can see, because
# it reads names, not suites. Naming the capability makes the sibling convention the one
# authority on where its cases live, so the next split moves nothing here.
#
# ⚑⚑⚑ `ratchet_render` IS HERE BECAUSE THE DERIVATION FOUND IT ON ITS FIRST RUN, AND ITS
# ABSENCE IS THE EXACT DEFECT ⟡derive-the-roster WAS DISPATCHED AGAINST. The facade re-exports
# it (`Report`), `ratchet_render_selftest.py` passes, and the hand-typed roster of seven simply
# never named it — silently uncomposed, with nothing in the tree able to say so. It was not
# caught by review, by the coverage census, or by the three splits that broke this file in one
# hour; it was caught the moment membership stopped being typed. **A roster that omits a member
# is not a smaller roster, it is a green one that tests less** — and the count going 7 → 8 is
# the finding, not a regression.
#
# ⚑ ITS POSITION IS A JUDGEMENT LIKE EVERY OTHER ROW HERE, not an append. It imports no other
# extracted capability (`sys`, `dataclasses`, `pathlib` only), so it is a LEAF beside
# `ratchet_log`; and `ratchet_core` renders through `Report`, so it must precede the aggregate.
# Placed among the leaves rather than at the end — which is what the refusal exists to force.
#
# ⚑⚑⚑ AND `ratchet_suites` IS ITSELF A ROW, WHICH THE DERIVATION FOUND THE INSTANT THIS MODULE
# GAINED A SUITE (⟡cover-the-composer). The facade re-exports `run_all` from here, so the moment
# `ratchet_suites_selftest.py` existed this module became a discovered member its own ORDER did
# not place — `UnorderedSuiteError` fired before a single case ran. The composer is a composed
# capability like any other, and nothing had ever typed that fact; the derivation did not have to
# be told. Its position is LAST, after `ratchet_core`: its arms call `members()` and `suites()`
# over the live tree, so it is the only row that depends on every other row being resolvable.
# ⚑ IT DOES NOT RECURSE — the sibling's cases exercise the derivation, never `run_all`.
ORDER = (
    "vlogs_destination",
    "ratchet_flags",
    "proc_ancestry",
    "withheld_verdict",
    "baseline_state",
    "baseline_io",
    "ratchet_core",
    "ratchet_suites",
)


class Suite(Protocol):
    """The part of a suite sibling this composition uses.

    ⚑ THE SHAPE IS DECLARED, WHICH IS WHAT MAKES THE DYNAMIC IMPORT CHECKABLE. `import_module`
    returns a bare `ModuleType`, so every attribute off it is `Any` — an unchecked value walking
    into the roster. Naming the one member consulted narrows it to a call this file's own type
    check can verify, the same move `import_manifest.Classifier` makes for its codemod tool.
    """

    def selftest(self) -> int:
        """Run this module's cases; 0 when they all pass."""
        ...


class UnorderedSuiteError(RuntimeError):
    """A discovered member the ORDER does not place.

    ⚑ RAISED, NOT APPENDED. Constraint 1 of ⟡derive-the-roster: a reader must be able to tell
    "ordered deliberately" from "fell to the end because nobody said". Silently appending
    makes those two indistinguishable and puts an unjudged module in the position that is
    load-bearing — last, where `ratchet_core` belongs. Refusing names the module and the
    one-line repair, which is cheaper than a wrong order nobody can see.

    ⚑ THE MESSAGE IS BUILT HERE, NOT AT THE RAISE SITE. `TRY003`/`EM102` refused the reverse
    and were right for this file specifically: the repair instruction is part of what the
    refusal IS, so it belongs with the type rather than at whichever call site noticed.
    """

    def __init__(self, unordered: tuple[str, ...]) -> None:
        """Name the unplaced modules and the one-line repair."""
        super().__init__(
            f"{', '.join(unordered)} — re-exported by {'/'.join(MANIFEST)} with a "
            f"{SUITE_SUFFIX} suite, but ORDER does not place it. Add it to ORDER at its "
            f"leaf-first position; the order is a judgement, so it cannot be derived."
        )


class NoEntryPointError(AttributeError):
    """A member module discovery accepted that exposes no `selftest`.

    ⚑ A LOUD REFUSAL AT COMPOSITION, WHICH IS THE PROPERTY THE HAND-TYPED ROSTER HAD AND MUST
    NOT LOSE. Constraint 2 of ⟡derive-the-roster: that roster could not be stale and green at
    the same time, because naming a moved suite raised `AttributeError` at import. A `cast`
    alone would type-check a module with no entry point and defer the failure to call time;
    `getattr(..., None)` would SKIP it — a false green, the
    `census-green-is-a-fact-about-the-census` failure this repo has banked before. This keeps
    the original loudness and adds the module name and the diagnosis the bare one lacked.
    """

    def __init__(self, module: str) -> None:
        """Name the module whose split left no entry point."""
        super().__init__(
            f"{PACKAGE}.{module}{SUITE_SUFFIX} answers --selftest but defines no {ENTRY!r} — "
            f"a split that moved the cases without leaving the entry point its composer calls"
        )


def manifest_path(root: Path | None = None) -> Path:
    """Return the facade whose imports declare the extracted membership."""
    return (root if root is not None else corpus.ROOT).joinpath(*MANIFEST)


def extracted(root: Path | None = None) -> frozenset[str]:
    """Return the capability modules `scripts/ratchet.py` re-exports from `substrate`.

    ⚑ MODULE-LEVEL ONLY. A deferred import inside a function is not part of the facade's
    surface, and unioning the two readings would compose a suite for a capability the facade
    does not actually re-export — `import_edges` keeps the two apart for exactly this reason.
    """
    prefix = f"{PACKAGE}."
    return frozenset(
        name[len(prefix) :]
        for name in import_edges.module_level_dotted(str(manifest_path(root)))
        if name.startswith(prefix) and "." not in name[len(prefix) :]
    )


def has_suite(module: str, root: Path | None = None) -> bool:
    """Report whether a capability's `_selftest` sibling IS a suite.

    ⚑ `suite_discovery` OWNS THE PREDICATE. Testing for the file's existence, or for a `def
    selftest`, would be a second authority on what a suite is — and this repo has measured that
    predicate wrong in both directions, with the under-admitting direction costing more.
    """
    base = (root if root is not None else corpus.ROOT) / PACKAGE
    path = base / f"{module}{SUITE_SUFFIX}.py"
    try:
        return suite_discovery.is_suite(path.read_text(encoding="utf-8"))
    except OSError:
        return False


def members(root: Path | None = None) -> tuple[str, ...]:
    """Return the composed capability names, leaf-first.

    Raises `UnorderedSuiteError` when discovery finds a member `ORDER` does not place.
    """
    found = {mod for mod in extracted(root) if has_suite(mod, root)}
    unordered = tuple(sorted(found - set(ORDER)))
    if unordered:
        raise UnorderedSuiteError(unordered)
    return tuple(mod for mod in ORDER if mod in found)


def member_edges(root: Path | None = None) -> dict[str, frozenset[str]]:
    """Return, per ORDER-placed capability, which OTHER placed capabilities it imports.

    ⚑ THE CAPABILITY'S OWN SOURCE, NOT ITS SUITE'S. The order being checked is the order the
    CAPABILITIES depend on each other in; a suite sibling imports the module under test by
    construction, so reading siblings would report an edge that says nothing about depth.

    ⚑ MODULE-LEVEL ONLY, the same reading `extracted` uses. A deferred import fires when the
    function runs, not when the module loads, so it is not a load-order constraint — and
    `import_edges` keeps the two apart precisely so a caller cannot merge them by accident.

    ⚑ IT RANGES OVER `ORDER`, NOT OVER `members()`. A capability whose suite is absent is not
    composed, but it is still a node the order places, and an edge through it is still a fact
    about the judgement typed here. Restricting to composed members would make the check
    weaken exactly when a suite goes missing.
    """
    base = (root if root is not None else corpus.ROOT) / PACKAGE
    placed = set(ORDER)
    prefix = f"{PACKAGE}."
    edges: dict[str, frozenset[str]] = {}
    for name in ORDER:
        path = base / f"{name}.py"
        if not path.exists():
            continue
        imported = import_edges.module_level_dotted(str(path))
        edges[name] = frozenset(
            dotted[len(prefix) :]
            for dotted in imported
            if dotted.startswith(prefix)
            and dotted[len(prefix) :] in placed
            and dotted[len(prefix) :] != name
        )
    return edges


def inversions(root: Path | None = None) -> tuple[tuple[str, str], ...]:
    """Return every `(importer, imported)` pair where ORDER is NOT leaf-first.

    ⚑⚑ THIS IS THE ARM THE LEAF-FIRST COMMENT NEVER HAD. `ORDER` is hand-typed and stays that
    way — dependency order is a JUDGEMENT, not derivable from the facade's flat import set —
    but the judgement has a checkable CONSEQUENCE: if A imports B, B must run first, so that a
    failure names the DEEPEST broken module rather than the composition that noticed. Membership
    was already gated; soundness of the order was asserted by comment and verified by nothing.

    ⚑ A PAIR, NOT A BOOLEAN. The repair is per-edge — move B above A — so the reader needs the
    edge, not the news that one exists somewhere in nine rows.
    """
    rank = {name: i for i, name in enumerate(ORDER)}
    edges = member_edges(root)
    return tuple(
        sorted(
            (importer, imported)
            for importer, imports in edges.items()
            for imported in imports
            if rank[imported] > rank[importer]
        )
    )


def suite(module: str) -> Suite:
    """Import one member's suite sibling, narrowed to the entry point it owes.

    ⚑ THE PRESENCE CHECK RUNS BEFORE THE NARROWING, AND THAT ORDER IS THE CONTRACT. `cast` is
    a claim, not a verification — it would hand back a module with no `selftest` and let the
    failure surface later, somewhere less legible. Asking first turns the claim into something
    the composition has actually checked.

    ⚑ `hasattr`, NOT `getattr` AND NOT `mod.__dict__`. Both of those yield an `Any` this file's
    own type check refuses — correctly, because the point is to ASK whether the name is bound
    and only the boolean is wanted. Reaching for the VALUE in order to test for it is what
    drags the unchecked type in, and it is also the shape one keystroke from the
    `getattr(..., None)` skip the constraint forbids.
    """
    mod = importlib.import_module(f"{PACKAGE}.{module}{SUITE_SUFFIX}")
    if not hasattr(mod, ENTRY):
        raise NoEntryPointError(module)
    return cast("Suite", mod)


def suites(root: Path | None = None) -> tuple[Suite, ...]:
    """Return each member's suite module, in composition order."""
    return tuple(suite(name) for name in members(root))


def run_all() -> int:
    """Run every module suite; return 1 if any failed."""
    roster = suites()
    failures = sum(1 for member in roster if member.selftest() != 0)
    sys.stdout.write(f"ratchet: {len(roster) - failures}/{len(roster)} module suite(s) passed\n")
    return 1 if failures else 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS COMPOSITION — see `baseline_io`
# (⟡selftest-discovery). This one is the aggregate, so the runner would count its member
# suites a second time; that is correct and deliberate, because the composition ORDER is itself
# under test (leaf-first, so a failure names the deepest broken module rather than the
# composition that noticed) and nothing else exercises it.
if __name__ == "__main__":
    sys.exit(run_all() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
