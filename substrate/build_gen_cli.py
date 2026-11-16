# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The makefile generator's CLI, drained from `gen_build_makefiles.main` (⟡promote-path A, step 3).

⚑⚑⚑ THE DISPATCH, NOT THE DEPENDENCIES. Three things `main` reaches are bare-name `scripts/`
modules — `build_census` (the census modes), `edit_snapshot` (armed before a write) and
`_agdatext` (the comment stripper the graph needs). A `substrate/` module cannot import those
without `sys.path` surgery, so they arrive INJECTED as a `Hooks` value; the final shim in
`scripts/`, where bare imports resolve, supplies the real ones. That also makes every mode here
drivable with fakes.

⚑⚑ AN UNKNOWN FLAG IS REFUSED. The origin tested flag membership and fell through to REGENERATE,
so a typo (`--chek`) silently rewrote both makefiles. Here every flag must be known.

⚑ `--jobs` PRINTS ONLY THE NUMBER. Pre-commit reads it inside `$(… 2>/dev/null)` with a bare `-j`
fallback, so any extra stdout — or a crash — silently unthrottles the build. A bad `AGDA_JOBS`
goes to stderr with exit 2 and NOTHING on stdout, so the fallback is at least visible as empty.

⚑ `--check` COMPARES EXACT BYTES, as the origin did: a makefile that differs by one newline is
stale, because make reads the file, not a normalisation of it.

⚑⚑ `--selftest` WAS LOST IN THE DRAIN AND IS RESTORED (2026-09-25). The origin answered it; the
clean shim's unknown-flag refusal then turned it into exit 2, so `sync_precondition` read the
generator's own suite as RED and refused the census sync — a regression measured by the full
roster, not reasoned about. It now runs the suites of the modules the generator was drained into.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import (
    build_compat_selftest,
    build_settings,
    build_settings_selftest,
    flat_emit,
    flat_emit_selftest,
    root_emit,
    root_emit_selftest,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from substrate import agda_dag

#: Every flag this CLI accepts; anything else is refused rather than read as "regenerate".
FLAGS = frozenset(
    {"--jobs", "--check", "--sync-census", "--check-census", "--parameterized", "--selftest"}
)
USAGE = (
    "usage: gen_build_makefiles.py [--check | --jobs | --sync-census | --check-census"
    " | --selftest] [--parameterized]\n"
    "  bare: regenerate agda/Flat.mk and agda/Makefile\n"
    "  --parameterized: the tenant-aware renders\n"
    "  --selftest: the suites of the modules this generator was drained into\n"
)

#: The suites `--selftest` runs — one per module the generator's logic now lives in.
SUITES: tuple[Callable[[], bool], ...] = (
    build_settings_selftest.selftest,
    build_compat_selftest.selftest,
    flat_emit_selftest.selftest,
    root_emit_selftest.selftest,
)


@dataclass(frozen=True, slots=True)
class Hooks:
    """What the CLI needs from `scripts/`, injected so this module never imports it."""

    graph: Callable[[], agda_dag.Dag]
    snapshot: Callable[[Path], None]
    census: Callable[[bool], int]


def renders(hooks: Hooks, root: Path, *, parameterized: bool) -> dict[Path, str]:
    """Return `{target path: its rendered text}` for both makefiles under `root`.

    ⚑ `root` IS A PARAMETER OF THIS CALL, NOT READ OFF `build_settings.ROOT` (W35, operator
    2026-09-24). `build_settings.ROOT` itself stays as-is: it is the differential-tested bridge
    to the frozen `gen_build_makefiles` origin (`build_settings_selftest`), not the thing this
    item is about. Its CALLER here — the entry point, `main` below — is where the default lives.
    """
    settings = flat_emit.Settings(
        marker=build_settings.MARKER,
        shim_dir=str(build_settings.SHIM_DIR),
        membudget=str(build_settings.MEMBUDGET),
        mem_cap=build_settings.MEM_CAP,
        ver=build_settings.build_ver(),
        parameterized=parameterized,
    )
    agda_dir = root / "agda"
    return {
        agda_dir / "Flat.mk": flat_emit.text(hooks.graph(), settings),
        agda_dir / "Makefile": root_emit.text(parameterized=parameterized),
    }


def check(targets: dict[Path, str], root: Path) -> tuple[int, str]:
    """Return `(exit, report)` — 0 when every makefile on disk equals its render byte for byte."""
    problems = []
    for path, body in targets.items():
        rel = path.relative_to(root)
        if not path.exists():
            problems.append(f"  missing: {rel}")
        elif path.read_text(encoding="utf-8") != body:
            problems.append(f"  stale:   {rel}")
    if problems:
        lines = [
            "gen_build_makefiles --check: FAILED",
            *problems,
            "Run scripts/gen_build_makefiles.py to regenerate.",
        ]
        return 1, "\n".join(lines) + "\n"
    return 0, f"gen_build_makefiles --check: OK ({len(targets)} makefiles current)\n"


def regenerate(targets: dict[Path, str], snapshot: Callable[[Path], None]) -> str:
    """Write each makefile whose text changed, arming the snapshot before each write."""
    written = 0
    for path, body in targets.items():
        old = path.read_text(encoding="utf-8") if path.exists() else None
        if old != body:
            snapshot(path)
            path.write_text(body, encoding="utf-8")
            written += 1
    return f"gen_build_makefiles: wrote/updated {written} of {len(targets)} makefiles.\n"


def selftest() -> int:
    """Run every drained module's suite; 0 only when all pass (every suite runs regardless)."""
    results = [suite() for suite in SUITES]
    return 0 if all(results) else 1


def jobs() -> int:
    """Print only the `-j` width; a bad `AGDA_JOBS` goes to stderr with exit 2 and empty stdout."""
    try:
        sys.stdout.write(f"{build_settings.jobs()}\n")
    except build_settings.JobsError as exc:
        sys.stderr.write(f"gen_build_makefiles: {exc}\n")
        return 2
    return 0


def main(argv: list[str], hooks: Hooks, root: Path = build_settings.ROOT) -> int:
    """Dispatch one mode; refuse any flag this CLI does not know.

    ⚑ `root` DEFAULTS TO `build_settings.ROOT` HERE, AT THE ENTRY POINT (W35) — the one place a
    default belongs. `renders`/`check` take it as a required parameter rather than reading
    `build_settings.AGDA_DIR`/`.ROOT` as globals.
    """
    unknown = [a for a in argv if a not in FLAGS]
    if unknown:
        sys.stderr.write(f"gen_build_makefiles: unknown argument(s) {unknown}\n{USAGE}")
        return 2
    if "--selftest" in argv:
        return selftest()
    if "--jobs" in argv:
        return jobs()
    if "--sync-census" in argv or "--check-census" in argv:
        return hooks.census("--sync-census" in argv)
    targets = renders(hooks, root, parameterized="--parameterized" in argv)
    if "--check" in argv:
        code, report = check(targets, root)
        sys.stdout.write(report)
        return code
    sys.stdout.write(regenerate(targets, hooks.snapshot))
    return 0
