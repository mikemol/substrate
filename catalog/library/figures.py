#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""figures.py - the READERS the worklist's item witnesses share, now a shim over the package.

THIS FILE IS ADAPTORS (W4 file 5 cut 6, tick 64). Every mechanism it once held has a home in
`substrate/` and is witnessed there: the leaf-verify ledger is `leaf_ledger`; the build-failed
partition is `failure_census`; the added-key partitions are `key_partition`; the cone planning
is `kind_cone` over `import_cone`; the rostered reach-the-store predicates are `site_paydown`;
the ratchet family binds to `gate_population`, `gate_module`, `ratchet_census`, `universal_flags`
and `key_spec`; the remaining readers bind to `gate_status`, `sole_authority` and
`census_denominator`. What stays here is the SHAPE thirteen bare consumer sites reach through
`import figures as F`: `report`, `DERIVED`, `ROOT`, `LEDGER`, `_read`, `build_log`,
`_failures_by_kind`, `_refine` - and every other public name the origin had, kept.

THREE OF THE ORIGIN'S CLAIMS ARE CORRECTED HERE, EACH RECORDED AS A FINDING:

- `worklist_gate.scratch_size` moved to `wg_engine` when worklist_gate was drained and this file
  was never repointed, so its own selftest died before any case ran (gate-G440).
- `sweeps_without_denominator` raised `NO INSTRUMENT` for an instrument the package holds:
  `census_denominator.bare`. It answers now (gate-G445).
- `dag_rederivations` / `cst_blob_sites` tested a store token against the LIST of rows
  `pycodemod.source_of` returns - a membership test that never matches a substring, so no site
  could ever read as paid. The adaptor joins the rows' text (gate-G446).

The caches stay where the origin put them - the L2 memo on the failure walk keyed on the ledger
stamp (a stamp change is precisely when the answer changes), the per-process ratchet census
memo, and the two refinement verdict memos - because a cache is an adaptor over a computation,
and the computations are what moved. The origin's docstrings were the record of why each figure
exists; the package modules carry those now and this file does not repeat them.
"""

from __future__ import annotations

import concurrent.futures as cf
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, cast

ROOT = Path(__file__).resolve().parent.parent.parent

# ⚑ BOTH AUTHORITY DIRECTORIES, ONCE, AT IMPORT - the origin's mechanism, kept: this file is not
# in the package, and the scratch tools it adapts are reached by leaf name. The typed surface
# comes from `stubs/`; this insert is what makes the same names resolve at runtime.
for _dir in ("scripts", "scratch"):
    _p = str(ROOT / _dir)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import agda_lex
import fix_noparse
import fix_notinscope
import gate_status
import pycodemod
import split_census
import split_lemmas
import wg_engine

from substrate import (
    census_denominator,
    failure_census,
    gate_module,
    gate_population,
    import_cone,
    key_partition,
    key_spec,
    leaf_ledger,
    log_freshness,
    site_paydown,
    sole_authority,
    universal_flags,
)
from substrate import kind_cone as kc_lib
from substrate import ratchet_census as rc_lib
from substrate.agda_error_class import CLASS_REMEDY

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator, Sequence

    from substrate.agda_error_class import Verdict

LEDGER = str(ROOT / "agda" / ".leaf-verify.tsv")
AGDA = ROOT / "agda"

# The derived artifacts and the item that produces each - repo-relative, longest prefix wins.
DERIVED: dict[str, str] = {
    "agda/.leaf-verify.tsv": "CENSUS",
    "agda/_build": "CENSUS",
    "catalog/catalog.db": "B2",
}

# The ratchet census memo (pure reads, idempotent under a race), and the two verdict memos.
_CENSUS_CACHE: dict[str, tuple[tuple[int, int, list[str]] | None, str | None]] = {}
_NIS_CACHE: dict[str, str | None] = {}
_NP_CACHE: dict[str, str | None] = {}
_LOG_INDEX: dict[str, str] = {}
# How many pool workers a sweep spreads over; below three gates the child import cost dominates.
_POOL = 8
_POOL_MIN = 3


def _read(p: str) -> str:
    """Read a text file whole."""
    return Path(p).read_text(encoding="utf-8")


# ── the ledger ────────────────────────────────────────────────────────────────────


def _index() -> dict[str, str]:
    """Return the per-module log index, walked once per process."""
    if not _LOG_INDEX:
        _LOG_INDEX.update(log_freshness.log_index(AGDA / "_build"))
    return _LOG_INDEX


def build_log(rel: str) -> str:
    """Return the per-module `.agdai.log` path for an agda-relative source ('' when none)."""
    return leaf_ledger.log_for(rel, _index()) or ""


def census_stamp() -> str | None:
    """Return the ledger's recorded tree-stamp, or None if absent."""
    return leaf_ledger.stamp_of(LEDGER)


