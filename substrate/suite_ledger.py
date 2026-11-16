#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The last run's outcome per suite, and whether it still describes today's tree.

⚑ "HAVE I RUN THE SUITE SINCE THESE EDITS" IS A CENSUS QUESTION, NOT A MEMORY. Before this
existed the only available answer was the operator's recollection of which files had been
touched since the last green run, reported as a caveat. A caveat is what a missing measurement
sounds like.

⚑ THE PREDICATE IS THE CONTENT OF EVERY SUITE FILE, NOT A FUNCTION'S SOURCE. A run's result
depends on what the suites CONTAIN, so the stamp is `(label, digest(source))` per suite. That
makes it total: a new suite, a deleted suite and an edited suite all move it, and nothing else
does.

⚑ PER SUITE, NEVER ONE HASH OVER THE CORPUS. A single corpus digest answers "is anything
stale" and cannot say WHICH — so every edit would invalidate the whole record and the runner
could only ever say "re-run everything". Keyed per suite, the reader NAMES the suites whose
recorded result no longer describes their source, which is the actionable form.

⚑⚑ THE LEDGER IS WRITTEN ON PASS **AND** ON FAILURE, and the verdict is a COLUMN. Recording
only green runs would make the reader unable to distinguish "never measured" from "measured and
BROKEN" — the same collapse as a census folding `stale` into `clean`. A failing suite IS a
measurement; it is the reason to look, not a reason to record nothing.

⚑⚑⚑ AND THE COLUMN CARRIES THE KIND, NOT ONE BIT. It was `BROKEN`/`ok` while the run loop had
already distinguished four states — so the same run kept the grade in its metrics and flattened
it in the ledger, which is the one place the staleness reader looks. A reader CANNOT RECOVER
WHAT THE WRITER DISCARDED: a whole session was spent treating a suite as defective when it had
passed 67/67 and been killed by its memory lease.

⚑ EVERY NON-`ok` KIND IS A FAILURE, AND THE KIND IS REPORTED. Keying on one literal is how a
reader keyed on the old spelling would report every failing suite as passing the moment the
writer began recording WHICH kind. Keying on "not ok" is TOTAL: a kind added tomorrow is a
failure here without editing a line, and an unrecognised kind cannot silently become green.

⚑ `BROKEN` IS STILL ACCEPTED, because a ledger written before the kind existed is a real
measurement of a real run. Dropping it would make the currency question answer "never measured"
for a tree that WAS.

⚑ EXTRACTED FROM `scripts/run_selftests.py` (⟡retire-the-runner).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

# The kind a suite carries when it ran clean.
OK = "ok"

# The pre-kind spelling, still honoured: a ledger written before kinds existed measured a
# real run, and refusing it would report that tree as never measured.
LEGACY_BROKEN = "BROKEN"

# How many characters of the digest identify a suite's source. Collisions here cost a
# false CURRENT; the full digest costs nothing but width, so this is deliberately generous.
_DIGEST_CHARS = 12

# What a row that could not be read records, so an unreadable file never reads as unchanged.
UNREADABLE = "unreadable"

# A ledger row is `label \t digest \t kind`.
_ROW_FIELDS = 3


@dataclass(frozen=True, slots=True)
class Row:
    """One suite's recorded run: what its source was, and how the run ended."""

    digest: str
    kind: str

    @property
    def ok(self) -> bool:
        """Report whether this row records a clean run."""
        return self.kind == OK


@dataclass(frozen=True, slots=True)
class Reading:
    """What the ledger says about today's tree."""

    header: str = ""
    stale: tuple[str, ...] = ()
    gone: tuple[str, ...] = ()
    broken: tuple[tuple[str, str], ...] = ()
    suites: int = 0
    rows: dict[str, Row] = field(default_factory=dict)

    @property
    def current(self) -> bool:
        """Report whether the record describes today's tree at all."""
        return not (self.stale or self.gone)


def digest_of(path: Path) -> str:
    """Return the short digest of one suite's source, or UNREADABLE."""
    try:
        body = path.read_bytes()
    except OSError:
        return UNREADABLE
    return hashlib.sha256(body).hexdigest()[:_DIGEST_CHARS]


def stamp(suites: list[tuple[str, str]]) -> dict[str, str]:
    """Return `{label: digest}` for every suite — what the run WOULD test."""
    return {label: digest_of(Path(path)) for label, path in suites}


def render(
    suites: list[tuple[str, str]],
    census_counts: tuple[int, int],
    kinds: dict[str, str],
    broken: set[str],
) -> str:
    """Render the ledger body for one run, kinds and all."""
    passed, declared = census_counts
    stamps = stamp(suites)
    lines = [f"# suites={len(suites)}\tcases={passed}/{declared}\tfailed={len(broken)}"]
    for label, _path in suites:
        default = LEGACY_BROKEN if label in broken else OK
        lines.append(f"{label}\t{stamps[label]}\t{kinds.get(label, default)}")
    return "\n".join(lines) + "\n"


def _rows(body: str) -> tuple[str, dict[str, Row]]:
    """Split a ledger body into its header and its rows."""
    header = ""
    rows: dict[str, Row] = {}
    for line in body.splitlines():
        if line.startswith("#"):
            header = line
            continue
        parts = line.split("\t")
        if len(parts) == _ROW_FIELDS:
            rows[parts[0]] = Row(digest=parts[1], kind=parts[2])
    return header, rows


def read(body: str, suites: list[tuple[str, str]]) -> Reading:
    """Read a ledger against today's suites."""
    header, rows = _rows(body)
    now = stamp(suites)
    stale = tuple(
        sorted(
            label for label, dig in now.items() if label not in rows or rows[label].digest != dig
        )
    )
    gone = tuple(sorted(label for label in rows if label not in now))
    # ⚑ ONLY SUITES WHOSE RECORD STILL DESCRIBES THEIR SOURCE can be reported broken. A row
    # whose digest has moved is STALE — reporting it as broken would blame today's source for
    # yesterday's run.
    broken = tuple(
        sorted(
            (label, row.kind)
            for label, row in rows.items()
            if not row.ok and now.get(label) == row.digest
        )
    )
    return Reading(
        header=header, stale=stale, gone=gone, broken=broken, suites=len(suites), rows=rows
    )
