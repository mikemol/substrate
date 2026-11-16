# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The FACTS the build census renders, each read from the file that owns it, never restated.

⚑⚑⚑ DRAINED FROM `scripts/build_census.py` (W329). That file carried 376 findings, so the
per-file gate refused every edit; its derivations moved here, and `build_census_render` and
`build_census_skill` took the rest. Each function returns PLAIN DATA: nothing here formats
and nothing judges.

⚑⚑ THE TREE IS A PARAMETER. The origin resolved `HERE`/`REPO` from its own `__file__` at
import, so no caller could point it at a fixture. Every reader here takes the repo root (and
the `scripts/` directory where a bare-named sibling must be loaded); the CLI entry resolves
them at call time.

⚑⚑ THE MEMBUDGET CLIENT IS TEXT-PARSED, DELIBERATELY AND FOR NOW. `scripts/membudget` is a
bash script, so its lease defaults and subcommand roster are read by regex from its SOURCE.
The path comes from `build_settings.MEMBUDGET` (one owner); a follow-up swaps the parse for
the python client's own describe surface. Until then the loud refusal stays: a respelled
assignment must FAIL, never default.

⚑ THE DAG'S ROOT IS NOT A PARAMETER YET. `agda_dag` is anchored to `corpus.ROOT`, so
`dag_census` takes only the `scripts/` directory (for the comment stripper). That residue is
owned by `agda_dag`.
"""

from __future__ import annotations

import importlib.util
import re
from typing import TYPE_CHECKING, Protocol, TypedDict, cast

from substrate import build_compat, build_settings, sibling_finder

if TYPE_CHECKING:
    from pathlib import Path
    from types import ModuleType

# The membudget authority: parsed, NEVER restated.
#
# ⚑ THIS IS THE `agda-shim` LESSON APPLIED. That file refused to restate AGDA_MB and cited a
# LINE NUMBER instead, and the line moved, so the anti-drift pointer became the drift. A line
# number is itself a restatement of something mutable. Key on the ASSIGNMENT TEXT, which
# moves with the code, and REFUSE when it is not found rather than defaulting.
MB_RE = re.compile(r'def="\$\{AGDA_MB_DEFAULT:-(\d+)\}"\s+cap="\$\{AGDA_MB_MAX:-(\d+)\}"')

# The subcommand roster: a `case` arm indented two to four spaces, e.g. `  run)`.
CMD_RE = re.compile(r"^\s{2,4}([a-z][a-z-]+)\)\s", re.MULTILINE)

# The gate roster: parsed from the pre-commit hook's own `run` call sites.
#
# ⚑ THE POPULATION IS THE DECLARATION, NOT THE LEDGER. `gate_ledger.py --report` can only
# rank gates it has OBSERVED and reads as complete, the census-keyed-on-one-spelling shape.
# The declared population lives in the hook, and this is the reader for it.
RUN_RE = re.compile(r'^\s*run\s+"([^"]+)"', re.MULTILINE)

# ⚑ THE PHASES ARE NOT LABELLED IN THE HOOK, so they are keyed on the two STRUCTURAL anchors
# that actually create them: the full build, and the reorder marker that moved the
# core-reading gates after it. A first cut looked for `# Phase A/B/C` comments, found none,
# and rendered every gate under one heading, a confident flattening of the very distinction
# this census exists to preserve.
# ⚑⚑ ANCHOR ON THE INVARIANT SUBSTRING, NOT THE WHOLE COMMAND LINE. The directory is what
# makes the make line the full build; the flags are what change around it (⟡agda-jobs
# rewrote them once and a verbatim anchor would have silently collapsed every gate into
# Phase A).
PHASE_ANCHORS = (
    ('make -C "$ROOT/agda"', "Phase B — the full build"),
    ("⟡gqs-precommit-reorder", "Phase C — core-reading gates (AFTER the build)"),
)
PHASE_A = "Phase A — cheap gates (BEFORE the build)"

HOOK_REL = ".githooks/pre-commit"
TIMES_COLS = ("module", "seconds", "peak_mb")
PROFILE_COLS = ("module", "total_ms", "checkrhs_ms", "cmp_reduce", "alloc_mb", "peak_mb", "gc_pct")

#: The tools that OWN a question about this surface: path to the question it answers.
#:
#: ⚑ DATA, NOT PROSE, so the block can assert each path still exists: a tool that is renamed
#: or deleted breaks the gate instead of rotting into a false pointer.
READERS = (
    ("scripts/gen_build_makefiles.py", "THE build authority — MEM_CAP, the import DAG, Flat.mk"),
    ("agda/Flat.mk", "the generated flat DAG — one real-file rule per module"),
    ("scripts/membudget", "THE lease authority — budget, cgroup scope, retry-on-OOM"),
    ("scripts/agda-shim/agda", "the PATH shim — every agda routes through membudget"),
    ("scripts/buildtime.py", "the TIME/PEAK ledger reader — predict, top, module, mem"),
    ("scripts/proofcost.py", "the PROOF-COST profiler — phases, alloc, GC, the regime oracle"),
    ("scripts/cap_diagnose.py", "elaboration-bound vs load-bound, by three real compiles"),
    ("scripts/check_cap_ratchet.py", "the per-module peak DEBT ratchet toward the cap"),
    ("scripts/gate_ledger.py", "gate outcomes — order, report (OBSERVED, not declared)"),
    ("scripts/run_selftests.py", "every tool's --selftest suite"),
    (".githooks/pre-commit", "THE gate declaration — three phases around the full build"),
)


class _AgdaText(Protocol):
    def strip(self, text: str, /) -> str: ...


class _LedgerModule(Protocol):
    LEDGER: str
    KEEP: int


class DagFacts(TypedDict):
    """The import DAG's figures."""

    modules: int
    edges: int
    depth: int
    roots: int
    leaves: int
    top_in: list[tuple[str, int]]
    top_out: list[tuple[str, int]]
    mem_cap: str
    build_ver: str


