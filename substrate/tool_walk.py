# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""Enumerate this repo's own Python tools — the population a tooling census measures.

⚑⚑⚑ THE SECOND UNIT OF THE `check_rederive_ratchet` DRAIN, and the walk is a separate unit from
the census for the reason `agda_walk` is separate from `ban_census`: a pure function of text can
be cased without a tree, and a walk is where the filesystem assumptions live. `agda_walk` does
NOT serve here — it enumerates `.agda` under one root, and this enumerates `.py` across several.
Reaching for it because the names rhyme would be the shared-name-is-not-shared-authority defect.

⚑⚑ EVERY EXCLUSION IS A MEASURED INCIDENT, NOT A TIDINESS RULE, and the origin records each:

  * `tests/` is excluded BY CONSTRUCTION. Its whole job is to hold the BROKEN forms as
    regression witnesses, so censusing them would demand that the tests stop testing.
  * `.edit-snapshots/` holds copy-aside backups of untracked files — byte copies of censused
    sources. Measured: two keys appeared for the gate's OWN file seconds after a guard run.
    *A backup of a censused file is not a second derivation.*
  * `jea/` and `el-atlas/` are absent from the ROOTS rather than the exclusions, and the
    difference is substantive: a policy gate forbids them from importing the tree that holds
    the authorities, so they CANNOT adopt them and *it would be dishonest to census them as
    debt.* An exclusion says "skip this"; an absent root says "this was never the population."

⚑ THE ROOTS AND EXCLUSIONS ARE DECLARED HERE, NOT PASSED IN, because they encode policy rather
than a caller's scope. A caller free to widen them could census a tree that is barred from
adopting the authorities, and a false key banked into a paydown-only baseline is debt nobody can
ever legitimately pay.
"""

from __future__ import annotations

import os
from pathlib import Path

#: The trees whose `.py` files a tooling census covers. ⚑ `jea/` and `el-atlas/` are absent by
#: POLICY, not oversight — see the module docstring.
ROOTS = ("scripts", "scratch")

#: Directories skipped inside those trees, each for a recorded reason.
EXCLUDE = frozenset({"tests", "eliza", ".venv", "__pycache__", ".edit-snapshots"})

#: The extension a tool carries.
SUFFIX = ".py"


def tool_files(root: str | Path) -> list[str]:
    """Return every `.py` file under `root`, sorted, minus the excluded directories.

    ⚑ PRUNED IN PLACE, which is what stops `os.walk` DESCENDING into an excluded tree. Filtering
    the results instead would still walk a vendored virtualenv — thousands of files to discard.
    """
    out: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE]
        here = Path(dirpath)
        out.extend(str(here / f) for f in filenames if f.endswith(SUFFIX))
    return sorted(out)


def sources(repo: str | Path) -> list[tuple[str, str]]:
    """Return `(repo-relative path, text)` for every tool under this repo's declared roots.

    ⚑⚑ THE PATHS ARE REPO-RELATIVE because a census key built from them is compared against a
    committed baseline. An absolute path would read as a new offender for every key at once, and
    a paydown-only ratchet would then refuse every commit while defending a phantom population —
    a measured hazard in this family (gate-F76 is its sibling, one type away).

    ⚑ A FILE THAT CANNOT BE READ IS SKIPPED, NOT GUESSED AT. Supplying an empty string for it
    would silently shrink the census, and a key that vanishes lowers a baseline nobody can raise
    again.

    ⚑ A MISSING ROOT IS SKIPPED RATHER THAN RAISED, so this answers the same way in a checkout
    that carries only one of the trees — an adopter's case, not a hypothetical.
    """
    base = Path(repo)
    out: list[tuple[str, str]] = []
    for tree in ROOTS:
        start = base / tree
        if not start.is_dir():
            continue
        for path in tool_files(start):
            try:
                text = Path(path).read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            out.append((str(Path(path).relative_to(base)), text))
    return out