def tree_stamp() -> str:
    """Re-derive the stamp from the tree NOW, in the ledger's own format."""
    return split_census.tree_stamp()


def census_is_current() -> tuple[bool, str]:
    """Return (ok, detail): the ledger is current iff its stamp matches the tree's now."""
    return leaf_ledger.is_current(census_stamp(), tree_stamp())


# ── the failure census ────────────────────────────────────────────────────────────


def _verdict_nis(rel: str) -> str | None:
    """Return fix_notinscope's first verdict for a source, memoised; None without a log."""
    if rel not in _NIS_CACHE:
        log = build_log(rel)
        rows = fix_notinscope.classify(log) if log and Path(log).exists() else []
        _NIS_CACHE[rel] = rows[0][2] if rows else None
    return _NIS_CACHE[rel]


def _verdict_np(rel: str) -> str | None:
    """Return fix_noparse's first verdict for a source, memoised; None without a log."""
    if rel not in _NP_CACHE:
        log = build_log(rel)
        rows = fix_noparse.classify(log) if log and Path(log).exists() else []
        _NP_CACHE[rel] = rows[0][4] if rows else None
    return _NP_CACHE[rel]


def _refine(kind: str, rel: str) -> str:
    """Split the two refinable kinds by the repairing tool's verdict; pass every other kind."""
    return failure_census.refine(kind, rel, _verdict_nis, _verdict_np)


def _refine_noparse(kind: str, rel: str) -> str:
    """Split `other:NoParseForApplication` by whether a fixity collision caused it."""
    return failure_census.refine(kind, rel, _verdict_nis, _verdict_np)


def _is_fresh(rel: str) -> bool:
    """Report whether a source's build log describes today's tree."""
    return bool(split_census.log_is_fresh(rel)[0])


def _classify(rel: str, txt: str) -> Verdict:
    """Classify one compile's error text."""
    return split_census._classify(rel, txt)


def _read_log(path: str) -> str:
    """Return a log's text, or '' when it cannot be read - the classifier reads '' as clean."""
    try:
        return _read(path)
    except OSError:
        return ""


def _walk() -> failure_census.Census:
    """Walk the ledger: the build-failed rows partitioned by refined kind."""
    if not Path(LEDGER).exists():
        return {}, {}
    _stamp, rows = leaf_ledger.read(LEDGER)
    return failure_census.census(
        failure_census.Inputs(
            rows=rows,
            log_of=lambda rel: build_log(rel) or None,
            read_text=_read_log,
            is_fresh=_is_fresh,
            classify=_classify,
            refine=_refine,
            remedies=CLASS_REMEDY,
        )
    )


def _stamp_key(stamp: object) -> bytes:
    """Key the L2 entry on the ledger stamp - exactly when the answer changes."""
    return str(stamp).encode()


@agda_lex.l2("figures.failures", _stamp_key, derives_from="agda/_build")
def _failures_at(stamp: str | None) -> failure_census.Census:
    """Return the walk keyed by the ledger stamp it describes."""
    return _walk()


def _failures_by_kind() -> failure_census.Census:
    """Return ({kind: [module]}, {module: remedy}) from the build census, memoised on the stamp."""
    return _failures_at(census_stamp())


def failure_kinds() -> list[str]:
    """Return every error kind present in the census - the discovered roster."""
    return failure_census.kinds(_failures_by_kind())


def failing_modules(kind: str) -> list[str]:
    """Return a copy of the modules failing with `kind`."""
    return failure_census.modules(_failures_by_kind(), kind)


def failing_parts(kind: str) -> list[tuple[str, str | None]]:
    """Return [(module, remedy | None)] for `kind`."""
    return failure_census.parts(_failures_by_kind(), kind)


# ── the ratchet family ────────────────────────────────────────────────────────────


