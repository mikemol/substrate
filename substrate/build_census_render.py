# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Render the two census blocks: the GATED structural one and the UNGATED measured one.

⚑⚑⚑ DRAINED FROM `scripts/build_census.py` (W329); the facts live in `build_census_facts`.
The origin's reason for two blocks is not cosmetic and is kept here:

  * `build-census`       STRUCTURAL. Caps, flags, module and edge counts, DAG depth, ledger
                         schemas, the gate roster. A pure function of the TREE, identical on
                         every machine, so `--check` can GATE it in pre-commit.
  * `build-observations` MEASURED. Build times, peaks, over-cap counts, read from
                         `.agda-times.tsv`, which is GITIGNORED and hardware-specific. Rendered
                         with the ledger's mtime beside each figure, and NEVER gated.

Gating the measured half would fail on every machine and after every build. A gate that cries
wolf gets disabled, and it would take the structural gate down with it.

⚑ THE CENSUS IS A RENDERING, NOT A SECOND ANALYSIS. Every figure comes from the tool that already
owns the artifact; a census that re-derived any of them would be a second authority to drift
against the first.

⚑ THE TREE IS A PARAMETER: `root` is the repo, `scripts` its `scripts/` directory.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, cast

from substrate import build_census_facts as facts
from substrate import build_settings

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

#: The unit-less width of a figure's name column, from the origin's `%-58s`.
_NAME_WIDTH = 58


def exists(root: Path, rel: str) -> bool:
    """Report whether `rel` exists under the repo root."""
    return (root / rel).exists()


def mtime(path: Path) -> str:
    """Return the file's mtime as `YYYY-MM-DD HH:MM`, or `absent` when it cannot be stat'd."""
    try:
        stamp = path.stat().st_mtime
    except OSError:
        return "absent"
    local = datetime.datetime.fromtimestamp(stamp, tz=datetime.UTC).astimezone()
    return local.strftime("%Y-%m-%d %H:%M")


def _dag_lines(dag: facts.DagFacts) -> list[str]:
    """Return the DAG section."""
    counts = f"{dag['modules']} modules · {dag['edges']} source-parsed import edges"
    ends = f"{dag['roots']} roots (no in-tree import)"
    target = f"_build/{dag['build_ver']}/agda/<Mod>.agdai"
    out = [
        "── THE FLAT IMPORT DAG (⟡make-import-dag)",
        f"   {counts} · DAG depth {dag['depth']}",
        f"   {ends} · {dag['leaves']} leaves (nothing imports them)",
        f"   ONE flat makefile. Targets are REAL FILES ({target}), each",
        "   depending on its own .agda AND every direct import's .agdai. There are NO",
        "   per-directory makefiles — 280 of them were deleted because directory order",
        "   encoded only 0.4% of the real import edges.",
        "",
        "   ⚑ DAG DEPTH IS THE HONEST PARALLEL FLOOR. `buildtime.py --predict` divides by a",
        "     HARDCODED J=6, which is unrelated to the RAM-derived concurrency `make -j`",
        f"     actually achieves. No schedule can beat the critical path: {dag['depth']}.",
        "",
        "   most-imported:",
    ]
    out.extend(f"     {name:<{_NAME_WIDTH}} {count:4d} importers" for name, count in dag["top_in"])
    out.append("")
    return out


def _memory_lines(dag: facts.DagFacts, mb: facts.MembudgetFacts) -> list[str]:
    """Return the memory-discipline section."""
    cap = f"{dag['mem_cap']:<6}"
    default = f"{mb['default_mb']:<6d}"
    ceiling = f"{mb['max_mb']:<4d}"
    return [
        "── THE MEMORY DISCIPLINE — ⚑ TWO CAPS, TWO KINDS, INVERTED ASYMMETRY",
        f"   MEM_CAP  = {cap}  a GHC HEAP GATE, per module (+RTS -M). Exceeding it is a",
        "                     BUILD FAILURE (exit 251) — the forcing function that makes a",
        "                     module shard or seal `opaque`. WRONG-LARGE silently admits debt.",
        f"   AGDA_MB  = {default}  a cgroup LEASE default (maxRSS: heap + RTS + everything else).",
        "                     It AUTOSIZES from recorded peaks and RETRIES on OOM-kill",
        "                     (137/143), doubling until it fits. WRONG-SMALL costs one retry",
        "                     and self-corrects.",
        f"   AGDA_MB_MAX = {ceiling} the top of that SEARCH, not a bound the lease must respect.",
        "",
        "   ⚑ SO READING THE LEASE AS A CEILING GETS IT BACKWARDS. For the heap gate a",
        "     too-large value hides debt; for the lease a too-small one self-heals. This is",
        "     the single most-confused pair on this surface.",
        "",
        "   membudget subcommands: " + " ".join(mb["commands"]),
        "",
    ]


