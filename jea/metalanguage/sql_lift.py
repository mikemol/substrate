#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""sql_lift - the graded-relational-carrier lift map, assembled from the package.

THE COSPAN `Python-ops -> R <- SQL-ops`: the common carrier R is a GradedProductOver over
(N, +, 0) whose elements are relational-op PIPELINES and whose grade is composition depth. Both
sides lower through a GradedHomOver into one shared interner, and a python op is a LICENSED LIFT
exactly when its Rel-lowering is grade-0 coherent with an SQL construct - proved by
same-interned-id, never by similarity. The grade IS the liftability boundary: a bounded pipeline
flattens to a relational normal form; an unbounded one (a recursive walk) is placed on the
recursion/loop/parallel triangle instead, where the recursion-to-parallel transition lifts a
closure to `WITH RECURSIVE`.

THIS FILE IS A SHIM (W4 file 3 swap, tick 37). Every mechanism lives in the package and is
witnessed there: `substrate.rel_term` (RelTerm, the python lowering, licensed_lifts),
`substrate.rel_bridges` (the Select and numpy lowerings, coherence), `substrate.recursion_class`
(the L6 pole classifier), `substrate.sql_circuit` (the H4 conductance roofline). What stays here
is what needs the ORIGIN'S neighbours: the interner (`jea_pyalg`), the compiled builders
(`query_defs.INTERN_BUILDERS`), the declared relations (`schema_decl.MD`), and the census modes
(`sql_census`). Three adaptors join them - an interner over `Intern`/`IR`, `CrossMix.coherent`
as the coherence predicate, and `RelTerm -> (heads, breadth)` for the roofline - so nothing
below decides anything the package does not already decide.

THE SUITE HERE IS THE CORPUS HALF ONLY. The origin's mechanism cases moved out with the modules
(sql_circuit 22, rel_term 41, recursion_class 22, rel_bridges 21); what remains are the arms that
need the real tree - the render_graph/render_import ACCEPT lift, the five carrier-unmodelled
walks with their liftable control, lsz as residue, pack as not-a-recursion, q_reach as Closure.
The three `canon_syms` arms are DROPPED: they failed in the origin because `sppf_db.canon_syms`
no longer classifies as a walk (a corpus fact), and `recursion_class_selftest` pins what they
specified on a stable fixture (gate-G414). Dropping a red arm is recorded here, not hidden.
"""

from __future__ import annotations

import ast
import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, cast

from jea_pyalg import IR, CrossMix, Intern
from query_defs import INTERN_BUILDERS
from schema_decl import MD
from sqlalchemy.sql.selectable import Select

from substrate import recursion_class, rel_bridges, rel_term, sql_circuit
from substrate.rel_term import REL_HEADS, RelTerm

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping

__all__ = [
    "REL_HEADS",
    "RelTerm",
    "build",
    "licensed_lifts",
    "np_sql_coherent",
    "report",
    "roofline",
    "selftest",
]

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
# How many entries a report section lists before eliding the rest.
_LIST_CAP = 12
_SITE_CAP = 4

Record = tuple[str, int, str, recursion_class.Verdict]
Lift = tuple[RelTerm, list[RelTerm]]
Cases = list[tuple[str, bool]]


def _say(line: str) -> None:
    """Print one report line."""
    sys.stdout.write(line + "\n")


def _py_files() -> list[Path]:
    """Return the default corpus: this directory's modules and the repo's scripts."""
    return sorted(set(HERE.glob("*.py")) | set((REPO / "scripts").glob("*.py")))


def _interner(i: Intern) -> Callable[[str, str | None, tuple[int, ...]], int]:
    """Adapt an `Intern` to the package's `(op, lit, children) -> id` shape."""

    def intern(op: str, lit: str | None, children: tuple[int, ...]) -> int:
        return i.intern(IR(kind="Rel", op=op, lit=lit or "", children=children))

    return intern


def roofline(rt: RelTerm, n: float | None = None, branches: int = 1) -> sql_circuit.Roofline:
    """Return the H4 readout for a term - the package roofline over its heads and breadth."""
    return sql_circuit.roofline(rt.heads, len(rt.sites), n, branches)