class MembudgetFacts(TypedDict):
    """The lease defaults and the subcommand roster."""

    default_mb: int
    max_mb: int
    commands: list[str]


class LedgerFacts(TypedDict):
    """The two per-dir ledger schemas."""

    times_ledger: str
    times_keep: int
    times_cols: tuple[str, ...]
    profile_ledger: str
    profile_keep: int
    profile_cols: tuple[str, ...]


class GateFacts(TypedDict):
    """The declared gates in hook order, with the phase each falls in."""

    gates: list[tuple[str, str]]
    count: int
    phases: list[str]


def load_script(scripts: Path, stem: str) -> ModuleType:
    """Load `<scripts>/<stem>.py` by LOCATION, with its bare siblings resolvable for the load.

    ⚑ A FINDER, NOT A `sys.path` INSERT: the origin edited the interpreter's search path for
    the whole process; the sibling finder answers for one directory and is removed when the
    load returns.
    """
    path = scripts / f"{stem}.py"
    spec = importlib.util.spec_from_file_location(stem, path)
    if spec is None or spec.loader is None:
        msg = f"cannot load {path}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    with sibling_finder.siblings_of(scripts):
        spec.loader.exec_module(module)
    return module


def _count_then_name(item: tuple[str, int]) -> tuple[int, str]:
    """Order `(name, count)` rows by descending count, then name."""
    return (-item[1], item[0])


def dag_census(scripts: Path) -> DagFacts:
    """Return the import DAG, from the generator's OWN parse, never re-parsed here.

    ⚑ NO FALLBACK ON ANY COUNT. A defaulted count would render `0 modules` the day a symbol
    moves: a figure that looks like a measurement and is an attribute miss. Let it raise.
    """
    strip = cast("_AgdaText", load_script(scripts, "_agdatext")).strip
    disk, deps = build_compat.parse_tree(strip)
    depth, _order = build_compat.kahn_depth(disk, deps)
    edges = sum(len(v) for v in deps.values())
    fan_in: dict[str, int] = {}
    for module in disk:
        for dep in deps[module]:
            fan_in[dep] = fan_in.get(dep, 0) + 1
    top_in = sorted(fan_in.items(), key=_count_then_name)[:5]
    top_out = sorted(((m, len(deps[m])) for m in disk), key=_count_then_name)[:5]
    return {
        "modules": len(disk),
        "edges": edges,
        "depth": depth,
        "roots": len([m for m in disk if not deps[m]]),
        "leaves": len([m for m in disk if m not in fan_in]),
        "top_in": top_in,
        "top_out": top_out,
        "mem_cap": build_settings.MEM_CAP,
        "build_ver": build_settings.build_ver(),
    }


