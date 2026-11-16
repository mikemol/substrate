#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.store_reach` — the import-closure lens, and the defects it records.

⚑⚑⚑ TWO OF THESE ARMS PIN DEFECTS THE MODULE SAYS IT ALREADY HAD, which is the reason they are
worth writing: a bug fixed without a case is a bug with nothing holding it fixed.

  · THE VISITED SET IS KEYED ON `(module, eager)`, NOT ON THE MODULE. The first cut marked a
    module seen when it was first reached through a `~` hop, so a LATER fully-eager route to the
    same module was discarded and the walk reported the conditional route as the only one. That
    understates what EXECUTES — the direction that certifies a suite as safe when it is not.
  · `eager_prefix` TRUNCATES AT THE FIRST `~`, it does not filter. One cut anywhere makes every
    later hop conditional; joining a call census against the whole route credited openers past a
    `~` and drove ruling agreement from 6/7 down to 3/7.

⚑⚑⚑ AND WRITING THESE FOUND A THIRD PROPERTY THE MODULE DOES NOT CLAIM, LEFT AS A FINDING
RATHER THAN A CASE. `reaches` RETURNS AT THE FIRST SEED IT MEETS in an unordered depth-first
walk, so when one module is reachable both conditionally and eagerly, WHICH route comes back
depends on traversal order — measured: a fixture whose eager route genuinely executes reports
`('lazyside', '~shared', 'store')` under `through_cuts=True`. Nothing is lost (the eager route is
still found, and the narrow reading returns it unmarked), but the wide reading's ROUTE is not
guaranteed to be the most eager one available. A consumer joining a call census against a wide
route should truncate with `eager_prefix` and not assume minimality.

⚑⚑ AND THE `through_cuts` PARAMETER IS TESTED IN BOTH POSITIONS BECAUSE IT IS A PARAMETER RATHER
THAN A REPLACEMENT. The narrow reading answers *what does importing this EXECUTE*; the wide one
*what could it reach if the code RUNS*. A suite exercising one default would leave the other
question — the one the module refused to collapse — unmeasured.

⚑⚑ THE FIXTURES ARE A SYNTHETIC TREE UNDER A TEMPORARY ROOT, AND THE SEEDS ARE REAL NAMES. The
walk resolves through an index the caller supplies, so a fixture tree needs no path injection —
only a `module_index` over it. What it cannot fake is `STORE_SEEDS`, which is a module constant;
so a fixture importing `store` is importing the real seed name, and the roster arm iterates the
constant rather than naming a member of it.

⚑ WHAT THIS LENS CANNOT SEE IS PINNED TOO. A file opening a store WITHOUT importing a seed is
invisible here — measured on `query_defs` — and `store_calls` is the decorrelated second lens for
exactly that gap. A case asserting the gap does not exist would be asserting the opposite of what
the module says about itself.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import store_reach


def _tree(base: Path, **modules: str) -> dict[str, str]:
    """Write each named module and return the index over them."""
    for name, body in modules.items():
        (base / f"{name}.py").write_text(body, encoding="utf-8")
    return store_reach.module_index(base.parent, (base.name,))


def the_index_maps_every_local_module(out: list[str]) -> int:
    """Check the walk's resolution table is flat by BASENAME — how these files import."""
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw) / "tree"
        base.mkdir()
        index = _tree(base, alpha="", beta="")
        if set(index) != {"alpha", "beta"}:
            out.append(f"selftest: the index holds {sorted(index)!r}")
            return 1
        if not index["alpha"].endswith("alpha.py"):
            out.append(f"selftest: alpha resolves to {index['alpha']!r}")
            return 1
    return 0


def the_index_skips_the_vendored_directories(out: list[str]) -> int:
    """Check the skip roster is honoured — a shape over the constant, not a named member."""
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw) / "tree"
        base.mkdir()
        for skipped in store_reach.SKIP_DIRS:
            nested = base / skipped
            nested.mkdir()
            (nested / "hidden.py").write_text("", encoding="utf-8")
        index = _tree(base, visible="")
        if "hidden" in index:
            out.append(f"selftest: a skipped directory contributed to {sorted(index)!r}")
            return 1
        if "visible" not in index:
            out.append("selftest: the index found nothing at all — a constant, not a walk")
            return 1
    return 0


def a_direct_seed_import_reaches(out: list[str]) -> int:
    """Check the one-hop case, and that the SEED is named in the route."""
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw) / "tree"
        base.mkdir()
        index = _tree(base, tool="import store\n")
        found, via = store_reach.reaches(index["tool"], index)
        if not found:
            out.append("selftest: a direct `import store` did not reach")
            return 1
        if via != ("store",):
            out.append(f"selftest: the route is {via!r}, not the seed alone")
            return 1
    return 0