def ratchet_gates() -> list[str]:
    """Return every `scripts/check_*.py` ratchet gate, by the predicate-keyed census.

    ⚑ THE ORIGIN GREPPED `scripts/` FOR THE STRING `set_ratchet` - a name-keyed census - and
    counted `check_baseline_health.py`, which only MENTIONS it in prose (`pycodemod --calls
    set_ratchet` finds 0 calls there). `gate_population` keys on what a file DOES and drops it.
    THE SCOPE IS KEPT: the figure's rows are stemmed as `<check_>...<.py>-added` and the worklist
    cites them by that spelling, so the four gates the package sees OUTSIDE `scripts/check_*`
    (`run_selftests.py`, `private_gate.py`, `public_gate.py`, `type_gate.py`) are a declared
    bound of this figure, not silently folded into a roster whose consumers cannot name them
    (gate-G448).
    """
    return sorted(
        Path(p).name
        for p in gate_population.gates()
        if p.startswith("scripts/check_") and p.endswith(".py")
    )


def gates_outside_scope() -> list[str]:
    """Return the ratchet gates the predicate-keyed census sees that `ratchet_gates` declines."""
    return sorted(
        p
        for p in gate_population.gates()
        if not (p.startswith("scripts/check_") and p.endswith(".py"))
    )


def _gate_module(name: str) -> tuple[object | None, str | None]:
    """Return (module, None) or (None, why) for one gate by name."""
    return gate_module.gate_module(name)


def _flag_literals(src: str) -> set[str]:
    """Return every `--flag` string literal in a source text."""
    import ast

    try:
        tree = ast.parse(src)
    except SyntaxError:
        return set()
    return universal_flags._literals(tree)


def gates_without_universal_flags(total: list[int] | None = None) -> Iterator[str]:
    """Yield the ratchet gates accepting the universal flags by neither route; count in `total`."""
    names = tuple(ratchet_gates())
    rows = universal_flags.population(names, ROOT)
    if total is not None:
        total[0] = len(names)
    seen = {row.gate for row in rows}
    for name in names:
        if name not in seen:
            yield name  # unimportable is not compliant
    for row in universal_flags.lacking(rows):
        yield row.gate


def gates_missing_check_argv() -> Iterator[str]:
    """Yield the ratchet gates that do not route their flags through the shared authority."""
    names = tuple(ratchet_gates())
    for row in universal_flags.population(names, ROOT):
        if not row.routes:
            yield row.gate


Census = tuple[tuple[int, int, list[str]] | None, str | None]


def ratchet_census(name: str) -> Census:
    """Return ((held, added, keys), None) or (None, why) for one gate, memoised per process."""
    if name in _CENSUS_CACHE:
        return _CENSUS_CACHE[name]
    got, why = _census_uncached(name)
    _CENSUS_CACHE[name] = (got, why)
    return got, why


def _census_uncached(name: str) -> Census:
    """Ask the package census and re-shape it to the origin's tuple."""
    c, why = rc_lib.census(name)
    if c is None:
        return None, why
    return (c.held, c.over, list(c.added)), None


def _key_spec(name: str) -> key_spec.KeySpec | None:
    """Return the gate's declared key schema, or None."""
    return key_spec.spec_for(name)


def added_kinds(name: str) -> key_partition.Partition:
    """Return the added keys partitioned by kind, or (None, why)."""
    got, why = ratchet_census(name)
    if got is None:
        return None, why
    return key_partition.by_kind(got[2], _key_spec(name))


def kind_concentration(name: str, kind: str) -> key_partition.Partition:
    """Return where one kind's keys concentrate by identity, or (None, why)."""
    got, why = ratchet_census(name)
    if got is None:
        return None, why
    return key_partition.concentration(got[2], _key_spec(name), kind)


# ── the cone family ───────────────────────────────────────────────────────────────


def _lever(srcs: list[str], against: list[list[str]]) -> import_cone.Leverage | None:
    """Ask the driver's cone over the live DAG, re-shaped to the package's Leverage."""
    try:
        lev = split_census.leverage(srcs, against=against)
    except (OSError, KeyError, ValueError):
        return None
    n_cone, n_seeds, top = lev
    return import_cone.Leverage(
        n_cone=n_cone,
        n_seeds=n_seeds,
        top=top,
        members=lev.members or [],
        exclusive=lev.exclusive,
        exclusive_members=lev.exclusive_members,
    )