def membudget_census(client: Path) -> MembudgetFacts:
    """Return the lease defaults and subcommand roster, parsed from the client's SOURCE."""
    src = client.read_text(encoding="utf-8")
    found = MB_RE.search(src)
    if not found:
        # ⚑ REFUSE, never default. A census cannot distinguish "no default declared" from
        # "the assignment was respelled"; only a failure can.
        msg = (
            "build_census: could not find the AGDA_MB_DEFAULT/AGDA_MB_MAX assignment in "
            "scripts/membudget — it was respelled. Update _MB_RE; do NOT hardcode the values."
        )
        raise RuntimeError(msg)
    cmds = sorted({str(c.group(1)) for c in CMD_RE.finditer(src)})
    return {
        "default_mb": int(str(found.group(1))),
        "max_mb": int(str(found.group(2))),
        "commands": cmds,
    }


def membudget_from_describe(text: str) -> MembudgetFacts:
    """Return the same facts from `mikemol-membudget describe` rows (W331, mtools:W964).

    The python client has no source to regex, so it prints PARSEABLE ROWS: `default_mb N`,
    `max_mb N`, and one `verb NAME` per verb, the verbs read from its dispatch table so the
    roster cannot drift from what the client does. This is the pure half (the text in, the facts
    out); running the client is the caller's, so the suite never starts one.

    ⚑ EVERY SHAPE THAT IS NOT THE CONTRACT REFUSES, as the bash arm does for a respelled
    assignment: a missing or repeated figure, a non-integer, no verb at all, and a row kind this
    reader has not seen (a changed format must be REVIEWED, not absorbed into a quiet default).
    """
    figures: dict[str, int] = {}
    verbs: set[str] = set()
    for line in text.splitlines():
        parts = line.split()
        if not parts:
            continue
        kind, rest = parts[0], parts[1:]
        if kind == "verb" and len(rest) == 1:
            verbs.add(rest[0])
        elif kind in ("default_mb", "max_mb") and len(rest) == 1 and rest[0].isdigit():
            if kind in figures:
                msg = f"build_census: describe printed {kind!r} twice; refusing to pick one"
                raise RuntimeError(msg)
            figures[kind] = int(rest[0])
        else:
            msg = f"build_census: unrecognised describe row {line!r}; the format changed"
            raise RuntimeError(msg)
    for needed in ("default_mb", "max_mb"):
        if needed not in figures:
            msg = f"build_census: describe printed no {needed!r} row; the client did not answer"
            raise RuntimeError(msg)
    if not verbs:
        msg = "build_census: describe printed no verb rows; the client did not answer"
        raise RuntimeError(msg)
    return {
        "default_mb": figures["default_mb"],
        "max_mb": figures["max_mb"],
        "commands": sorted(verbs),
    }


def ledger_census(scripts: Path) -> LedgerFacts:
    """Return the ledger schemas, from the modules that OWN them."""
    times = cast("_LedgerModule", load_script(scripts, "buildtime"))
    profile = cast("_LedgerModule", load_script(scripts, "proofcost"))
    return {
        "times_ledger": times.LEDGER,
        "times_keep": times.KEEP,
        "times_cols": TIMES_COLS,
        "profile_ledger": profile.LEDGER,
        "profile_keep": profile.KEEP,
        "profile_cols": PROFILE_COLS,
    }


def gate_census(root: Path) -> GateFacts:
    """Return the declared gates in hook order, with the phase each falls in."""
    src = (root / HOOK_REL).read_text(encoding="utf-8")
    marks: list[tuple[int, str]] = []
    for needle, name in PHASE_ANCHORS:
        pos = src.find(needle)
        if pos < 0:
            msg = (
                f"build_census: phase anchor {needle!r} not found in .githooks/pre-commit — the "
                "hook was restructured. Update _PHASE_ANCHORS; do NOT collapse the phases, which "
                "are the load-bearing distinction here."
            )
            raise RuntimeError(msg)
        marks.append((pos, name))
    marks.sort()
    gates: list[tuple[str, str]] = []
    for found in RUN_RE.finditer(src):
        phase = PHASE_A
        for pos, name in marks:
            if pos < found.start():
                phase = name
        gates.append((str(found.group(1)), phase))
    if not gates:
        msg = (
            'build_census: no `run "..."` gate call sites found in .githooks/pre-commit — '
            "the hook was restructured. Update _RUN_RE; do NOT report zero gates."
        )
        raise RuntimeError(msg)
    return {"gates": gates, "count": len(gates), "phases": sorted({p for _, p in gates if p})}


def readers_census() -> list[tuple[str, str]]:
    """Return the tools that OWN a question about this surface, as `(path, question)`."""
    return list(READERS)