def _ledger_lines(led: facts.LedgerFacts) -> list[str]:
    """Return the ledgers section."""
    times_ledger = f"{led['times_ledger']:<20}"
    times_cols = " ⇥ ".join(led["times_cols"])
    profile_ledger = f"{led['profile_ledger']:<20}"
    profile_cols = " ⇥ ".join(led["profile_cols"])
    return [
        "── THE LEDGERS — three, with three owners",
        f"   {times_ledger} {times_cols}   (last {led['times_keep']}/module)",
        "        written by membudget, read by buildtime.py — ⚑ where AGDA peaks live",
        f"   {profile_ledger} {profile_cols}",
        "        written+read by proofcost.py — ⚑ its peak_mb is deliberately 0;",
        "        membudget is the single maxRSS authority",
        "   labels.tsv           label ⇥ wall_s ⇥ peak_mb ⇥ epoch ⇥ user_s ⇥ sys_s",
        "        `membudget peaks` reads ONLY this — selftest/gate/item labels, ZERO Agda",
        "        modules. Asking it about a module returns nothing, and that is a fact",
        "        about the ledger, not the module.",
        "",
    ]


def _gate_lines(gates: facts.GateFacts) -> list[str]:
    """Return the gate-pipeline section, one heading per phase."""
    out = [
        f"── THE GATE PIPELINE — {gates['count']} DECLARED gates",
        "   ⚑ DECLARED, from the hook's own `run` call sites. `gate_ledger.py --report`",
        "     ranks only what it has OBSERVED and reads as complete — a different number.",
    ]
    seen = ""
    for name, phase in gates["gates"]:
        if phase != seen:
            out.append(f"   {phase or '(before any phase marker)'}")
            seen = phase
        out.append(f"     · {name}")
    out.extend(
        [
            "",
            "   ⚑ THE PHASE IS LOAD-BEARING. Phase C gates read what the build PRODUCED, so they",
            "     must run after it — an earlier order let the Set₁ ratchet FALSE-PASS on stale",
            "     cores. Naming a gate without its phase is half an answer.",
            "   ⚑ PHASE B HOLDS NO `run` GATE. The full build is a bare `make -C agda -j`, so it",
            "     is the boundary the gates are partitioned BY, not a phase containing any.",
            "     Its failure blocks Phase C by the same `fail`-guard the others use.",
            "",
        ]
    )
    return out


def render_block(root: Path, scripts: Path) -> str:
    """Return the gated census, a pure function of the tree, identical on every machine."""
    dag = facts.dag_census(scripts)
    mb = facts.membudget_census(build_settings.MEMBUDGET)
    led = facts.ledger_census(scripts)
    gates = facts.gate_census(root)
    readers = facts.readers_census()
    sync = "`python3 scripts/gen_build_makefiles.py --sync-census`"
    out = [
        f"⚑ **GENERATED — DO NOT EDIT BY HAND.** {sync}",
        "rewrites everything between the markers; a hand edit is overwritten on the next",
        "sync, and `--check-census` is a pre-commit gate that refuses drift. Every figure is",
        "DERIVED from the tool that owns it — the DAG from `gen_build_makefiles.parse_tree`,",
        "the lease defaults PARSED from `scripts/membudget`, the ledger schemas from",
        "`buildtime`/`proofcost`, the gate roster from the pre-commit hook's own call sites.",
        "",
        "⚑ **STRUCTURAL ONLY — the measured figures live in the UNGATED block below.**",
        "Build times and peaks come from `.agda-times.tsv`, which is gitignored and",
        "hardware-specific; gating them would fail on every machine and after every build.",
        "",
        "```",
    ]
    out.extend(_dag_lines(dag))
    out.extend(_memory_lines(dag, mb))
    out.extend(_ledger_lines(led))
    out.extend(_gate_lines(gates))
    out.append("── WHO OWNS WHICH QUESTION")
    for rel, what in readers:
        mark = "" if exists(root, rel) else "   ⚑ ABSENT"
        out.append(f"   {rel:<34} {what}{mark}")
    out.append("```")
    return "\n".join(out)


