#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read the build's suite stamps — what ran, what kind of outcome it had, and whether it stands.

⚑⚑⚑ THE STAMP IS THE MEMO, AND `make` IS WHAT DERIVES A MISS. The runner's `--last` mode
carried a content-stamped ledger whose consumer (`catalog.library.items.SUITE`) treats a moved
stamp as a CACHE MISS to re-derive rather than a state to report — *"a suite's verdict is a pure
function of its source"*. That is exactly a build system's contract: a target is valid while its
stamp is newer than its source, and `make` re-derives it otherwise. So the ledger and the
population-sha were a second implementation of mtime.

⚑ WHAT THE STAMP HOLDS THAT A BARE MARKER CANNOT. `suite_run` writes the outcome INTO the stamp
(operator: *"that stamp can hold whatever you want it to, though? It can be JSON."*), so the
kind survives the run — `ok` / `cases` / `vacuous` / `unfit` / `refused` / `silent` / `unread`.
A suite KILLED by its lease is not a suite that FAILED, and flattening that to pass/fail
discards the distinction that cost a session to learn.

⚑⚑ A MISSING STAMP HAS THREE CAUSES AND THIS REPORTS WHICH IT CANNOT TELL. Never run, ran and
failed (the wrapper writes no stamp on failure, so the build re-runs it), or cleaned. The
reader states the absence; naming one cause would be the unestablished-cause error.

⚑ AND STALENESS IS mtime, NOT A HASH. `make` already decides it that way, and a second rule
here would be one relation with two answers — the drift this whole cut is removing.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from substrate import corpus

# Where `gen_selftest_mk` puts the stamps. ⚑ ONE AUTHORITY: the generator writes this path and
# this reader reads it, so a change moves both or neither.
BUILD = "_build/selftest"

# The stamp's extension, as the generated recipe names its targets.
SUFFIX = ".ran"


@dataclass(frozen=True, slots=True)
class Stamp:
    """One suite's recorded outcome, and whether it still describes its source."""

    label: str
    kind: str
    ok: int
    total: int
    fresh: bool


def stamp_path(label: str) -> Path:
    """Return the stamp path for one suite's label, as the generator spells it."""
    return corpus.ROOT / BUILD / (label.replace("/", "__") + SUFFIX)


def parse(text: str) -> tuple[str, str, int, int] | None:
    """Read a stamp's JSON body into its fields, or None when it is not one.

    ⚑ AN OLD EMPTY STAMP READS AS ABSENT, NOT AS A CRASH. Stamps written by the previous
    `touch` recipe hold nothing; a reader that raised on them would report the whole build as
    broken on the first run after the change.

    ⚑ THE `Any` FROM `json.loads` IS NARROWED HERE, AT THE SEAM. A raw return would carry it
    into every field read downstream — the recorded boundary shape.
    """
    try:
        parsed: object = json.loads(text)
    except ValueError:
        return None
    if not isinstance(parsed, dict):
        return None
    label, kind = parsed.get("label"), parsed.get("kind")
    ok, total = parsed.get("ok"), parsed.get("total")
    if not isinstance(label, str) or not isinstance(kind, str):
        return None
    if not isinstance(ok, int) or not isinstance(total, int):
        return None
    return label, kind, ok, total


def read(label: str, source: str) -> Stamp | None:
    """Return the recorded outcome for one suite, or None when no stamp stands.

    `fresh` is the build's own predicate: the stamp is newer than the source it describes.
    """
    path = stamp_path(label)
    try:
        body = path.read_text(encoding="utf-8")
        stamped = path.stat().st_mtime
    except OSError:
        return None

    fields = parse(body)
    if fields is None:
        return None

    try:
        fresh = stamped >= Path(source).stat().st_mtime
    except OSError:
        fresh = False

    name, kind, ok, total = fields
    return Stamp(label=name, kind=kind, ok=ok, total=total, fresh=fresh)


def census(suites: list[tuple[str, str]]) -> dict[str, Stamp | None]:
    """Read every suite's stamp. A None value is an absence, with three possible causes."""
    return {label: read(label, path) for label, path in suites}
