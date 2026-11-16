# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Resolve a bare sibling name to a file in ONE directory, for the length of one load.

⚑⚑⚑ REGISTERING A MODULE UNDER ITS OWN STEM IS NOT ENOUGH, AND THAT IS THE GAP THIS FILLS.
A loader that puts the module it is executing into `sys.modules` lets that module find
ITSELF mid-import — which is necessary and insufficient. It does nothing for a module
importing a DIFFERENT sibling by bare name, and a directory of scripts is full of exactly
that. Measured: a gate loaded by file location died with `ModuleNotFoundError` on
`import ratchet`, a sibling sitting beside it, so the gate read as UNMEASURABLE when it was
merely unreachable.

⚑⚑ A FINDER, NOT A PATH INSERT. `sys.path.insert` makes every later import in the process
resolve differently and outlives the call that made it. A meta-path finder scoped to one
directory answers only for names that have a file there, and is removed when the load
returns — so the resolution is an INPUT to that load rather than an ambient change to the
interpreter.

⚑ IT REFUSES DOTTED NAMES. A package import is somebody else's to resolve, and answering
for one would put this finder ahead of the real owner for every submodule in the process.

⚑ EXTRACTED FROM `scratch_module`, WHICH BUILT IT AND KEPT IT PRIVATE. That module's own
docstring says it is a sibling of the gate loader rather than a generalisation of it — true
of the LOADER, whose directory and roster are its own, and not of the finder, which was
already parameterised on a directory. One mechanism, two callers.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator


class SiblingFinder:
    """Resolve a bare name to `<directory>/<name>.py`, and nothing else."""

    def __init__(self, directory: str) -> None:
        """Bind the one directory this finder will answer for."""
        self._directory = Path(directory)

    def find_spec(
        self,
        name: str,
        path: object = None,
        target: object = None,
    ) -> importlib.machinery.ModuleSpec | None:
        """Return a spec when the directory holds a file for this bare name."""
        del path, target
        if "." in name:
            return None
        candidate = self._directory / f"{name}.py"
        if not candidate.exists():
            return None
        return importlib.util.spec_from_file_location(name, str(candidate))


@contextmanager
def siblings_of(directory: Path | str) -> Iterator[None]:
    """Make one directory's bare names importable for the duration of the block.

    ⚑ THE FINDER IS REMOVED WHETHER OR NOT THE BLOCK SUCCEEDS. A failed load that left the
    finder installed would leave the interpreter resolving bare names against a directory
    nobody asked about — an ambient effect indistinguishable from the path insert this
    exists to replace.
    """
    finder = SiblingFinder(str(directory))
    sys.meta_path.append(finder)
    try:
        yield
    finally:
        sys.meta_path.remove(finder)