def _kind_seeds(name: str, kind: str) -> tuple[set[str] | None, str | None]:
    """Return the consumer files carrying one kind, agda-relative, or (None, why)."""
    got, why = ratchet_census(name)
    if got is None:
        return None, why
    return kc_lib.seeds(got[2], _key_spec(name), kind)


Cone = tuple[int, int, list[tuple[int, str]]]


def kind_cone(name: str, kind: str) -> tuple[Cone | None, str | None]:
    """Return (n_cone, n_seeds, top) - what this bucket participates in blocking."""
    seeds, why = _kind_seeds(name, kind)
    if seeds is None:
        return None, why
    return kc_lib.cone(seeds, _lever)


def kind_cone_exclusive(
    name: str, kind: str, others: Iterable[str]
) -> tuple[kc_lib.Exclusive | None, str | None]:
    """Return (cone, exclusive, members, exclusive members) against the other kinds' seeds."""
    mine, why = _kind_seeds(name, kind)
    if mine is None:
        return None, why
    other_seeds = [s for s, _w in (_kind_seeds(name, o) for o in others) if s]
    return kc_lib.exclusive(mine, other_seeds, _lever)


def _probe() -> kc_lib.Probe:
    """Build the provider probe over the live tree."""
    return kc_lib.Probe(
        file_of=lambda m: agda_lex.module_file(m, str(AGDA)),
        exists=lambda p: Path(p).exists(),
        has_leaf_dir=lambda m: AGDA.joinpath(*m.split(".")).is_dir(),
        blockers=split_lemmas.blockers,
    )


def kind_providers(name: str, kind: str) -> tuple[list[kc_lib.Provider] | None, str | None]:
    """Return [(provider, keys, blocked_by)] - the providers with the splitter's verdict."""
    conc, why = kind_concentration(name, kind)
    if conc is None:
        return None, why
    return kc_lib.providers(conc, _probe()), None


def _provider_seeds(mods: Sequence[str]) -> list[str]:
    """Return the agda-relative sources of provider modules, sorted."""
    return sorted({str(Path(agda_lex.module_file(m, str(AGDA))).relative_to(AGDA)) for m in mods})


def route_cones(name: str, kind: str) -> tuple[list[kc_lib.RouteRow] | None, str | None]:
    """Return [(route, providers, files, blocks, exclusive)] - the cone per route."""
    prov, why = kind_providers(name, kind)
    if prov is None:
        return None, why
    routes = kc_lib.by_route(prov)
    if not routes:
        return None, f"no providers for kind `{kind}`"
    seeds_of = {r: _provider_seeds(ms) for r, ms in routes.items()}
    return kc_lib.route_rows(routes, seeds_of, _lever), None


def cone_containment(name: str, kind: str) -> tuple[tuple[int, int] | None, str | None]:
    """Return (consumers inside the providers' reach, consumers total)."""
    prov, why = kind_providers(name, kind)
    if prov is None:
        return None, why
    cons, cwhy = _kind_seeds(name, kind)
    if cons is None:
        return None, cwhy
    reach = split_census._blast_radius(_provider_seeds([m for m, _n, _r in prov]))
    return kc_lib.containment(cons, reach), None


# ── the remaining readers ─────────────────────────────────────────────────────────


def _source_of(rel: str, fn: str) -> str | None:
    """Return the joined source of a def in a file, or None when it cannot be read.

    ⚑ `source_of` RETURNS ROWS; the origin tested a substring against the list (gate-G446).
    """
    try:
        rows = pycodemod.source_of(fn, [str(ROOT / rel)])
    except (OSError, ValueError, RuntimeError):
        return None
    return "\n".join(row[3] for row in rows) or None


def dag_rederivations() -> list[tuple[str, str]]:
    """Return the sites re-deriving `_module_edges` in Python that do not yet read the catalog."""
    return [
        (rel, fn)
        for rel, fn, _w in site_paydown.unpaid(
            site_paydown.DAG_SITES, site_paydown.DAG_PAID, _source_of
        )
    ]


def cst_blob_sites() -> list[tuple[str, str]]:
    """Return the sites storing a parsed CST whole instead of as node rows."""
    return [
        (rel, f"{fn} ({w})")
        for rel, fn, w in site_paydown.unpaid(
            site_paydown.CST_SITES, site_paydown.CST_PAID, _source_of
        )
    ]


