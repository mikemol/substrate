# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Who adopts a directory's files BY SYMLINK — the census that must precede any delete.

⚑⚑⚑ BUILT BECAUSE A DELETE ONCE BROKE THIRTEEN REPOS. Other repos under `~/github` adopt
substrate's `scripts/` by symlink, under bare `python3`; deleting `hook_shellcheck.py` blocked
them all (memory `feedback_census_symlinks_before_deleting_scripts`). The rule was "run
`find -lname` first", and the answer came back as 51 KB of raw lines — a population nobody can
act on without grouping it by hand, which is the judgement this module does in a program.

⚑ GROUPED BY THE TARGET FILE, because the question a retirement asks is *who still reads THIS
file*: a file with no adopter can go now, and one with adopters names exactly who must move.

⚑ A LINK IS RESOLVED, NOT PATTERN-MATCHED. A relative link (`../../substrate/scripts/x.py`) and
an absolute one both count, because the test is where the link POINTS, not how it is spelled.
⚑ AN UNREADABLE DIRECTORY IS COUNTED AND SAID, never silently skipped — a census that cannot see
part of the tree reports a floor, and says it is one.

    python -m substrate.symlink_adopters <search-root> <target-dir> [<file> ...]
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

# The exit a refused invocation returns.
USAGE_EXIT = 2

USAGE = "usage: python -m substrate.symlink_adopters <search-root> <target-dir> [<file> ...]"

# Directories never walked: tool caches and environments, not adopters.
_SKIP = frozenset({".git", ".venv", "node_modules", "__pycache__", "_build", "build"})


@dataclass(slots=True)
class Census:
    """Every link into the target, keyed by target file, plus what the walk could not read."""

    by_target: dict[str, list[Path]] = field(default_factory=dict)
    unreadable: list[str] = field(default_factory=list)


def _repo_of(link: Path, root: Path) -> str:
    """Return the top-level directory under `root` that holds `link` — the adopting repo."""
    return link.relative_to(root).parts[0]


def census(root: Path, target: Path) -> Census:
    """Walk `root` for symlinks resolving into `target`, excluding `target`'s own tree."""
    target = target.resolve()
    out = Census()

    def refused(err: OSError) -> None:
        out.unreadable.append(str(err))

    for here, dirs, files in os.walk(root, onerror=refused):
        base = Path(here)
        if base.resolve().is_relative_to(target.parent):
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if d not in _SKIP]
        for name in files:
            link = base / name
            if not link.is_symlink():
                continue
            resolved = link.resolve()
            if resolved.is_relative_to(target):
                out.by_target.setdefault(resolved.name, []).append(link)
    return out


def render(found: Census, root: Path, only: list[str]) -> list[str]:
    """Render adopters per target file; with `only`, report exactly those files, zero included."""
    names = only or sorted(found.by_target)
    lines: list[str] = []
    for name in names:
        links = found.by_target.get(name, [])
        repos = sorted({_repo_of(link, root) for link in links})
        lines.append(f"{name}: {len(repos)} adopting repo(s) {' '.join(repos) or '-- none'}")
    lines.append(f"{len(names)} file(s); {len(found.unreadable)} unreadable dir(s)")
    lines.extend(f"  UNREADABLE {d} -- adopters there are unseen" for d in found.unreadable)
    return lines


def main(argv: list[str]) -> int:
    """Walk the search root and print adopters per target file."""
    minimum = 3
    if len(argv) < minimum:
        sys.stderr.write(USAGE + "\n")
        return USAGE_EXIT
    root, target = Path(argv[1]), Path(argv[2])
    for line in render(census(root, target), root, argv[3:]):
        sys.stdout.write(line + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