def licensed_lifts(_i: Intern, py: Mapping[int, RelTerm], sql: Mapping[int, RelTerm]) -> list[Lift]:
    """Return the licensed lifts; the interner is accepted for the consumer's arity and unused."""
    return rel_term.licensed_lifts(py, sql)


def np_sql_coherent(i: Intern, np_heads: Iterable[str], sql_stmt: Select) -> bool:
    """Return whether a numpy chain and a Select meet at one carrier node under `i`."""
    return rel_bridges.np_sql_coherent(_interner(i), np_heads, sql_stmt, CrossMix(i).coherent)


def _walk_file(
    path: Path, i: Intern, py: dict[int, RelTerm], rec: list[Record], declared: frozenset[str]
) -> None:
    """Intern one file's pipelines and classify its walks."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return
    rel = str(path.relative_to(REPO)) if path.is_relative_to(REPO) else str(path)
    intern = _interner(i)
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for rt in rel_term.terms_of_function(node):
            py.setdefault(rt.intern_into(intern), rt).sites.append((rel, node.lineno, node.name))
        cls = recursion_class.classify(node, declared)
        if cls is not None:
            heads = (("Agg",) if cls["scheme"].startswith("fold") else ()) + ("Closure",)
            if cls["sql_target"] != "residue":
                RelTerm(heads, "*").intern_into(intern)
            rec.append((rel, node.lineno, node.name, cls))


def _lower_builder(thunk: Callable[[], object]) -> RelTerm | None:
    """Lower one compiled builder, or None when it needs parameters or is not a SELECT.

    A write builder (`INTERN_BUILDERS` holds an `Insert` too) has no Rel lowering; the origin
    hid that under the same `except Exception` that skips a parameterised builder. Here the
    narrowing is explicit, so a non-SELECT is a stated skip rather than a swallowed error.
    """
    try:
        stmt = thunk()
    except Exception:  # noqa: BLE001 - a builder needing params is still a builder; it is skipped
        return None
    return rel_bridges.rel_of_select(stmt) if isinstance(stmt, Select) else None


def build(
    files: list[Path] | None = None,
) -> tuple[Intern, dict[int, RelTerm], dict[int, RelTerm], list[Record]]:
    """Intern the SQL builders and every python pipeline into ONE carrier; return the four maps."""
    i = Intern()
    py: dict[int, RelTerm] = {}
    rec: list[Record] = []
    declared = frozenset(MD.tables)
    for path in files or _py_files():
        _walk_file(path, i, py, rec, declared)
    sql: dict[int, RelTerm] = {}
    intern = _interner(i)
    for name, thunk in INTERN_BUILDERS.items():
        rt = _lower_builder(thunk)
        if rt is not None:
            sql.setdefault(rt.intern_into(intern), rt).sites.append(("query_builders", 0, name))
    return i, py, sql, rec


def _seq(rt: RelTerm) -> str:
    """Render a term's non-Scan heads in SQL order."""
    return " -> ".join(h for h in rt.canon_seq() if h != "Scan")


def _by_scheme(r: Record) -> str:
    """Sort key: a record's scheme."""
    return r[3]["scheme"]


def _by_fanin(rt: RelTerm) -> tuple[int, int]:
    """Sort key: widest fan-in first, then deepest grade."""
    return (-len(rt.sites), -rt.grade)


def _report_lifts(lifts: list[Lift]) -> None:
    """Print the licensed lifts, steered by the conductance bridge times breadth."""
    n = sql_circuit.n_estimate()
    _say(
        f"LICENSED LIFTS - STEER by the conductance bridge sign(G_cte - G_eager) x breadth at "
        f"N~{int(n)} (H4: the 275x/0.7x regime is a bridge-null OUTPUT, not a flat 2.5k):\n"
    )
    for rt, matches in lifts:
        sset = ", ".join(sorted({s[2] for srt in matches for s in srt.sites})[:_SITE_CAP])
        rf = roofline(rt)
        _say(
            f"  score {rf['score']:+.4f}  {rf['regime']:5s} x{rf['speedup']:.2f} @N={rf['N']:.0f}"
            f"  ({rf['k']} heads x {len(rt.sites)} sites)  [{_seq(rt)}]  <- SQL: {sset}"
        )
        for site in rt.sites[:_SITE_CAP]:
            _say(f"        {site[0]}:{site[1]}  {site[2]}()")
    if not lifts:
        _say("  (none)")
        return
    rf0 = roofline(lifts[0][0])
    _say(
        f"\n  -> STEER: lift `[{_seq(lifts[0][0])}]` first (score {rf0['score']:+.4f}, regime "
        f"{rf0['regime']}: the highest conductance advantage x breadth at the estimated N)."
    )


