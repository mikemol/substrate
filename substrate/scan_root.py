# SPDX-License-Identifier: Apache-2.0
# Copyright substrate contributors
"""Resolve a census operand to the files it names, and refuse what it cannot resolve.

⚑⚑⚑ A FILE OPERAND USED TO BECOME THE WHOLE TREE, SILENTLY. `codepoints.py` resolved its root
with `next(a for a in args if not a.startswith("-") and os.path.isdir(a), ".")`, so a caller
naming a FILE failed the `isdir` test, was skipped, and the root fell back to `.`. The census then
answered about 14,402 files while the caller believed it had narrowed to one.

⚑⚑ AND THE FAILURE DIRECTION IS WHY IT SURVIVED. A narrowing that does not narrow returns MORE
rows, never fewer, so it reads as a rich answer rather than an error. Measured by a peer who
passed their own `CLAUDE.md`, read a whole-tree population as a fact about that one file, and
reported that reading onward — then by this repo, whose own scoped measurement turned out to have
been scoped by LUCK, because the operand it happened to pass was a directory.

⚑ THAT IS `census-green-is-a-fact-about-the-census` WITH THE SIGN FLIPPED. A false ZERO invites
doubt. A false POSITIVE population does not, because a caller checking their work sees rows and
stops. So the discriminator has to be structural rather than a caller's vigilance.

⚑ THE THIRD OUTCOME IS THE POINT. A path-shaped operand naming nothing is a typo, and a typo that
silently censuses the tree is the same defect wearing a different cause. `resolve` returns a
`Refusal` for it rather than a root, so a caller cannot fail to notice.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

SKIP_DIRS = frozenset({".git", "__pycache__", ".venv", "node_modules", "_build", ".mypy_cache"})


@dataclass(frozen=True)
class Refusal:
    """Name an operand that cannot be resolved, and what the caller should do instead."""

    message: str


@dataclass(frozen=True)
class Scan:
    """Carry a resolved operand: the root as given, and whether it names one file or a tree.

    ⚑ `is_file` is carried rather than re-derived at each use. A caller that re-tests the path is
    asking the filesystem a question this already answered, and the two can disagree if the tree
    moves underneath — the straddled-measurement shape this repo already records.
    """

    root: str
    is_file: bool


def looks_like_path(arg: str) -> bool:
    """Report whether this operand is path-shaped, i.e. meant by the caller as a location.

    ⚑ SEPARATOR OR EXISTENCE, not existence alone. `foo/bar` that does not exist is a typo the
    caller wants refused. A bare word that does not exist may be a mode operand for some other
    flag, and refusing it would break every caller passing a non-path argument.
    """
    return os.sep in arg or Path(arg).exists()


def resolve(args: list[str], default: str = ".") -> Scan | Refusal:
    """Return the first path-shaped operand as a `Scan`, or a `Refusal` naming what went wrong.

    ⚑ FLAGS ARE EXCLUDED BY PREFIX, never by a roster. A roster here would be a second copy of the
    caller's own flag list — the two-rosters defect this tree has measured repeatedly — and the
    caller already knows its flags. What this owns is the PATH question alone.
    """
    named = [a for a in args if not a.startswith("-") and looks_like_path(a)]
    if not named:
        return Scan(root=default, is_file=False)

    first = named[0]
    if not Path(first).exists():
        return Refusal(
            f"no such path {first!r} — refusing rather than censusing the tree,\n"
            f"  which is what a silently-discarded operand used to do."
        )
    return Scan(root=first, is_file=Path(first).is_file())


def files(scan: Scan, skip_suffix: frozenset[str] = frozenset()) -> list[str]:
    """List every file the scan names: one for a file root, the walked tree for a directory.

    ⚑ A FILE ROOT YIELDS ITSELF, which `os.walk` does not do. Walking a file path yields NOTHING,
    so a reader that only walks reports an empty census for a file the caller named — the same
    wrong answer as the widening, arriving from the opposite side.

    ⚑ AND THE SUFFIX FILTER IS NOT APPLIED TO AN EXPLICITLY NAMED FILE, because a caller naming a
    path has already made the selection the filter exists to make.
    """
    if scan.is_file:
        return [scan.root]

    out: list[str] = []
    for dirpath, dirnames, filenames in os.walk(scan.root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        out.extend(
            str(Path(dirpath) / fn) for fn in filenames if Path(fn).suffix not in skip_suffix
        )
    return out
