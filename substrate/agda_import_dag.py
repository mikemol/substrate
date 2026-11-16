# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The Agda import DAG, parsed ONCE per process, plus the reverse-edge cone.

Extracted from `scratch/split_census.py` as part of ⟡drain-split-census. That file carried
a large standing ruff+mypy population, so the zero-tolerance per-file gate refused every
write to it — including the one-line `edit_snapshot.guard()` insertion the snapshot-guard
gate names as its repair. The gate's own words are the method: *a file too large to leave
clean in one edit is the per-file gate saying the file does too much*, so the unit of
repair is the whole file and the drain proceeds by responsibility.

⚑ THE MEMO IS THE FIX, NOT PARALLELISM. The parse walks ~3000 sources; two call sites
re-ran it, and the cone ranking called one of them ONCE PER FAILED MODULE — 121 identical
tree walks. Caching at the single place that owns the relation gives every consumer
(freshness, blast radius, cone ranking) the same parse. *Before reaching for concurrency,
check whether the work is REPEATED: parallelising 121 redundant walks would only have made
the same mistake run faster.*

⚑ ONE IMPORT DAG, THREE CONSUMERS. The edges come from `substrate.agda_dag.parse()` — the
SAME relation the build's prerequisites are generated from and the same one the census
judges freshness by. A private re-scan is how two authorities for one relation start
disagreeing (the `agda_files()` class, §6d).

⚑⚑⚑ THE SOURCE MOVED INTO THE PACKAGE (⟡drain-the-generator), AND THE OLD SHAPE COULD NOT
BE IMPORTED AT ALL FROM HERE. This read `from gen_build_makefiles import parse_tree` — a
BARE-NAME import of a scripts-resident module — with a docstring defending it: the stub
`stubs/gen_build_makefiles.pyi` is keyed on the module NAME, so a qualified
`from scripts.gen_build_makefiles import …` would bypass the stub and mypy would follow the
untyped source. That reasoning was correct about the STUB and wrong about the REACH: a bare
name resolves only when something has arranged the path, which a package module cannot
assume. MEASURED: `tests/test_agda_census_drain.py` fails in a plain run with
`ModuleNotFoundError: No module named 'gen_build_makefiles'`.

⚑⚑ AND THE REPOINT RETIRES THE STUB RATHER THAN RELOCATING IT. `substrate.agda_dag` is
natively typed and the package ships `py.typed`, so there is no stub to key on and no
name-vs-path tension left to navigate — the constraint the old docstring worked around
stops existing rather than moving.

⚑ THE FOUR `type: ignore[assignment]` CASTS ARE GONE WITH IT. The memo was a
`dict[str, object]` whose four reads each needed a cast to recover the type the parse
already knew; `agda_dag.Dag` carries `rdeps` and `src_to_mod` as typed properties, so the
shape that required the ignores is no longer built here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from substrate import agda_dag

if TYPE_CHECKING:
    from collections.abc import Iterable

_PARSED: list[agda_dag.Dag] = []


def dag() -> agda_dag.Dag:
    """Return the import DAG, memoised per process.

    ⚑ MEMOISED AND DELIBERATELY NOT INVALIDATED. A parse that changed mid-process would be
    a straddled measurement, which the tree stamp already refuses at the census layer; a
    stale DAG within one process is the same class, so the honest scope is the process.
    """
    if not _PARSED:
        _PARSED.append(agda_dag.parse())
    return _PARSED[0]


def import_dag() -> tuple[
    dict[str, str], dict[str, frozenset[str]], dict[str, frozenset[str]], dict[str, str]
]:
    """Return `(disk, deps, rdeps, src_to_mod)` — the import DAG, memoised per process.

    `disk` maps a module name to its source relpath, `deps` a module to its direct in-tree
    imports, `rdeps` the reverse relation, and `src_to_mod` inverts `disk`.

    ⚑ A SRC RELPATH IS `Substrate/…/X.agda` RELATIVE TO `agda/` — the generator's docstring
    states it verbatim, and the origin ADDED an `agda/` prefix instead of reading it. Every
    lookup missed, so the freshness check withheld its verdict on every file. That was the
    third time in one session an authority's contract was inferred from a call site rather
    than read from the line that states it.

    ⚑ KEPT AS A TUPLE-RETURNING FACADE because three consumers already destructure it. The
    typed carrier is `dag()`; this is the shape its callers were written against, and
    changing both at once would be a rename hiding inside a repoint.
    """
    parsed = dag()
    return parsed.disk, parsed.deps, parsed.rdeps, parsed.src_to_mod


def blast_radius(failed_srcs: Iterable[str]) -> set[str]:
    """Return every module transitively IMPORTING one of `failed_srcs` (as src relpaths).

    ⚑ C1: THE DOWNSTREAM CONE OF A BUILD FAILURE IS A FINDING, NOT A GAP. Given the modules
    `make` reported as failed, these are the ones it therefore never attempted — so their
    `stale` verdict means *blocked*, not *unmeasured*.

    ⚑ THE CONE EXCLUDES THE SEEDS THEMSELVES. This returns IMPORTERS; a set of files that
    nothing imports has a cone of 0 and is still that many files of work.
    """
    parsed = dag()
    src_to_mod = parsed.src_to_mod
    rdeps = parsed.rdeps
    stack = [src_to_mod[s] for s in failed_srcs if s in src_to_mod]
    out: set[str] = set()
    while stack:  # BFS to fixpoint; cycle-safe via `out`
        for importer in rdeps.get(stack.pop(), frozenset()):
            if importer not in out:
                out.add(importer)
                stack.append(importer)
    return {parsed.disk[m] for m in out if m in parsed.disk}


def importers_of(path: str) -> list[str]:
    """Return the source relpaths of every module directly importing `path`.

    ⚑ THIS IS THE DOMAIN-SPECIFIC HALF, AND IT IS THE ONLY HALF. Cone reachability and seed
    ranking are generic and live in `dagcone`; what is Agda-specific is exactly this edge
    relation. The origin defended a wider domain boundary ("top-seed ranking") and it did
    not survive contact — ranking seeds by reach is generic, and its truncation was a
    DISPLAY decision frozen into the computation.
    """
    parsed = dag()
    module = parsed.src_to_mod.get(path)
    if module is None:
        return []
    return [parsed.disk[i] for i in parsed.rdeps.get(module, frozenset()) if i in parsed.disk]