def _report_recursion(rec: list[Record], sql: Mapping[int, RelTerm]) -> None:
    """Print the recursion-pole split: liftable, residue, carrier-unmodelled."""
    cte = [r for r in rec if r[3]["transition"] == recursion_class.RECURSION_TO_PARALLEL]
    residue = [r for r in rec if r[3]["sql_target"] == "residue"]
    und = [r for r in rec if r[3]["verdict"] == "carrier-unmodelled"]
    has_cte = any("Closure" in rt.heads for rt in sql.values())
    tgt = (
        "MATCHES query_builders.q_reach (WITH RECURSIVE)"
        if has_cte
        else "RECOMMENDED (no WITH RECURSIVE builder in production yet)"
    )
    _say(
        f"\nRECURSION->PARALLEL (a greatest-fp recursion -> a least-fixpoint WITH RECURSIVE) - "
        f"{len(cte)} of {len(rec)} recursion-pole computations lift."
    )
    _say(f"  recursion->parallel target: {tgt}")
    for path, ln, name, cls in sorted(cte, key=_by_scheme):
        _say(f"  {cls['sql_target']:26}  {name}()  ({cls['scheme']})  {path}:{ln}")
        if cls["reads"]:
            _say(f"      reads: {', '.join(cls['reads'])}")
    _say(f"\nRESIDUE (stays python - no relational/declarative form) - {len(residue)}:")
    for path, ln, name, cls in residue[:_LIST_CAP]:
        mark = "  REFUTED - " + cls["why"] if cls["verdict"] == "REFUTED" else ""
        _say(f"  {name}()  {cls['scheme']} - {cls['reason']}  {path}:{ln}{mark}")
    _say(
        f"\nCARRIER-UNMODELLED (a closure whose carrier has no relational model YET - WORK, "
        f"not a wall) - {len(und)}:"
    )
    for path, ln, name, cls in und[:_LIST_CAP]:
        _say(f"  {name}()  {cls['scheme']}  {path}:{ln}")
    if len(und) > _LIST_CAP:
        _say(f"  ... {len(und) - _LIST_CAP} more")


def report(files: list[Path] | None = None) -> None:
    """Print the lift map over the corpus."""
    i, py, sql, rec = build(files)
    lifts = licensed_lifts(i, py, sql)
    _say(
        f"graded-relational-carrier - {len(py)} distinct python Rel-pipelines, {len(sql)} SQL "
        f"builder pipelines, interned into ONE carrier ({i.size()} nodes)\n"
    )
    _report_lifts(lifts)
    shared = [rt for rt in py.values() if len(rt.sites) > 1 and len(_seq(rt).split()) > 1]
    _say(f"\nORBIT-DEDUP: {len(shared)} composed python Rel-pipeline(s) recur across >=2 sites:")
    for rt in sorted(shared, key=_by_fanin):
        sites = "; ".join(f"{s[0]}:{s[1]}({s[2]})" for s in rt.sites[:_SITE_CAP])
        _say(f"  fan-in {len(rt.sites)}  grade {rt.grade}  [{_seq(rt)}]  sites: {sites}")
    _report_recursion(rec, sql)


_PACKAGE_SUITES = ("sql_circuit", "rel_term", "recursion_class", "rel_bridges")
_UNMODELLED_WALKS = ("_support", "_subnodes", "descsh", "sz", "hei")
_ACCEPT_FNS = frozenset({"render_graph", "render_import"})


def _names(rt: RelTerm) -> set[str]:
    """Return the function names a term is emitted from."""
    return {s[2] for s in rt.sites}


