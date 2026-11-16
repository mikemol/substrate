#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Λ8 — the gate: a promoted project makes NO LIVE scratch/ reference.

⚑⚑⚑ THE FOURTH DRAIN OF THE ⟡drain-arc, and the one that carries the VERDICT. The invariant
(the G9 escalation from the 2026-06-17 scratch-dissolution arc): once a project is promoted out
of `scratch/`, it must not silently re-acquire a runtime dependency on it. Before the gate,
"is jea independent of scratch?" was answered by re-grepping by hand, and the answer was wrong
twice. The gate makes it correct-by-construction: a live reference blocks the commit.

LIVE = `scratch` in EXECUTABLE CODE — a string literal used as a path, or an import naming
scratch. EXEMPT = comments, docstrings, and all `.md`/`.agda` prose; a dated ledger note is a
historical fact with no runtime dependency. The exemption is MECHANICAL: `scratch_refs.scan_file`
parses with `ast`, so comments are absent by construction and docstrings are the identifiable
first-Expr-Constant of a scope.

⚑⚑ SEVERITY, NOT JUST PRESENCE. `scan_file` labels every hit `[path-string]`, so a `"scratch"`
inside a log message and a `sys.path.insert(0, …"scratch")` feeding an `import` two lines down
render IDENTICALLY. Measured on `jea/metalanguage/sql_lift.py:809-810`, a HARD runtime coupling
the gate reported with the same label as cosmetic text — so a reader triaging by label
deprioritised the one that actually breaks. `dependency_sites` draws that line; the verdict is
unchanged (any hit fails) but RUNTIME couplings render FIRST, marked, and the count of each is
in the headline.

⚑ THE GATE'S WALK HAS NO SKIP LIST AND NO ORDERING, verbatim from the origin: every `.py`
under a root is scanned, `.venv` and `__pycache__` included if present — they are not present
under the promoted roots today, and the differential is against the origin's own output, so
the walk is not narrowed here. The report is sorted (runtime first, then path, then line), so
walk order never reaches the reader.

Scope: `substrate.promoted.ROOTS` by default — the authority, which lists `substrate/` where the
origin's own roster (frozen behind the per-file gate) does not. `run` takes the roster as a
parameter and the result CARRIES it, so the differential can ask the origin's question and a
report always names the roster it was computed over. `scripts/` is NOT guarded — that exclusion
licenses el-atlas→scripts/ and says nothing about scripts/→scratch/, which `--scope` measures.

⚑ THE TREE IS A REQUIRED ARGUMENT (2026-09-24, operator: "We should not have things [like]
corpus.ROOT"). `run` used to default `root` to `corpus.ROOT`; the entry point (`scratch_cli`,
reading `--root`) now chooses it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import scratch_refs as sr
from substrate.promoted import ROOTS

if TYPE_CHECKING:
    from pathlib import Path

# The two severities a hit renders under.
DEP = "DEP"
TEXT = "text"

# The origin's closing prose, kept so the differential holds.
_RUNTIME_NOTE = (
    "  ⚑ The {n} RUNTIME ref(s) are a real coupling — a `sys.path.insert` feeding "
    "an import, or an import naming scratch. The promoted project CANNOT RUN "
    "without scratch/. Repoint by PROMOTING the module (`--promotable <dir>`), "
    "not by repathing."
)
_REPAIR_NOTE = (
    "  A promoted project must not depend on scratch/ at runtime. Either repoint "
    "the path to the artifact's real home, or — if this is a dated HISTORICAL note "
    "— move it into a comment or a .md ledger (those are exempt; live code is not)."
)


@dataclass(frozen=True, slots=True)
class Hit:
    """One live reference under a promoted root, with its severity."""

    relpath: str
    lineno: int
    kind: str
    snippet: str
    severity: str


@dataclass(frozen=True, slots=True)
class Result:
    """What the gate scanned and found, over which roster — the verdict is `not hits`."""

    hits: tuple[Hit, ...]
    warns: tuple[str, ...]
    scanned: int
    roots: tuple[str, ...]

    @property
    def ok(self) -> bool:
        """Report whether the promoted corpus is scratch-free."""
        return not self.hits

    @property
    def runtime(self) -> int:
        """Count the hits that are real couplings."""
        return sum(1 for h in self.hits if h.severity == DEP)


def _order(h: Hit) -> tuple[bool, str, int]:
    """Return the report's sort key: runtime first, then path, then line."""
    return (h.severity != DEP, h.relpath, h.lineno)


def _files(root: Path, roots: tuple[str, ...]) -> list[Path]:
    """Return every `.py` under every present root — no skip list, see the header."""
    return [p for r in roots if (root / r).is_dir() for p in (root / r).rglob("*.py")]


def _hits_of(path: Path, root: Path) -> tuple[list[Hit], tuple[str, ...]]:
    """Classify one file's hits by whether each is a dependency site or an import."""
    scan = sr.scan_file(path)
    deps = sr.dependency_sites(path)
    rel = str(path.relative_to(root))
    hits = [
        Hit(
            rel,
            h.lineno,
            h.kind,
            h.snippet,
            DEP if (h.lineno in deps or h.kind == sr.IMPORT) else TEXT,
        )
        for h in scan.hits
    ]
    return hits, scan.warns


def run(root: Path, roots: tuple[str, ...] = ROOTS) -> Result:
    """Scan every promoted root under the tree `root` and return the gate's result."""
    hits: list[Hit] = []
    warns: list[str] = []
    files = _files(root, roots)
    for path in files:
        found, w = _hits_of(path, root)
        hits.extend(found)
        warns.extend(w)
    return Result(tuple(hits), tuple(warns), len(files), roots)


def render(result: Result) -> tuple[list[str], list[str]]:
    """Render the gate's report as `(stdout, stderr)` lines, in the origin's words.

    Warnings and the FAILED report go to stderr; the OK line goes to stdout. A caller that
    wants `--quiet` drops the stdout half — the verdict is in the exit code, not the line.
    """
    err = [f"  scratch-independence: WARN {w}" for w in result.warns]
    roots = "/".join(result.roots)
    if result.ok:
        ok = (
            f"scratch-independence (Λ8): OK ({result.scanned} .py scanned across {roots}, "
            f"0 live refs)"
        )
        return [ok], err
    n_dep = result.runtime
    err.append(
        f"scratch-independence (Λ8): FAILED — {len(result.hits)} LIVE scratch/ "
        f"reference(s) in a promoted project ({roots}) — {n_dep} RUNTIME, "
        f"{len(result.hits) - n_dep} text:"
    )
    for h in sorted(result.hits, key=_order):
        mark = "⚑ RUNTIME" if h.severity == DEP else "  text   "
        err.append(f"    {mark}  {h.relpath}:{h.lineno}  [{h.kind}]  {h.snippet}")
    if n_dep:
        err.append(_RUNTIME_NOTE.format(n=n_dep))
    err.append(_REPAIR_NOTE)
    return [], err