_COST_NOTES = [
    "   scripts/buildtime.py --predict   full-build estimate (Σ medians; wall ≈ Σ/J)",
    "   scripts/buildtime.py --top       the hot spots",
    "   scripts/buildtime.py --mem       the heaviest peaks",
    "",
    "   ⚑ THE ESTIMATE DRIFTS LOW, IN A KNOWN DIRECTION. It is a MEDIAN of the last",
    "     K runs, and cold elaborations mix with warm no-ops at ~50x separation. Because",
    "     Flat.mk targets are real files, an unchanged module is never re-invoked and",
    "     appends no row — so warm rows accumulate and the forecast decays over time.",
    "     The distribution is heavy-tailed, so a handful of modules own the number.",
    "",
    "── THE CAP RATCHET",
    "   scripts/check_cap_ratchet.py --quiet    the over-cap census (DEBT; paydown-only)",
    "   scripts/cap_diagnose.py <mod>           elaboration-bound or load-bound?",
    "   ⚑ Its statistic is the LATEST row, not median or max — both of the others are",
    "     wrong here, and the docstring records why with measured windows.",
    "",
    "── PROOF COST",
    "   scripts/proofcost.py --top / --module <rel> / --oracle / --reprofilable",
    "   ⚑ Cost lives in ELABORATION and ALLOCATION CHURN, almost never residency: a",
    "     measured module allocated ~31.7 GB inside a 12 MB peak. Time and memory are",
    "     near-independent axes — which is WHY the heap gate and the lease are",
    "     different kinds rather than two spellings of one budget.",
    "   ⚑ `--top` may show alloc_MB 0.0 for rows predating the `+RTS -s` capture; that",
    "     is a legacy artifact, not a measurement. `--module` shows the real figure.",
    "   ⚑ `--oracle` ranks over ALL profiled modules including the ones",
    "     `--reprofilable` warns are not clean; the filter is not composable onto it.",
    "",
]

_OUTCOME_NOTES = [
    "   scripts/gate_ledger.py --order / --report",
    "   ⚑ OBSERVED, NOT DECLARED. It ranks only gates it has recorded rows for, and",
    "     prints no recency — so a stale ledger reads as a current ranking. The DECLARED",
    "     population is in the gated block above.",
    "```",
]


def _stats_line(scripts: Path) -> str:
    """Return the buildtime summary line, or the pointer to run it when it has none.

    ⚑ THE ORIGIN'S `except Exception` ALSO COVERED A MISSING `stats`. `buildtime` defines no such
    reader today, so the fallback is what renders; it is kept as an explicit branch rather than
    an attribute miss swallowed by a broad handler.
    """
    buildtime = facts.load_script(scripts, "buildtime")
    stats: object = cast("object", getattr(buildtime, "stats", None))
    if callable(stats):
        reader = cast("Callable[[], object]", stats)
        try:
            return f"   {reader()}"
        except (OSError, ValueError, TypeError, KeyError, AttributeError, ZeroDivisionError):
            pass
    return "   scripts/buildtime.py --stats     (run it; no summary available here)"


def render_observations(root: Path, scripts: Path) -> str:
    """Return the UNGATED measured block.

    Every figure carries its producing command; volatile figures carry the mtime of the ledger
    they came from.

    ⚑ WITHOUT THE STAMP THESE READ AS CURRENT WHILE QUOTING A DEAD WINDOW, which is exactly the
    state `gate_ledger.py --report` is in: 38 rows from one 5-hour window, rendered as a ranking
    with no recency anywhere in the output.
    """
    out = [
        "⚑ **DERIVED, NOT TYPED — AND NOT GATED.** Every figure came from the command beside",
        "it. These read `.agda-times.tsv`, which is **gitignored and hardware-specific**, so",
        "they are NOT drift-gated: on your machine they will differ, and that is correct.",
        "**Re-run before asserting any of them.** Refresh with",
        "`python3 scripts/gen_build_makefiles.py --sync-census`.",
        "",
        "```",
        f"── COST (ledger last written {mtime(root / 'agda' / '.agda-times.tsv')})",
        _stats_line(scripts),
    ]
    out.extend(_COST_NOTES)
    out.append(f"── GATE OUTCOMES (ledger last written {mtime(scripts / '.gate-outcomes.tsv')})")
    out.extend(_OUTCOME_NOTES)
    return "\n".join(out)