def _accept_cases(cases: Cases) -> None:
    """Pin the L3 acceptance over scripts/reuse_catalog.py - the headline lift."""
    i2, pyt, sqlt, _ = build([REPO / "scripts" / "reuse_catalog.py"])
    lifts = licensed_lifts(i2, pyt, sqlt)
    cases.append(
        (
            "render_graph/render_import [OrderBy->Limit] is ONE licensed lift, breadth >= 2",
            any(_seq(rt) == "OrderBy -> Limit" and _names(rt) >= _ACCEPT_FNS for rt, _m in lifts),
        )
    )
    cases.append(
        (
            "Counter (GroupBy->Agg) is ONE shared carrier node across both",
            any(_seq(rt) == "GroupBy -> Agg" and _names(rt) >= _ACCEPT_FNS for rt in pyt.values()),
        )
    )
    scores = [roofline(rt)["score"] for rt, _m in lifts]
    cases.append(
        ("licensed lifts are steered (sorted) by score", scores == sorted(scores, reverse=True))
    )
    cases.append(
        (
            "the SQL corpus contains a Closure builder (q_reach lowers to Rel(Closure))",
            any("Closure" in rt.heads for rt in sqlt.values()),
        )
    )


def _walk_cases(cases: Cases) -> None:
    """Pin the L6 split over the four files the origin classified."""
    files = (
        REPO / "scripts" / "reuse_tui.py",
        HERE / "jea_pysim.py",
        HERE / "jea_pyalg.py",
        REPO / "scripts" / "sppf_db.py",
    )
    walks: dict[str, recursion_class.Verdict] = {
        nm: cls for f in files for _p, _l, nm, cls in build([f])[3]
    }
    for fn in _UNMODELLED_WALKS:
        cases.append(
            (
                f"{fn} walks an IN-MEMORY carrier -> carrier-unmodelled",
                fn in walks and walks[fn]["verdict"] == "carrier-unmodelled",
            )
        )
    lift = [nm for nm, c in walks.items() if c["verdict"] == "derived-liftable"]
    cases.append(("...while a walk over DECLARED relations is still derived-liftable", bool(lift)))
    cases.append(
        (
            "...and every derived verdict names the relations that decided it",
            all(walks[nm]["reads"] for nm in lift),
        )
    )
    cases.append(
        ("lsz (log-sum-exp) is residue", "lsz" in walks and walks["lsz"]["sql_target"] == "residue")
    )
    cases.append(("pack is a depth-1 self-join, NOT a recursion pole", "pack" not in walks))


_ORIGIN = HERE / "sql_lift_origin.py"


class _OriginTerm(Protocol):
    @property
    def heads(self) -> tuple[str, ...]: ...
    @property
    def sites(self) -> list[tuple[str, int, str]]: ...


class _Origin(Protocol):
    def build(
        self,
        files: list[str] | None = None,
    ) -> tuple[object, dict[int, _OriginTerm], dict[int, _OriginTerm], list[object]]: ...


def _origin() -> _Origin | None:
    """Load the pre-swap origin by PATH while it is kept beside the shim, else None."""
    if not _ORIGIN.exists():
        return None
    spec = importlib.util.spec_from_file_location("_sql_lift_origin_diff", _ORIGIN)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return cast("_Origin", module)


def _sql_names(sql: Mapping[int, _OriginTerm]) -> dict[str, tuple[str, ...]]:
    """Return builder name -> heads, the SQL side of a build as a comparable map."""
    # ⚑ `s[-1]`: the origin's SQL sites are `("query_builders", name)`, the shim's carry a line.
    return {s[-1]: rt.heads for rt in sql.values() for s in rt.sites}


