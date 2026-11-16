# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Fixture files for the `sys.path` census cases — written into a temp tree, not the repo.

⚑⚑ THE CENSUS READS PATHS FROM DISK, so its cases need real files. Pointing them at REPO
files instead would make every case a measurement of the tree: green or red for reasons that
have nothing to do with the grouping logic, and red the next time anyone edits an unrelated
tool. The fixture states the exact shapes the grouping must distinguish.

⚑ THE FIXTURE LIVES UNDER `corpus.ROOT` BECAUSE `census` REPORTS REPO-RELATIVE PATHS. A tree
elsewhere would make `relative_to` raise, so the files are written into a directory inside the
repo and removed when the cases finish — a fixture left on disk would be counted by the very
census it exists to test.
"""

from __future__ import annotations

import shutil

from substrate import corpus

# ⚑ THE SHAPES THE GROUPING MUST TELL APART, one per file:
#   two files naming ONE directory   -> one target, two owners  (one decision)
#   one file naming TWO directories  -> two targets, one owner  (two decisions)
#   a computed argument              -> the unresolved bucket   (needs reading)
_FILES = {
    "shared_a.py": 'import sys\nsys.path.insert(0, "shared")\n',
    "shared_b.py": 'import sys\nsys.path.insert(0, "shared")\n',
    "two_dirs.py": ('import sys\nsys.path.insert(0, "alpha")\nsys.path.insert(0, "beta")\n'),
    "computed.py": "import sys\nsys.path.insert(0, where())\n",
    "broken.py": "def (\n",
}

_DIR = "_syspath_fixture"

#: The deliberately unparseable member, named so a case can target it alone.
BROKEN = f"{_DIR}/broken.py"


def write() -> list[str]:
    """Write the fixture tree and return its repo-relative paths."""
    base = corpus.ROOT / _DIR
    base.mkdir(exist_ok=True)
    for name, text in _FILES.items():
        (base / name).write_text(text, encoding="utf-8")
    return [f"{_DIR}/{name}" for name in sorted(_FILES)]


def remove() -> None:
    """Delete the fixture tree.

    ⚑ A FIXTURE LEFT ON DISK WOULD BE COUNTED BY THE CENSUS IT TESTS, and it sits directly
    under the repo root where nothing skips it.
    """
    shutil.rmtree(corpus.ROOT / _DIR, ignore_errors=True)


def paths() -> list[str]:
    """Return the fixture paths, writing the tree if it is not present.

    ⚑ IDEMPOTENT, so a case may call it without knowing whether an earlier one did. The
    alternative — a module-level write at import — would put files on disk merely because
    something imported this.
    """
    return write()
