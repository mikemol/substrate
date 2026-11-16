#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The mypy census, ratchet-keyed: `<error-code>::<relpath>` -> [messages].

⚑ WHY A TYPE GATE, AND THE EVIDENCE IS A DEFECT LOG (user, 2026-08-01: *"have we reached a
point where we should be using [a type checker] to provide typing guarantees… because that's
what it's feeling like"*). Seven defects in ONE session that a checker catches mechanically:
a 2-tuple widened to a 3-tuple with 4 returns and a call site unchecked; a function called
before it existed; an alias that does not exist; an invented API; a function reached behind a
`hasattr` fallback — **the strongest case, because the guard HID it and a fallback to an
absent function would have measured NOTHING**; a callable-vs-list argument error; an unused
import. Every one cost a run-edit-run cycle; two shipped behind guards that silently
degraded. *A signature change verified only by running it is the same class as a census
verified only by reading it.*

⚑⚑ SPLIT OUT OF `scratch/_pycodemod_census.py` (⟡corpus-repoint), AND THE MEASUREMENT IS THE
ARGUMENT. `check_mypy_ratchet` — a pre-commit gate — carried a **4,955-finding closure over
23 callees** to call this one function, because it reached it through `pycodemod` and that
drags the whole analysis family. The function itself needs `subprocess`, `re` and a list of
paths. A gate should not import a codemod toolkit to run a type checker.

⚑ KEYED, NOT COUNTED. `set_ratchet` needs a SET so swap-gaming is refused (remove one, add
another — the added key is caught) and so `--list` can enumerate. Line numbers are
deliberately NOT in the key: they churn on every unrelated edit above a site, which is a
measured defect elsewhere (`check_rederive_ratchet` keyed on line number and would have fired
on nearly every commit).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from mikemol.corpus import tree_root

from substrate import corpus

# ⚑ A CENSUS OVER A LARGE CORPUS IS SLOW, AND A TIMEOUT THAT FIRES IS A CENSUS THAT DID NOT
# RUN — which must not read as a clean one. See the `__unrunnable__` sentinel below.
_TIMEOUT_S = 900

# The error-code bracket mypy appends, e.g. `[no-any-return]`. Absent for some messages,
# which key as `misc` — mypy's own default.
_ERROR_RE = re.compile(r"^(.+?):\d+:(?:\d+:)?\s*error:\s*(.*?)(?:\s*\[([\w-]+)\])?$")

# Returned when mypy could not run at all. A CALLER MUST DISTINGUISH THIS FROM `{}`.
UNRUNNABLE = "__unrunnable__"

# ⚑ `--ignore-missing-imports` IS NOT A CONCESSION. These tools import `panflute`, `libcst`,
# `cupy` — optional deps absent in a bare environment. Without it the census is dominated by
# rows saying nothing about our code, and *a census too wide to read has already failed*.
#
# ⚑ `--explicit-package-bases` BECAUSE THE CORPUS HAS DUPLICATE BASENAMES. MEASURED:
# `scratch/hadamard_basis.py` and `scratch/figures/hadamard_basis.py` both map to module
# `hadamard_basis`, and mypy REFUSES the whole run rather than guess — correctly. Without
# this the census is not "clean", it is ABSENT, and the first cut reported that as `0 keys`.
#
# ⚑⚑ PUBLIC BECAUSE A SECOND READER NEEDS THE SAME PREDICATE. `type_scope` runs a one-file
# census with ONE arm varied (`--follow-imports`), and a module-private constant is not an
# interface — respelling these four flags there would create a second authority that drifts
# from the gate's silently, which is `census-keyed-on-one-spelling` at the flag list. Exported
# rather than made a parameter here: a `flags=` argument would let any caller change the
# GATE's predicate, and the gate's predicate is policy, not a setting.
FLAGS = (
    "--ignore-missing-imports",
    "--explicit-package-bases",
    "--no-error-summary",
    "--no-color-output",
)


def _run(files: list[str], root: Path) -> subprocess.CompletedProcess[str] | None:
    """Invoke mypy over the given repo-relative paths. None when it is not installed.

    ⚑ `sys.executable`, NOT `"python3"` — AND THE FIRST CUT MEASURED NOTHING. Under `uv run
    --with mypy`, mypy is installed for THAT interpreter; a bare `python3` subprocess is a
    different one, so the run failed, the parse found no error lines, and **0 keys over 60
    unannotated files** was reported as a clean census. That is the
    guard-degrades-to-measuring-nothing class, in the tool built to catch it, caught only
    because zero was implausible.
    """
    try:
        return subprocess.run(
            [sys.executable, "-m", "mypy", *FLAGS, "--", *files],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_S,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None


def parse(stdout: str) -> dict[str, list[str]]:
    """Turn mypy's output into the keyed census.

    ⚑ PUBLIC FOR THE SAME REASON `FLAGS` IS. The key spelling `<code>::<relpath>` is what the
    baseline, the gate, the summary and `type_scope` all agree on; a second reader that
    re-implemented this regex would be a second definition of the census key, and the two
    would disagree first on exactly the messages that have no `[code]` bracket.
    """
    out: dict[str, list[str]] = {}
    for line in stdout.splitlines():
        m = _ERROR_RE.match(line)
        if m:
            code = m.group(3) or "misc"
            out.setdefault(f"{code}::{m.group(1)}", []).append(m.group(2))
    return out


def type_errors(
    paths: list[str] | None = None, root: Path = corpus.ROOT
) -> dict[str, list[str]] | None:
    """Return the keyed mypy census, or None when mypy is not installed.

    ⚑ A FAILED RUN MUST NOT READ AS A CLEAN ONE. mypy exits 1 when it finds errors and 2 when
    it CANNOT RUN; only the first is a census. Returning the `UNRUNNABLE` sentinel for the
    second is what makes "no errors" mean no errors.

    ⚑ AND IT SAYS WHY IT COULD NOT RUN. "not importable" was once a guess printed as a fact;
    mypy exits 2 for a config error, a duplicate module name, or an unreadable path just as
    readily as for an absent install — and each wants a different fix. Carry the real message
    rather than a plausible story.

    ⚑⚑⚑ AND THE `is_absolute()` GUARD ADMITTED EXACTLY THE FAILING SHAPE (gate-G257). A path from a
    BORROWING checkout is absolute — that IS the case that raises — so the guard excluded only the
    inputs that could never fail. Measured: repairing `type_census_summary` moved its crash one
    frame down into this line, which is the census being right rather than a new site.
    """
    tree = tree_root.of(root)
    files = [
        tree.label(Path(p)) for p in (paths if paths is not None else corpus.py_files(root=root))
    ]
    p = _run(files, root)
    if p is None:
        return None
    if p.returncode not in (0, 1) or "No module named mypy" in (p.stderr or ""):
        detail = (p.stderr or p.stdout or "").strip()[:400]
        return {UNRUNNABLE: [detail or f"mypy exited {p.returncode}"]}
    return parse(p.stdout or "")
