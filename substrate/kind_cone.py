#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cone figures of a ratchet kind - seeds, providers, routes - with the DAG a parameter.

THE FOURTH CUT OF THE DRAIN'S FIFTH FILE (`catalog/library/figures.py:350-647`, W4 tick 61).
The cone itself is `import_cone.leverage` over `dagcone` and is never re-walked here: the
origin records that its first cut intersected the cones itself, "a second implementation of one
relation, which is how agda_files() became four bodies under one name". What this module owns
is the PLANNING around that call - which files seed it, how the providers group into routes,
and how a route's exclusivity is measured route-against-route - each a pure function of the
keys, the schema and callables the caller supplies for the DAG and the filesystem.

THREE MEASURED MISREADINGS ARE KEPT AS THE RULES THAT CORRECT THEM:

- "FREES" WAS AN OVERCLAIM. A cone is REACHABILITY; a module in it may sit behind other
  blockers too, and three kind cones once summed to 1253 over a ~3400-module tree because one
  subtree was counted three times. So a cone is reported BESIDE its exclusive part - what no
  other bucket also blocks - and the difference is the overlap.
- A CONE OF 0 FROM UNRESOLVED SEEDS IS AN ARTEFACT, NOT A FINDING. When no seed path resolves
  in the DAG the answer is a refusal naming the count, never `(0, 0, [])`.
- A MISSING PROVIDER FILE IS NOT A SPLITTER REFUSAL. The provider was split already - the
  leaves exist, the flat file is consumed, and a consumer still names the parent - whose route
  is rewire-then-retire, not decomposition. Reporting it as "the splitter refuses: no such
  file" sent the operator to re-split a module with no file left.

Consumer and provider cones are two views of ONE graph - a module consumes what it imports
and provides to what imports it - and relate by CONTAINMENT; `containment` reports it so the
relation is checked rather than assumed.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate.import_cone import Leverage
from substrate.key_partition import MIN_ARITY_WITH_KIND

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

    from substrate.key_spec import KeySpec

# The repo-relative prefix a key's path field carries; the DAG resolves agda-relative paths.
AGDA_PREFIX = "agda/"
# The route a provider takes when the splitter names no blocker.
DECOMPOSE = "decompose"
# The verdicts a provider whose file is gone can carry.
CONSUMED_PARENT = "consumed-parent (leaves exist; rewire)"
NO_FILE = "no file and no leaf dir"

Refusal = tuple[None, str]
# The cone over a seed set, or None when the DAG could not be asked.
Lever = Callable[[list[str], list[list[str]]], Leverage | None]
# (provider module, keys, the splitter's verdict or a route-changing fact).
Provider = tuple[str, int, str]
# (route, providers, seeds resolved, cone, exclusive) - cone and exclusive None on a failed ask.
RouteRow = tuple[str, int, int, int | None, int | None]


@dataclass(frozen=True)
class Probe:
    """What the provider verdict reads from the tree, supplied by the caller."""

    # module -> its source path, whether or not the file exists.
    file_of: Callable[[str], str]
    exists: Callable[[str], bool]
    has_leaf_dir: Callable[[str], bool]
    # The splitter's blockers for a path: empty when splittable; may raise. A Sequence, because
    # a list is invariant and the splitter's rows carry a narrower payload than `object`.
    blockers: Callable[[str], Sequence[tuple[str, object]]]


def seeds(keys: Iterable[str], spec: KeySpec | None, kind: str) -> tuple[set[str], None] | Refusal:
    """Return the agda-relative consumer files carrying one kind - the cone's seed set."""
    if spec is None:
        return None, "no gate_keys.SCHEMA entry"
    out: set[str] = set()
    for k in keys:
        parts = k.split(spec.sep)
        if len(parts) != spec.arity:
            continue
        if spec.arity >= MIN_ARITY_WITH_KIND and parts[-1] != kind:
            continue
        out.add(parts[spec.path_field].removeprefix(AGDA_PREFIX))
    if not out:
        return None, f"no keys of kind `{kind}`"
    return out, None


def cone(
    seed_set: Iterable[str], lever: Lever
) -> tuple[tuple[int, int, list[tuple[int, str]]], None] | Refusal:
    """Return (n_cone, n_seeds, top) - what the seeds PARTICIPATE IN blocking - or why not."""
    s = sorted(seed_set)
    lev = lever(s, [])
    if lev is None:
        return None, "the import DAG could not be asked"
    if lev.n_seeds == 0:
        return None, (
            f"none of {len(s)} seed path(s) resolved in the import DAG -- "
            f"a cone of 0 here would be an artefact, not a finding"
        )
    return (lev.n_cone, lev.n_seeds, lev.top), None


Exclusive = tuple[int, int, list[str], list[str] | None]


def exclusive(
    mine: Iterable[str], others: Iterable[Iterable[str]], lever: Lever
) -> tuple[Exclusive, None] | Refusal:
    """Return (cone, exclusive, members, exclusive members); exclusive is the cone when unasked."""
    against = [sorted(o) for o in others if o]
    lev = lever(sorted(mine), against)
    if lev is None:
        return None, "the import DAG could not be asked"
    if lev.n_seeds == 0:
        return None, "no seed path resolved in the import DAG"
    excl = lev.n_cone if lev.exclusive is None else lev.exclusive
    return (lev.n_cone, excl, lev.members, lev.exclusive_members), None


def providers(concentration: Iterable[tuple[str, int, str]], probe: Probe) -> list[Provider]:
    """Return each provider with its key count and the splitter's verdict on its file."""
    out: list[Provider] = []
    for ident, n, _sample in concentration:
        mod = ident.rsplit("::", 1)[0]
        path = probe.file_of(mod)
        if not probe.exists(path):
            out.append((mod, n, CONSUMED_PARENT if probe.has_leaf_dir(mod) else NO_FILE))
            continue
        try:
            b = probe.blockers(path)
        except Exception as e:  # noqa: BLE001 - the splitter's parse may raise anything; the verdict carries it
            out.append((mod, n, f"{type(e).__name__}: {e}"))
            continue
        out.append((mod, n, "; ".join(k for k, _d in b)))
    return out


def by_route(prov: Iterable[Provider]) -> dict[str, list[str]]:
    """Group providers by the route their verdict names; an empty verdict is decomposition."""
    out: dict[str, list[str]] = {}
    for mod, _n, route in prov:
        out.setdefault(route or DECOMPOSE, []).append(mod)
    return out


def route_rows(
    routes: Mapping[str, Sequence[str]], seeds_of: Mapping[str, Sequence[str]], lever: Lever
) -> list[RouteRow]:
    """Return one row per route with its cone measured against every OTHER route's seeds."""
    rows: list[RouteRow] = []
    for route, s in seeds_of.items():
        others = [list(v) for r, v in seeds_of.items() if r != route]
        lev = lever(list(s), others)
        if lev is None:
            rows.append((route, len(routes[route]), len(s), None, None))
            continue
        rows.append((route, len(routes[route]), lev.n_seeds, lev.n_cone, lev.exclusive))
    return sorted(rows, key=_by_freed)


def _by_freed(row: RouteRow) -> int:
    """Sort key: the exclusive cone descending, the full cone where exclusivity is undefined."""
    excl = row[4]
    return -(excl if excl is not None else (row[3] or 0))


def containment(consumers: Iterable[str], reach: Iterable[str]) -> tuple[int, int]:
    """Return (consumers inside the providers' reach, consumers total) - a checked relation."""
    cons = list(consumers)
    r = set(reach)
    return sum(1 for c in cons if c in r), len(cons)