def _origin_cases(cases: Cases) -> None:
    """Differential against the origin over one corpus file, or skip once it is retired."""
    o = _origin()
    if o is None:
        cases.append(("differential: origin retired, skipped", True))
        return
    corpus = REPO / "scripts" / "reuse_catalog.py"
    _i, py, sql, rec = build([corpus])
    _oi, opy, osql, orec = o.build([str(corpus)])
    cases.append(("differential: the python pipeline count agrees", len(py) == len(opy)))
    cases.append(("differential: the recursion-pole count agrees", len(rec) == len(orec)))
    ours, theirs = _sql_names(sql), _sql_names(osql)
    extra, missing = sorted(set(ours) - set(theirs)), sorted(set(theirs) - set(ours))
    cases.append(
        (f"differential: the shim lowers no builder the origin did not (extra={extra})", not extra)
    )
    # ⚑ TWO CORRECTIONS THE DIFFERENTIAL FOUND, PINNED AS DIRECTIONS RATHER THAN HIDDEN. The
    # origin lowered NON-SELECT builders (an INSERT, a DELETE, a compound) through `getattr`
    # defaults into a phantom `("Scan",)` pipeline; the shim narrows on `Select`, so exactly the
    # non-Select builders go missing. And the origin's `type(el).__name__ == "Function"` misses
    # `func.count()` - class `count`, a `Function` SUBCLASS - so it under-reported `Agg`; the shim's
    # `isinstance` finds it, so where heads differ the shim's set is the origin's plus `Agg`.
    non_select = {n for n, t in INTERN_BUILDERS.items() if not _is_select(t)}
    name = f"differential: the missing builders are exactly the non-SELECT ones (missing={missing})"
    cases.append((name, set(missing) <= non_select))
    both = set(ours) & set(theirs)
    differ = sorted(n for n in both if ours[n] != theirs[n])
    only_agg = all(
        set(ours[n]) - set(theirs[n]) == {"Agg"} and set(theirs[n]) <= set(ours[n]) for n in differ
    )
    name = f"differential: heads differ only by the origin's missed Agg ({len(differ)} builders)"
    cases.append((name, only_agg))


def _is_select(thunk: Callable[[], object]) -> bool:
    """Return whether a builder yields a SELECT; a raising builder counts as not-a-select."""
    try:
        return isinstance(thunk(), Select)
    except Exception:  # noqa: BLE001 - a builder needing params is skipped by build() too
        return False


def selftest() -> int:
    """Run the four package suites, then the corpus arms; print `selftest: N/M`."""
    cases: Cases = []
    for suite in _PACKAGE_SUITES:
        argv = [sys.executable, "-m", f"substrate.{suite}_selftest"]
        rc = subprocess.run(argv, check=False, cwd=REPO, capture_output=True).returncode  # noqa: S603 - fixed argv
        cases.append((f"package suite {suite}_selftest exits 0", rc == 0))
    _accept_cases(cases)
    _walk_cases(cases)
    _origin_cases(cases)
    failed = [n for n, ok in cases if not ok]
    for n in failed:
        _say(f"  FAIL  {n}")
    _say(f"selftest: {len(cases) - len(failed)}/{len(cases)}")
    return 1 if failed else 0


def _census(sync: bool) -> int:  # noqa: FBT001 - one flag, one branch
    """Dispatch the census modes; a missing marker pair exits 1, not 2."""
    import sql_census  # noqa: PLC0415 - reached only by the two census modes

    try:
        return sql_census.cmd_sync() if sync else sql_census.cmd_check()
    except sql_census.BlockError as e:
        sys.stderr.write(f"sql_lift: {e}\n")
        return 1


_USAGE = """usage: sql_lift.py --selftest | --report | --sync-census | --check-census
  --selftest      the four package suites + the corpus arms; exit 1 on any failure
  --report        the lift map over the corpus
  --sync-census   rewrite the generated block in .claude/skills/sql-relalg/SKILL.md
  --check-census  DRIFT GATE: exit 1 unless that block is what --sync-census would write
"""


def _report_mode() -> int:
    """Run the report; it never fails."""
    report()
    return 0


def main(argv: list[str]) -> int:
    """Dispatch one mode; an unknown or missing mode prints usage and exits 2."""
    modes: dict[str, Callable[[], int]] = {
        "--selftest": selftest,
        "--report": _report_mode,
        "--sync-census": lambda: _census(sync=True),
        "--check-census": lambda: _census(sync=False),
    }
    if len(argv) != 1 or argv[0] not in modes:
        sys.stderr.write(_USAGE)
        return 2
    return modes[argv[0]]()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
