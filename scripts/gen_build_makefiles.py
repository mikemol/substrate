#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""gen_build_makefiles.py — the SHIM over the drained makefile generator (⟡promote-path A).

⚑⚑⚑ THE 900-LINE ORIGIN IS DRAINED. It carried 292 findings and the per-file gate refused every
edit, so each concern moved into a clean `substrate/` module, each held byte-for-byte (or value-
for-value) against this file before the swap:

    settings, jobs, build_ver, shim block     substrate/build_settings     17/17 vs origin
    import graph, parse_tree, kahn_*, IMPRE    substrate/agda_dag, build_compat   4/4, 8/8
    agda/Flat.mk                              substrate/flat_emit          10/10 byte-for-byte
    agda/Makefile                             substrate/root_emit          8/8 byte-for-byte
    the CLI                                   substrate/build_gen_cli      8/8

This file keeps the NAME and the CLI every consumer uses — pre-commit (`--check`, `--check-census`,
`--jobs`), `agda/Makefile`'s check-makefiles, `scripts/build_census` and three scratch tools (bare
import), `scratch/paydown` (loaded by path) — and re-exports the names `stubs/
gen_build_makefiles.pyi` declares. New work goes in the modules, never here.

⚑⚑ IT RUNS ON THE PROJECT VENV, AND DOES NOT TOUCH `sys.path` (operator, 2026-09-23). The system
python3 cannot import `substrate` from a script path; its callers were moved to `.venv/bin/python`
instead of this file editing the interpreter's search state.

⚑ THREE `scripts/`/`scratch/` MODULES ARE LOADED BY PATH, READ THROUGH A PROTOCOL: `_agdatext` (the
comment stripper), `build_census` (the census modes) and `edit_snapshot` (armed before a write).
They are bare-name modules; importing them by name would need the `sys.path` edit ruled out above.
"""

from __future__ import annotations

import importlib.util
import sys
from typing import TYPE_CHECKING, Protocol, cast

from substrate import agda_dag, build_compat, build_gen_cli, build_settings, flat_emit, root_emit

if TYPE_CHECKING:
    from pathlib import Path
    from types import ModuleType

ROOT = str(build_settings.ROOT)
AGDA_DIR = str(build_settings.AGDA_DIR)
SRC = str(build_settings.SRC)
MARKER = build_settings.MARKER
SHIM_DIR = str(build_settings.SHIM_DIR)
MEM_CAP = build_settings.MEM_CAP
AGDA_JOBS = build_settings.AGDA_JOBS
IMPRE = build_compat.IMPRE

# ⚑ `scratch/agda_defs.cmdline_flags` READS THIS FILE'S SOURCE for a string constant starting with
# the flag assignment below; without one it silently returns []. Kept so that reader stays
# correct; its authority is the literal `flat_emit` emits into Flat.mk.
_AGDA_FLAGS_LINE = "AGDA_FLAGS ?= --safe --without-K"

_SCRIPTS = build_settings.ROOT / "scripts"
_SCRATCH = build_settings.ROOT / "scratch"


class _AgdaText(Protocol):
    def strip(self, text: str, /) -> str: ...


class _Census(Protocol):
    BlockError: type[Exception]

    def cmd_sync(self) -> int: ...

    def cmd_check(self) -> int: ...


class _Snapshot(Protocol):
    def guard(self, name: str, paths: list[str], *, intent: str) -> object: ...


def _load(name: str, path: Path) -> ModuleType:
    """Load a bare-name module by path, restoring `sys.path` whatever its import does."""
    saved = list(sys.path)
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            msg = f"cannot load {path}"
            raise ImportError(msg)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path[:] = saved


def _strip() -> agda_dag.Stripper:
    """Return the one Agda comment stripper (`scripts/_agdatext.strip`)."""
    return cast("_AgdaText", _load("_agdatext", _SCRIPTS / "_agdatext.py")).strip


def build_ver() -> str:
    """Return the agda interface version (`build_settings.build_ver`)."""
    return build_settings.build_ver()


def parse_tree() -> tuple[dict[str, str], dict[str, set[str]]]:
    """Return `(disk, deps)` in the origin's shape, from the model."""
    return build_compat.parse_tree(_strip())


def kahn_depth(disk: dict[str, str], deps: dict[str, set[str]]) -> tuple[int, list[str]]:
    """Return `(critical_path_depth, order)`; a cycle exits 2, as the origin did."""
    return build_compat.kahn_depth(disk, deps)


def kahn_check(disk: dict[str, str], deps: dict[str, set[str]]) -> None:
    """Refuse a cyclic graph (exit 2)."""
    build_compat.kahn_check(disk, deps)


def flat_text(disk: dict[str, str], deps: dict[str, set[str]]) -> str:
    """Render `agda/Flat.mk` (faithful mode) for the given graph."""
    settings = flat_emit.Settings(
        marker=MARKER,
        shim_dir=build_settings.SHIM_DIR_MAKE,
        membudget=build_settings.MEMBUDGET_MAKE,
        mem_cap=MEM_CAP,
        ver=build_ver(),
    )
    return flat_emit.text(flat_emit.from_origin(disk, deps), settings)


def root_text() -> str:
    """Render `agda/Makefile` (faithful mode)."""
    return root_emit.text()


def jobs() -> int:
    """Return the `make -j` width (`build_settings.jobs`)."""
    return build_settings.jobs()


def jobs_flag() -> list[str]:
    """Return `["-j", "<n>"]` (`build_settings.jobs_flag`)."""
    return build_settings.jobs_flag()


def _census(sync: bool) -> int:  # noqa: FBT001 - the injected hook's signature
    """Run the census sync or check; a missing marker pair exits 1, as the origin did."""
    census = cast("_Census", _load("build_census", _SCRIPTS / "build_census.py"))
    try:
        return census.cmd_sync() if sync else census.cmd_check()
    except census.BlockError as exc:
        sys.stderr.write(f"gen_build_makefiles: {exc}\n")
        return 1


def _snapshot(path: Path) -> None:
    """Arm edit_snapshot before rewriting a makefile; a missing snapshot tool only warns."""
    try:
        snap = cast("_Snapshot", _load("edit_snapshot", _SCRATCH / "edit_snapshot.py"))
        snap.guard("gen_build_makefiles", [str(path)], intent="apply")
    except (ImportError, OSError) as exc:
        sys.stderr.write(f"   snapshot unavailable ({exc}) — recover via git if needed\n")


def main() -> int:
    """Dispatch the CLI (`substrate.build_gen_cli`), supplying the scripts/ hooks."""
    hooks = build_gen_cli.Hooks(
        graph=lambda: agda_dag.parse(strip=_strip()), snapshot=_snapshot, census=_census
    )
    return build_gen_cli.main(sys.argv[1:], hooks)


if __name__ == "__main__":
    sys.exit(main())