def wired_gates() -> list[tuple[str, str, bool]]:
    """Return every gate the pre-commit hook runs, parsed from the hook."""
    return gate_status.gates()


def own_agda_files_definers() -> Iterator[str]:
    """Yield the files that REIMPLEMENT `agda_files` instead of delegating to the authority."""
    home = str(Path(agda_lex.__file__).resolve())
    for rival in sole_authority.authority("agda_files", home).debt:
        yield rival.path


def sweeps_without_denominator() -> Iterator[str]:
    """Yield `path:line` for every reported count with no population, across the tools."""
    for rel in sorted(p for d in ("scripts", "scratch") for p in (ROOT / d).glob("*.py")):
        label = str(rel.relative_to(ROOT))
        for row in census_denominator.bare(census_denominator.reports(rel, label)):
            yield f"{label}:{row.line}"


# ── the report ────────────────────────────────────────────────────────────────────

Row = tuple[str, int | str, str]


def _row(
    figure: str,
    names: Iterable[str],
    empty: str,
    *,
    prefix: Callable[[int], str] | None = None,
    cap: int | None = None,
) -> Row:
    """Fold a STREAM of names into one (figure, count, detail) row - one walk, no container."""
    n, shown, more = 0, [], 0
    for name in names:
        n += 1
        if cap is not None and n > cap:
            more += 1
            continue
        shown.append(name)
    if not n:
        detail = empty
    else:
        detail = ", ".join(shown) + (" ..." if more else "")
        if prefix is not None:
            detail = prefix(n) + detail
    return (figure, n, detail)


def _census_in_child(name: str) -> Census:
    """Top-level so it is picklable for the process pool."""
    return ratchet_census(name)


def _sweep(names: Sequence[str]) -> None:
    """Warm the census memo over a process pool when there is a sweep to spread."""
    if len(names) < _POOL_MIN or _CENSUS_CACHE:
        return
    try:
        with cf.ProcessPoolExecutor(max_workers=min(len(names), _POOL)) as pool:
            _CENSUS_CACHE.update(zip(names, pool.map(_census_in_child, names), strict=True))
    except (OSError, RuntimeError, cf.process.BrokenProcessPool):
        pass


def _gate_rows(rows: list[Row], names: Sequence[str]) -> None:
    """One row per gate, read live; a gate that cannot be measured says so, never zero."""
    for name in names:
        got, why = ratchet_census(name)
        stem = name.removeprefix("check_").removesuffix(".py").replace("_", "-")
        if got is None:
            rows.append(
                (
                    f"{stem}-added",
                    "n/a",
                    f"CANNOT MEASURE ({why}) -- refusing rather than reporting 0",
                )
            )
            continue
        held, added, keys = got
        sample = ", ".join(keys[:3]) + (" ..." if len(keys) > 3 else "") if keys else "at baseline"
        rows.append((f"{stem}-added", added, f"{held} held; {sample}"))


def report(gates: Sequence[str] | None = None) -> list[Row]:
    """Return the figure rows; `gates` narrows the ratchet sweep for the suite, default ALL."""
    total = [0]
    rows: list[Row] = [
        _row(
            "gates-without-dryrun",
            gates_without_universal_flags(total),
            "none",
            prefix=lambda n: f"{n} of {total[0]} ratchet gates; ",
        )
    ]
    ok, detail = census_is_current()
    rows.append(("census-current", int(ok), detail))
    rows.append(
        _row(
            "gates-without-checkargv",
            gates_missing_check_argv(),
            "every ratchet gate calls check_argv",
        )
    )
    rows.append(
        _row("own-agda-files", own_agda_files_definers(), "agda_lex.agda_files is the sole home")
    )
    rows.append(
        _row(
            "sweeps-without-denominator",
            sweeps_without_denominator(),
            "every population-visiting tool reports n of m",
            cap=5,
        )
    )
    rows.append(_row("ratchet-gates", ratchet_gates(), "none"))
    names = list(gates if gates is not None else ratchet_gates())
    _sweep(names)
    _gate_rows(rows, names)
    held = wg_engine.scratch_size()
    rows.append(
        (
            "scratch-bytes-held",
            held,
            "wg_engine.SCRATCH -- non-zero after a completed run means a sandbox leaked",
        )
    )
    return rows