def reach_is_transitive(out: list[str]) -> int:
    """Check a module reaching a store THROUGH another is found — the recorded incident.

    ⚑⚑ `schema.py` REACHES THE STORE THROUGH ITS OWN IMPORTS and a direct-import test would
    catch it — but `sppf_drain` reaches it through `_schema`, and a degree-1 census reports
    those as clean. Under-admitting certifies a suite that WILL abort as needing no tenant.
    """
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw) / "tree"
        base.mkdir()
        index = _tree(
            base, tool="import middle\n", middle="import deeper\n", deeper="import store\n"
        )
        found, via = store_reach.reaches(index["tool"], index)
        if not found:
            out.append("selftest: a three-hop route to a seed did not reach")
            return 1
        if via != ("middle", "deeper", "store"):
            out.append(f"selftest: the transitive route is {via!r}")
            return 1
    return 0


def a_store_free_closure_does_not_reach(out: list[str]) -> int:
    """Check an unrelated tree reports NOTHING — THE DISCRIMINATOR.

    ⚑⚑ WITHOUT THIS ARM A `reaches` RETURNING TRUE UNCONDITIONALLY passes every positive case.
    A census that says yes to everything reads exactly like a working one until asked to say no,
    and this walk's whole value is the split it draws.
    """
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw) / "tree"
        base.mkdir()
        index = _tree(base, tool="import middle\n", middle="import deeper\n", deeper="")
        found, via = store_reach.reaches(index["tool"], index)
        if found:
            out.append(f"selftest: a store-free closure reached, via {via!r}")
            return 1
        if via != ():
            out.append(f"selftest: a non-reaching walk returned a route {via!r}")
            return 1
    return 0


def a_deferred_seed_is_invisible_to_the_narrow_reading(out: list[str]) -> int:
    """Check the DEFAULT answers *what does importing this EXECUTE*.

    ⚑⚑ THE WIDE READING WAS MEASURED WRONG — following cuts unconditionally reported 54 of 99
    suites as store-reaching, including an Agda lexer, through chains only the EXPLAIN modes
    call. So the narrow reading is the default, and this pins it.
    """
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw) / "tree"
        base.mkdir()
        index = _tree(base, tool="def run():\n    import store\n")
        found, _via = store_reach.reaches(index["tool"], index)
        if found:
            out.append("selftest: a deferred import reached under the NARROW reading")
            return 1
    return 0


def a_deferred_seed_reaches_through_cuts_and_is_marked(out: list[str]) -> int:
    """Check the wide reading finds it AND marks the hop `~` rather than merging it.

    ⚑⚑ MARKING INSTEAD OF MERGING keeps both questions askable from ONE walk. An unmarked route
    is what importing executes; a `~` route is what it can reach if the code runs. A wide
    reading that dropped the mark would answer the second question in the first one's voice.
    """
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw) / "tree"
        base.mkdir()
        index = _tree(base, tool="def run():\n    import store\n")
        found, via = store_reach.reaches(index["tool"], index, through_cuts=True)
        if not found:
            out.append("selftest: a deferred import did not reach through cuts")
            return 1
        if via != ("~store",):
            out.append(f"selftest: the deferred route is {via!r}, unmarked or misrouted")
            return 1
    return 0


def an_eager_route_survives_an_earlier_conditional_one(out: list[str]) -> int:
    """Check a module reached first via `~` is still reachable eagerly — THE RECORDED DEFECT.

    ⚑⚑⚑ THE VISITED SET IS KEYED ON `(module, eager)`. The first cut marked a module seen the
    moment a `~` route touched it, so a later fully-eager route to the same module was silently
    discarded and the walk reported the conditional route as the only one — understating what
    EXECUTES, which certifies a suite as safe when it is not.

    ⚑⚑⚑ AND MEASURING THIS EXPOSED A SECOND, SEPARATE LIMITATION — recorded rather than
    asserted away. `reaches` RETURNS AT THE FIRST SEED IT MEETS in an unordered depth-first
    walk, so when a module is reachable both conditionally and eagerly, WHICH route comes back
    depends on traversal order: the fixture below yields `('lazyside', '~shared', 'store')`
    even though `('eagerside', 'shared', 'store')` genuinely executes. The `(module, eager)`
    key does its job — the eager route is not ERASED, and the narrow reading still finds it —
    but the wide reading's route is not guaranteed to be the most eager one available.

    So this arm pins what the key ACTUALLY guarantees: the eager route survives, demonstrated
    by the NARROW reading still reaching. Asserting an unmarked wide route would be asserting a
    property the walk does not have, and would go red on an ordering change rather than on a
    regression.
    """
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw) / "tree"
        base.mkdir()
        index = _tree(
            base,
            tool="import lazyside\nimport eagerside\n",
            lazyside="def run():\n    import shared\n",
            eagerside="import shared\n",
            shared="import store\n",
        )
        # ⚑ THE NARROW READING IS THE ONE THAT MUST NOT BE POISONED. It never enqueues the
        # deferred hop at all, so a route it returns is what importing EXECUTES — and if a
        # conditional visit could mark `shared` seen, this is where it would go missing.
        found, via = store_reach.reaches(index["tool"], index)
        if not found:
            out.append("selftest: the EAGER route to the seed was erased")
            return 1
        if any(hop.startswith("~") for hop in via):
            out.append(f"selftest: the narrow reading returned a conditional hop: {via!r}")
            return 1
        wide_found, _wide_via = store_reach.reaches(index["tool"], index, through_cuts=True)
        if not wide_found:
            out.append("selftest: the wide reading lost a route the narrow one found")
            return 1
    return 0


