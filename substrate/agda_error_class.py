#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""What an Agda compile failure IS - kind, detail, remedy - read from its text, no compile.

THE FOURTH CUT OF THE DRAIN'S FOURTH FILE (`scratch/split_census.py:358-505`, W4 tick 43). The
classification is the reusable part; obtaining the text is not. `diagnose` once compiled a
file to get `txt`, so classifying the 121 build-failed modules was 121 compiles of what `make`
had already done. Here the predicate takes the text, and the build's own per-module log feeds
it.

THREE READINGS ARE LOAD-BEARING. EVERY `[FileNotFound]`, not the first: Agda reports ONE
missing module per run, so a search that stopped at match one made the verdict depend on
compile order; `finditer` collects them, and the consumed-parent verdict needs only ONE of them
to have a leaf directory. THE COMPILER'S OWN `[Kind]` IS A TIEBREAKER: this branch once
collapsed every non-FileNotFound failure to the single kind `other` - ~80% of the population,
unpartitioned - where `[NotInScope]` / `[NoParseForApplication]` / `[UnequalTerms]` are a
partial order over the same set; the kind stays PREFIXED `other:` so a consumer testing
`kind == "other"` cannot silently change meaning, `other_kind` is the accessor, and an
unrecognised shape stays bare `other` rather than inventing a class. AND THE PREDICATE EXPLAINS
ITSELF: pass a `trace` list and each decision appends to it - the only way to ask *why did it
decide that* without a REPL.

THE LEAF PROBE IS A PARAMETER. The origin asks `os.listdir(agda/<mod as path>)` whether a
missing module has leaf files beside where it would live - that is a fact about the tree, and
a suite must be able to state it without a tree, so `leaves_of(module) -> int` is supplied by
the caller. `leaves_on_disk(root)` builds the production one.

A CLASS'S REMEDY IS A FACT ABOUT THE TOOLKIT, EARNED BY A MEASUREMENT (user, 2026-08-03:
"Shouldn't the census surface the tool we found to fix the problem?"). Every `other:` branch
once returned `None`, so the worklist's `solvers()` reported `NotInScope` as having NO TOOL
while `fix_notinscope` was repairing 9 of its 44 modules the same hour. A row in
`CLASS_REMEDY` means the tool was RUN against the class and repaired part of it; it is NOT a
completeness claim, which is why the keys are the REFINED classes (`:resolvable`, `:fixity`)
and not the bare kinds - keying the bare kind reported a 44-module class SOLVED on a tool that
repairs its smallest fifth. The remedy strings name the origin's commands verbatim; they are a
consumer's contract, not this module's opinion.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

Verdict = tuple[str, str, str | None]
LeavesOf = "Callable[[str], int]"

_FILE_NOT_FOUND = re.compile(
    r"\[FileNotFound\][\s\S]{0,80}?Failed to find source of module\s+(\S+)"
)
_ERROR_KIND = re.compile(r"error:\s*\[(\w+)\]")
# How much of the first error line the detail carries.
DETAIL_CAP = 160
TRACE_CAP = 80
# The agda tree, relative to a repo root - where a missing module's leaves would live.
AGDA_DIR = "agda"

# measured 2026-08-03: over the 44-site NotInScope class, `fix_notinscope --apply` kept 9
# (isolate-checked), reverted 8, refused 27. measured 2026-08-17: `fix_noparse --apply`
# repaired 4 of 4 fixity sites from the per-module logs, all four verified clean.
CLASS_REMEDY: dict[str, str] = {
    "other:NotInScope:resolvable": "python3 scratch/fix_notinscope.py <build.log> --apply",
    "other:NoParseForApplication:fixity": "python3 scratch/fix_noparse.py agda/_build --apply",
}


def leaves_on_disk(root: str | Path, agda_dir: str = AGDA_DIR) -> Callable[[str], int]:
    """Return the production leaf probe: how many `.agda` files sit where `module` would live."""
    base = Path(root) / agda_dir

    def leaves_of(module: str) -> int:
        d = base / module.replace(".", "/")
        return sum(1 for p in d.iterdir() if p.suffix == ".agda") if d.is_dir() else 0

    return leaves_of


def _consumed_parent(
    mods: list[str], leaves_of: Callable[[str], int], trace: list[str] | None
) -> Verdict:
    """Classify a file-not-found: the first missing module WITH leaves is a consumed parent."""
    with_leaves: list[str] = []
    for mod in mods:
        n = leaves_of(mod)
        _say(trace, f"  {mod}: dir={'yes' if n else 'no'} leaves={n}")
        if n:
            with_leaves.append(mod)
    if with_leaves:
        mod = with_leaves[0]
        _say(trace, f"→ consumed-parent: {mod} has leaves")
        return (
            "file-not-found",
            mod,
            f"python3 scratch/split_pipeline.py {mod} --rewire-only --apply",
        )
    _say(trace, f"→ file-not-found but NO leaf dir for any of {mods}")
    return (
        "file-not-found",
        mods[0],
        f"no leaf directory for {mods[0]} — NOT the consumed-parent class; read the error",
    )


def _say(trace: list[str] | None, msg: str) -> None:
    """Append one decision step when a trace is being kept."""
    if trace is not None:
        trace.append(msg)


def classify(txt: str, leaves_of: Callable[[str], int], trace: list[str] | None = None) -> Verdict:
    """Return (kind, detail, remedy) for one compile's error text."""
    if not txt.strip():
        _say(trace, "no error text → clean")
        return ("clean", "", None)
    mods = [str(m.group(1)) for m in _FILE_NOT_FOUND.finditer(txt)]
    _say(trace, f"[FileNotFound] matches: {len(mods)}")
    if mods:
        return _consumed_parent(mods, leaves_of, trace)
    first = next((ln for ln in txt.split("\n") if "error:" in ln), "")
    m = _ERROR_KIND.search(first)
    kind = f"other:{m.group(1)}" if m else "other"
    _say(trace, f"→ {kind}: {first.strip()[:TRACE_CAP]}")
    return (kind, first.strip()[:DETAIL_CAP], CLASS_REMEDY.get(kind))


def other_kind(kind: str) -> str | None:
    """Return the compiler's error class from a kind, or None - an accessor, not a second parse."""
    return kind.split(":", 1)[1] if kind.startswith("other:") else None


def is_other(kind: str) -> bool:
    """Return whether a kind is in the `other` population, partitioned or not."""
    return kind == "other" or kind.startswith("other:")