def _times() -> int:
    """Measure the census sweep serial vs threads vs processes, and print the degree."""
    names = ratchet_gates()
    per: list[tuple[float, str]] = []
    for n in names:
        _CENSUS_CACHE.clear()
        t0 = time.monotonic()
        ratchet_census(n)
        per.append((time.monotonic() - t0, n))
    serial = sum(t for t, _ in per)
    _CENSUS_CACHE.clear()
    t0 = time.monotonic()
    with cf.ThreadPoolExecutor(max_workers=min(len(names), _POOL)) as pool:
        list(pool.map(ratchet_census, names))
    threaded = time.monotonic() - t0
    t0 = time.monotonic()
    with cf.ProcessPoolExecutor(max_workers=min(len(names), _POOL)) as pool:
        list(pool.map(_census_in_child, names))
    procs = time.monotonic() - t0
    for t, n in sorted(per, reverse=True):
        sys.stdout.write(f"{t:6.2f}  {n}\n")
    slowest = max(t for t, _ in per)
    sys.stdout.write(f"serial   {serial:.2f}s\n")
    sys.stdout.write(
        f"threads  {threaded:.2f}s ({serial / threaded if threaded else 0:.1f}x) "
        f"-- GIL-bound: these are re.search over file content, not I/O\n"
    )
    sys.stdout.write(f"procs    {procs:.2f}s ({serial / procs if procs else 0:.1f}x)\n")
    sys.stdout.write(
        f"ceiling  {serial / slowest if slowest else 0:.1f}x -- the floor is the "
        f"slowest single gate ({max(per)[1]} at {slowest:.2f}s); no pool beats it\n"
    )
    return 0


def main(argv: Sequence[str]) -> int:
    """Dispatch: --all (default) prints the rows; --times measures; --selftest runs the suite."""
    known = {"--all", "--selftest", "--times"}
    arg = argv[0] if argv else "--all"
    if arg == "--selftest":
        return _selftest()
    if arg == "--times":
        return _times()
    if arg not in known:
        sys.stderr.write(f"figures.py: unknown flag {arg!r} (known: {' '.join(sorted(known))})\n")
        return 2
    for name, value, detail in report():
        sys.stdout.write(f"{name:<24} {value!s:<6} {detail}\n")
    return 0


class _Origin(Protocol):
    """The figures the differential compares, read through a Protocol off a by-path load."""

    def ratchet_gates(self) -> list[str]: ...
    def gates_without_universal_flags(self, total: list[int]) -> Iterator[str]: ...
    def gates_missing_check_argv(self) -> Iterator[str]: ...
    def census_is_current(self) -> tuple[bool, str]: ...
    def ratchet_census(self, name: str) -> Census: ...
    def own_agda_files_definers(self) -> Iterator[str]: ...


def _summary(c: Census) -> tuple[object, ...]:
    """Reduce a census to (held, over, first key, last key, why) for a legible diff."""
    got, why = c
    if got is None:
        # The one measured difference: the origin's refusal spells its dash `--`, the package's
        # `—`. A `why` is prose for a reader, never a key a consumer matches on.
        return (None, (why or "").replace("--", "—"))
    held, over, keys = got
    return (held, over, keys[0] if keys else None, keys[-1] if keys else None, len(keys))