def the_eager_prefix_truncates_at_the_first_cut(out: list[str]) -> int:
    """Check hops after a `~` are dropped, not filtered — THE SECOND RECORDED DEFECT.

    ⚑⚑ ONE `~` ANYWHERE MAKES EVERY LATER HOP CONDITIONAL. The hops after a cut are not `less
    certain`, they are unreached unless the cut fires — so this truncates. Filtering instead
    credited openers past a cut and drove ruling agreement from 6/7 down to 3/7, with all four
    new disagreements sharing that shape.
    """
    got = store_reach.eager_prefix(("a", "b", "~c", "d", "e"))
    if got != ("a", "b"):
        out.append(f"selftest: the eager prefix is {got!r}, expected truncation at the cut")
        return 1
    if store_reach.eager_prefix(("~a", "b")) != ():
        out.append("selftest: a route cut at its first hop kept an eager prefix")
        return 1
    return 0


def a_fully_eager_route_is_its_own_prefix(out: list[str]) -> int:
    """Check the no-cut case returns everything — the other half of the truncation arm.

    ⚑ WITHOUT THIS, A `eager_prefix` RETURNING `()` ALWAYS would pass the truncation case. The
    two halves together are what distinguish truncating from erasing.
    """
    route = ("a", "b", "c")
    if store_reach.eager_prefix(route) != route:
        out.append(f"selftest: a cut-free route lost hops: {store_reach.eager_prefix(route)!r}")
        return 1
    if store_reach.eager_prefix(()) != ():
        out.append("selftest: the empty route did not survive")
        return 1
    return 0


def every_seed_is_reachable_by_name(out: list[str]) -> int:
    """Check each declared seed terminates the walk — a shape over the roster.

    ⚑ NAMING THE SEEDS RATHER THAN THE REACHING FILES is what keeps the roster from being
    hand-maintained; iterating it here means a seed added tomorrow is covered without editing
    this case, and one added to the constant but unreachable fails rather than reporting zero.
    """
    for seed in sorted(store_reach.STORE_SEEDS):
        # ⚑ A FRESH TREE PER SEED. Reusing one directory leaves the previous seed's fixture on
        # disk, so the index grows and a later case resolves through a file it did not write —
        # which is what a first draft did, reporting `catalog_db` as `query_builders`' route.
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw) / "tree"
            base.mkdir()
            index = _tree(base, tool=f"import {seed}\n")
            found, via = store_reach.reaches(index["tool"], index)
            if not found or via != (seed,):
                out.append(f"selftest: seed {seed!r} did not terminate the walk: {via!r}")
                return 1
    return 0


def a_cycle_terminates(out: list[str]) -> int:
    """Check mutually-importing modules do not hang the walk — the visited set doing its job."""
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw) / "tree"
        base.mkdir()
        index = _tree(base, one="import two\n", two="import one\nimport store\n")
        found, _via = store_reach.reaches(index["one"], index)
        if not found:
            out.append("selftest: a cyclic closure did not reach the seed beyond the cycle")
            return 1
    return 0


def an_unresolvable_import_is_not_a_reach(out: list[str]) -> int:
    """Check a name outside the index is skipped rather than guessed at."""
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw) / "tree"
        base.mkdir()
        index = _tree(base, tool="import numpy\nimport nothing_here\n")
        found, via = store_reach.reaches(index["tool"], index)
        if found:
            out.append(f"selftest: an unresolvable import reached, via {via!r}")
            return 1
    return 0


_ARMS = (
    the_index_maps_every_local_module,
    the_index_skips_the_vendored_directories,
    a_direct_seed_import_reaches,
    reach_is_transitive,
    a_store_free_closure_does_not_reach,
    a_deferred_seed_is_invisible_to_the_narrow_reading,
    a_deferred_seed_reaches_through_cuts_and_is_marked,
    an_eager_route_survives_an_earlier_conditional_one,
    the_eager_prefix_truncates_at_the_first_cut,
    a_fully_eager_route_is_its_own_prefix,
    every_seed_is_reachable_by_name,
    a_cycle_terminates,
    an_unresolvable_import_is_not_a_reach,
)

# ⚑ THE SEED ARM'S CONTRIBUTION IS DERIVED FROM THE ROSTER, NOT TYPED. A literal here would go
# stale the day a seed is added — a count expiring for the same reason a named witness does.
_CASE_COUNT = 2 + 2 + 2 + 2 + 2 + 1 + 2 + 3 + 2 + 2 + 1 + 1 + len(store_reach.STORE_SEEDS)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"store-reach selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"store-reach selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
