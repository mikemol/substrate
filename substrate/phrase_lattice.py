# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The memory apparatus's phrase clusterer, loaded BY PATH and read through a Protocol.

`grammar_phrase_lattice.py` lives in the Claude-managed memory directory, not in this tree, and it
imports its vendored Sequitur as the bare module `_vendor_sequitur` — resolvable only by directory
adjacency. The tmi probes reached it with two `sys.path.insert`s, which this tree refuses. Here the
sibling is registered in `sys.modules` under the name the lattice expects, then the lattice is
loaded from its file: no path mutation, and nothing leaks into unrelated imports.

⚑ READ THROUGH A PROTOCOL because a module loaded by path is `Any`; a misspelled attribute would
type-check against nothing, and the probes' counts rest on these two calls.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, cast

if TYPE_CHECKING:
    from collections.abc import Sequence
    from types import ModuleType

MEMORY = Path.home() / ".claude" / "projects" / "-home-mikemol-github-substrate" / "memory"
_SEQUITUR = "_vendor_sequitur"


class Lattice(Protocol):
    """The two calls the tmi probes make."""

    def words(self, text: str, /) -> list[str]:
        """Tokenise prose the way the clusterer does."""
        ...

    def cluster_phrases(
        self,
        items: Sequence[tuple[str, list[str]]],
        phrase_min: int = 3,
        min_members: int = 2,
        tau: float = 0.5,
    ) -> list[tuple[str, frozenset[str]]]:
        """Cluster named token lists by shared grammar phrases, largest first."""
        ...


class LoadError(RuntimeError):
    """The lattice or its vendored Sequitur could not be loaded from the memory directory."""


def _load(name: str, path: Path) -> ModuleType:
    """Load one module from `path` and register it under `name`."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        msg = f"cannot load {name} from {path}"
        raise LoadError(msg)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load(memory: Path) -> Lattice:
    """Return the phrase lattice, registering its vendored Sequitur first.

    ⚑ `memory` IS REQUIRED, NOT DEFAULTED (operator 2026-09-24: "We should not have things
    [like] corpus.ROOT" — a module-level path constant). The memory directory is a parameter
    of the caller, not a property of this module; the caller (tmi_probes' CLI) now takes it
    explicitly rather than this module guessing a fixed location.
    """
    if _SEQUITUR not in sys.modules:
        _load(_SEQUITUR, memory / f"{_SEQUITUR}.py")
    return cast("Lattice", _load("grammar_phrase_lattice", memory / "grammar_phrase_lattice.py"))