def _differential(failed: list[str]) -> None:
    """Compare five figures against `catalog/library/figures.py` loaded BY PATH.

    ⚑ THE ORIGIN'S `report()` CANNOT COMPLETE (it dies at `worklist_gate.scratch_size` with its
    rows in a local it never returns), so the figures are compared one by one. Before the swap
    this file is the shim and that path is the ORIGIN; after the swap the path IS this file and
    the arm is the identity - the pre-swap run is the measurement (gate-G448), the post-swap run
    only says the arm still loads.
    """
    import importlib.util

    path = Path(__file__).resolve().parent / "figures.py"
    spec = importlib.util.spec_from_file_location("_figures_origin", path)
    if spec is None or spec.loader is None:
        return
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (ImportError, OSError, RuntimeError):
        sys.stdout.write("  differential: figures.py will not import here, skipped\n")
        return
    o = cast("_Origin", module)
    gates = ratchet_gates()
    theirs_gates = o.ratchet_gates()
    theirs_total, mine_total = [0], [0]
    theirs_lacking = set(o.gates_without_universal_flags(theirs_total))
    mine_lacking = set(gates_without_universal_flags(mine_total))
    # ⚑ THE ROSTER IS THE ONE KNOWN CORRECTION (gate-G448): the origin's substring census counts
    # a file that merely MENTIONS `set_ratchet`. Everything else is compared over the SHARED gates,
    # so a roster delta cannot masquerade as a census delta.
    shared = [g for g in gates if g in set(theirs_gates)]
    # After the swap the loaded module IS this file (it alone declares `gates_outside_scope`),
    # so the roster delta is empty by identity; before it, the delta is the prose-only mention.
    identity = hasattr(module, "gates_outside_scope")
    pairs: list[tuple[str, object, object]] = [
        (
            "roster: the origin's extra gates are prose-only mentions",
            sorted(set(theirs_gates) - set(gates)),
            [] if identity else ["check_baseline_health.py"],
        ),
        ("roster: the shim drops nothing else", sorted(set(gates) - set(theirs_gates)), []),
        (
            "gates_without_universal_flags over the shared gates",
            sorted(theirs_lacking & set(shared)),
            sorted(mine_lacking & set(shared)),
        ),
        (
            "the denominators differ by the roster delta alone",
            theirs_total[0] - mine_total[0],
            len(theirs_gates) - len(gates),
        ),
        (
            "gates_missing_check_argv over the shared gates",
            sorted(set(o.gates_missing_check_argv()) & set(shared)),
            sorted(set(gates_missing_check_argv()) & set(shared)),
        ),
        ("census_is_current", o.census_is_current(), census_is_current()),
        (
            "own_agda_files_definers",
            sorted(o.own_agda_files_definers()),
            sorted(own_agda_files_definers()),
        ),
    ]
    for g in shared:
        t, m = o.ratchet_census(g), ratchet_census(g)
        # Compared as (held, over, keys) but REPORTED as a summary: a 375-key list is not a
        # diagnosis, the first differing key and the two counts are.
        if t == m or (t[0] is None and _summary(t) == _summary(m)):
            continue
        pairs.append((f"ratchet_census({g})", _summary(t), _summary(m)))
    for name, theirs, mine in pairs:
        if theirs != mine:
            failed.append(f"differential: {name}")
            sys.stdout.write(
                f"  FAIL  differential: {name}\n    origin {theirs!r}\n    shim   {mine!r}\n"
            )
    sys.stdout.write(
        f"  differential over {len(shared)} shared gate(s): {len(pairs)} figure(s) "
        f"compared; outside this figure's scope: {', '.join(gates_outside_scope())}\n"
    )


def _selftest() -> int:
    """Run the package suites this shim composes, the differential, then the shape cases."""
    import subprocess

    suites = ("leaf_ledger", "failure_census", "key_partition", "kind_cone", "site_paydown")
    failed: list[str] = []
    _differential(failed)
    for s in suites:
        p = subprocess.run(
            [sys.executable, "-m", f"substrate.{s}_selftest"],
            capture_output=True,
            text=True,
            check=False,
            cwd=ROOT,
        )
        sys.stdout.write((p.stdout.strip().splitlines() or [f"{s}: no output"])[-1] + "\n")
        if p.returncode != 0:
            failed.append(s)
    one = ratchet_gates()[:1]
    rows = report(one)
    cases = [
        ("report rows are 3-tuples", all(len(r) == 3 for r in rows)),
        (
            "scratch-bytes-held reads wg_engine, an int",
            any(r[0] == "scratch-bytes-held" and isinstance(r[1], int) for r in rows),
        ),
        (
            "sweeps-without-denominator answers rather than refusing",
            any(r[0] == "sweeps-without-denominator" and r[1] != "n/a" for r in rows),
        ),
        ("a narrowed sweep reports one gate row", sum(r[0].endswith("-added") for r in rows) == 1),
        ("DERIVED types the two census artifacts", DERIVED["agda/_build"] == "CENSUS"),
    ]
    for name, ok in cases:
        if not ok:
            failed.append(name)
            sys.stdout.write(f"  FAIL  {name}\n")
    total = len(suites) + len(cases)
    sys.stdout.write(f"figures_selftest: {total - len(failed)}/{total}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
