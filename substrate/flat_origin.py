# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Reach `scripts/gen_build_makefiles.py` for what it still owns — ONE loader, typed.

⚑⚑ WHY THIS IS A MODULE AND NOT A HELPER IN A SUITE. `flat_emit_selftest` (the byte-for-byte
differential), `build_settings_selftest` (the constants differential) and `flat_render` (the CLI
that writes a makefile for `make` to parse) all reach the origin. Separate private loaders would be
separate spellings of one reach, free to disagree about which module they loaded.

⚑⚑ THE ORIGIN IS LOADED BY PATH AND READ THROUGH A `Protocol`. It is not importable from
`substrate/` without `sys.path` surgery (operator: *"No sys.path modification."*), and a
dynamically loaded module is `Any`, so every read off it would type-check against nothing. The
Protocol names exactly the members read. Loading it runs the origin's own `sys.path.insert` (it
finds `_agdatext` that way); `sys.path` is restored after, so callers inherit no trace of it.

⚑ WHAT IT STILL SERVES SHRINKS AS THE DRAIN PROCEEDS. The SETTINGS now come from
`build_settings`, their one owner (t111); only the GRAPH (`parse_tree`) is still read from the
origin, until the compat wrappers land. This module retires with the origin.
"""

from __future__ import annotations

import importlib.util
import sys
from typing import TYPE_CHECKING, Protocol, cast

from substrate import agda_dag, build_settings, corpus, flat_emit

if TYPE_CHECKING:
    from types import ModuleType

ORIGIN = corpus.ROOT / "scripts" / "gen_build_makefiles.py"


class Origin(Protocol):
    """The members of `gen_build_makefiles` read here or by the differentials."""

    MARKER: str
    SHIM_DIR: str
    MEM_CAP: str
    AGDA_JOBS: str
    ROOT: str
    AGDA_DIR: str
    SRC: str

    def build_ver(self) -> str:
        """Return the agda interface version."""

    def jobs(self) -> int:
        """Return the make -j width."""

    def jobs_flag(self) -> list[str]:
        """Return the make -j argv fragment."""

    def parse_tree(self) -> tuple[dict[str, str], dict[str, set[str]]]:
        """Return the origin's `(disk, deps)` graph."""


def load() -> Origin:
    """Load the origin by path, restoring `sys.path` whatever its import does."""
    saved = list(sys.path)
    try:
        spec = importlib.util.spec_from_file_location("_gbm_origin", ORIGIN)
        if spec is None or spec.loader is None:
            msg = f"cannot load {ORIGIN}"
            raise ImportError(msg)
        module: ModuleType = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return cast("Origin", module)
    finally:
        sys.path[:] = saved


def settings(*, parameterized: bool = False) -> flat_emit.Settings:
    """Return the emitter settings — from `build_settings`, their one owner.

    ⚑ NO LONGER READ OFF THE ORIGIN (t111). `build_settings_selftest` proves each value equals
    the origin's; reading them here from the origin as well would be the second spelling that
    differential exists to retire.
    """
    return flat_emit.Settings(
        marker=build_settings.MARKER,
        shim_dir=str(build_settings.SHIM_DIR),
        membudget=str(build_settings.MEMBUDGET),
        mem_cap=build_settings.MEM_CAP,
        ver=build_settings.build_ver(),
        parameterized=parameterized,
    )


def graph(origin: Origin) -> agda_dag.Dag:
    """Return the origin's import graph as a `Dag`."""
    disk, deps = origin.parse_tree()
    return flat_emit.from_origin(disk, deps)


AGDATEXT = corpus.ROOT / "scripts" / "_agdatext.py"


class AgdaText(Protocol):
    """The member of `scripts/_agdatext` the graph needs: the comment stripper."""

    def strip(self, text: str, /) -> str:
        """Return `text` with Agda comments masked."""


def load_agdatext() -> AgdaText:
    """Load `scripts/_agdatext` by path (it inserts `scratch/` itself); restore `sys.path` after."""
    saved = list(sys.path)
    try:
        spec = importlib.util.spec_from_file_location("_agdatext_origin", AGDATEXT)
        if spec is None or spec.loader is None:
            msg = f"cannot load {AGDATEXT}"
            raise ImportError(msg)
        module: ModuleType = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return cast("AgdaText", module)
    finally:
        sys.path[:] = saved


def model_graph() -> agda_dag.Dag:
    """Return the graph from the clean MODEL (`agda_dag.parse`) with the origin's stripper.

    ⚑ THIS IS THE GRAPH THE SHIM WILL SERVE, so it must equal `graph(load())` before it replaces
    it — `graph_parity_selftest` holds the two equal, module by module and edge by edge.
    """
    return agda_dag.parse(strip=load_agdatext().strip)
