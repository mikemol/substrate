# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Split a bare name into the kind of problem it is: an INSTALL or a DRAIN.

⚑⚑⚑ THE RANKING MIXES TWO POPULATIONS WITH DIFFERENT FIXES. `drain_leverage` ranks every
name reached under a `sys.path` insert, and some of them are third-party distributions a
file path-hacks its way to. No drain retires those: installing them does, and the insert
then goes away because the import resolves normally. Reading them as drain candidates puts
a dependency-declaration chore into a queue about module ownership.

⚑⚑ THE FIRST DISCRIMINATOR IS RESOLVABILITY ON A CLEAN PATH, NOT A NAME LIST. A hand-kept
roster of "third-party names" would go stale the first time a dependency landed or left,
and worse, it would encode the guess rather than the fact. `importlib.util.find_spec` run
WITHOUT the repo's own directories answers it directly: a name that resolves is installed
and its insert is redundant.

⚑⚑⚑ BUT RESOLVABILITY ALONE MISFILES EVERY ABSENT DEPENDENCY, AND THAT WAS MEASURED. The
first cut of this reader reported `matplotlib`, `bpy`, `bmesh` and `mathutils` as DRAIN —
they are third-party (Blender's, in three of those cases) and simply not installed in this
environment, which is indistinguishable from an own-tree module by a probe alone. So the
manifest is consulted SECOND: a name the project DECLARES is an install problem whether or
not it is installed here, because the fix is the same either way. Declaration is a fact
about intent; resolution is a fact about this machine, and the two disagree exactly where
it matters.

⚑ THE ORDER IS DECLARED-THEN-PROBED, and it must stay that way. Probing first would let a
declared dependency that happens to be absent fall through to DRAIN before the manifest is
ever read — the misfiling this second discriminator exists to prevent.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from typing import TYPE_CHECKING

from substrate import dep_addressing

if TYPE_CHECKING:
    from pathlib import Path

# The kinds a bare name can be.
INSTALL = "install"
DRAIN = "drain"
STDLIB = "stdlib"

# Directories whose presence on the path would make an own-tree module look installed.
REPO_DIRS = ("scratch", "scripts", "jea", "catalog", "substrate")

# A requirement string opens with the distribution name; everything from the first
# version specifier, extra, marker or URL onward is not part of it.
_DIST = re.compile(r"^\s*([A-Za-z0-9._-]+)")

# Distributions whose IMPORT name differs from their DISTRIBUTION name. ⚑ A MAP, NOT A
# GUESS: `pip install psycopg-binary` imports as `psycopg`, and no rule derives that. Kept
# minimal and only for names this corpus actually reaches.
_IMPORT_NAME = {
    "psycopg-binary": "psycopg",
    "psycopg2-binary": "psycopg2",
    "pyyaml": "yaml",
    "pillow": "PIL",
}


def declared_imports(manifest_root: Path) -> frozenset[str]:
    """Return the import names this project's manifest declares as dependencies.

    ⚑ THE DISTRIBUTION NAME IS NORMALISED THE WAY PACKAGING NORMALISES IT — case-folded
    with runs of `.`/`-`/`_` collapsed — because `Foo.Bar` and `foo-bar` name one project.
    A comparison on the raw string would miss a declared dependency over punctuation.
    """
    out: set[str] = set()
    for requirement in dep_addressing.declared(manifest_root / "pyproject.toml"):
        match = _DIST.match(requirement)
        if match is None:
            continue
        dist = re.sub(r"[-_.]+", "-", match.group(1)).lower()
        out.add(_IMPORT_NAME.get(dist, dist.replace("-", "_")))
    return frozenset(out)


def clean_path(root: Path) -> list[str]:
    """Return `sys.path` with this repo's own directories removed.

    ⚑ THE REPO ROOT ITSELF IS DROPPED TOO. A tool run from the repo root carries `''` or
    the root on `sys.path`, which makes every top-level module importable — so a reader
    that dropped only the subdirectories would report the entire drain population as
    INSTALL. That is the false green this exists to avoid.
    """
    drop = {str(root), str(root.resolve()), "", "."}
    drop.update(str(root / d) for d in REPO_DIRS)
    return [p for p in sys.path if p not in drop]


def kind_of(name: str, root: Path, declared: frozenset[str] | None = None) -> str:
    """Return the kind of problem `name` is: INSTALL, DRAIN or STDLIB.

    ⚑ STDLIB IS SEPARATED FIRST because it is neither problem. A bare `import json` needs
    no insert and no drain, and counting it either way would put a name nobody can act on
    into a queue of actions.

    ⚑⚑ AND A NAME THAT NEITHER RESOLVES NOR IS DECLARED STILL READS AS DRAIN. An
    undeclared, uninstalled third-party import is indistinguishable from an own-tree module
    by any static test — but it is also a defect either way, so over-reporting the drain
    queue is the safe direction: a name wrongly queued is discovered the moment someone
    looks for its file, while one wrongly filed INSTALL is never looked at again.
    """
    if name in sys.stdlib_module_names:
        return STDLIB
    known = declared_imports(root) if declared is None else declared
    if name in known:
        return INSTALL
    saved = sys.path[:]
    try:
        sys.path[:] = clean_path(root)
        try:
            found = importlib.util.find_spec(name)
        except (ImportError, ValueError):
            return DRAIN
    finally:
        sys.path[:] = saved
    return INSTALL if found is not None else DRAIN


def partition(names: list[str], root: Path) -> dict[str, list[str]]:
    """Group names by kind, so a caller reports two queues rather than one ranking."""
    known = declared_imports(root)
    out: dict[str, list[str]] = {INSTALL: [], DRAIN: [], STDLIB: []}
    for name in sorted(set(names)):
        out[kind_of(name, root, known)].append(name)
    return out
