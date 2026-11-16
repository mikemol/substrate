#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The `--scope` census: live scratch/ references in directories the GATE does not cover.

⚑⚑⚑ THE SECOND DRAIN OF THE ⟡drain-arc. `scripts/check_scratch_independence.py` is refused
whole by the per-file gate (five mypy codes, `misc` on nearly every line), so its `_scope_report`
moves here as the natural second module: it CONSUMES the three readers `scratch_refs` already
holds, and it held nothing of its own except a walk, a split, and a rendering. The walk and the
split are pure and live in `census`; the rendering returns LINES, so a future CLI prints and this
module never does.

⚑⚑ THE DIFFERENTIAL IS BYTE-FOR-BYTE AGAINST THE ORIGIN'S OUTPUT, and it holds — including on
the one file where `scratch_refs` deliberately disagrees with the origin. `store.py` carries a
guarded `path.insert(0, join(…, "scratch"))` whose CALL opens on line 705 and whose LITERAL sits
on 706; `dependency_sites` (correctly) reports 705, where the origin's reader reports nothing. Yet
both censuses render the row identically as a MENTION, because the join between the two readers
is `hit.lineno in deps` — the literal's line looked up in a set of call lines. A dependency whose
string is not on the same line as the call it feeds is INVISIBLE to that join, in this module and
in the origin alike. ⚑ RECORDED, NOT FIXED HERE: repairing the join changes the census's verdict
shape, and this module owes fidelity first. The repair is a span check (`call.lineno <= hit.lineno
<= call.end_lineno`), and it is the next correction the drain will carry once the origin retires.

⚑ THE DIRECTORY SKIP IS A SUBSTRING TEST ON THE DIRECTORY PATH, kept verbatim from the origin: a
directory whose path CONTAINS `.git` — `.github` included — is skipped. That is wider than the
name it means, and the differential would redden if it were narrowed, so it stays and is named.

⚑⚑ THE ROSTER IS `substrate.promoted.ROOTS`, AND THIS FILE BRIEFLY HELD A THIRD COPY. The first
cut declared `ROOTS = ("jea", "el-atlas")` here — a hand-copy of the origin's roster, written one
tick before the reuse-search found `promoted.py`, whose header records that a hand-copied roster
is precisely the defect it exists to prevent and that it had ALREADY happened once. So the
verdict takes the roster as a PARAMETER, defaulting to the authority; the differential suites
pass the origin's two-entry roster explicitly, labelled as the origin's, because the origin
cannot see `substrate/` and a byte-for-byte comparison must ask both readers the same question.
The origin once printed "outside ROOTS, none of this blocks" unconditionally and was wrong for
`--scope jea/metalanguage` while the gate failed on those files; the verdict is computed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import scratch_refs as sr
from substrate.promoted import ROOTS

if TYPE_CHECKING:
    from pathlib import Path

# Directory-path fragments the walk skips. ⚑ SUBSTRING semantics, see the header.
SKIP = (".venv", "__pycache__", ".git", ".edit-snapshots")

# Refusal text for a scoped directory that does not exist.
MISSING = "  ⚑ no such directory: {d} — a fact about the QUERY, not the tree"

# The fixed prose of the report, kept verbatim from the origin so the differential can hold.
_HARD_NOTE = (
    "module-level — the file cannot be IMPORTED without scratch/; a gate here cannot run at all"
)
_GUARDED_NOTE = "a fallback runs — what it does is UNVERIFIED; cf. ⟡inert-guard"
_MENTION_NOTE = (
    "'scratch' in a non-docstring string that is not used as a path "
    "(error text, usage lines, test fixtures)."
)
_MENTION_KEPT = (
    "    Not runtime dependencies. `--mentions` lists them; they are kept because "
    "a stale path in a message is a broken pointer, just not this gate's kind."
)
_MENTION_TAIL = (
    "  ⚑ NOT runtime dependencies — error text, usage lines, hook examples, test "
    "fixtures. Worth reading for STALE PATHS (a broken pointer in a message), "
    "which is a different defect from a dependency, not a lesser one."
)
_INSIDE = (
    "  ⚑ {inside} IS INSIDE ROOTS ({roots}) — the GATE covers it, so these refs DO "
    "block a commit. Run the gate itself for the verdict; this mode's exit code is "
    "still read-only and says nothing about it."
)
_OUTSIDE = (
    "  ⚑ THIS IS A READ, NOT A GATE for {outside}: outside ROOTS, so none of it blocks a commit."
)
_OUTSIDE_WHY = (
    "     `scripts/` is unguarded because the docstring's exclusion covers a "
    "DIFFERENT edge (el-atlas→scripts/), not scripts/→scratch/."
)


@dataclass(frozen=True, slots=True)
class Row:
    """One live reference in the scoped census, classified."""

    relpath: str
    lineno: int
    kind: str
    depth: str
    snippet: str
    is_dep: bool


@dataclass(frozen=True, slots=True)
class Census:
    """What `census` scanned and found.

    `scanned` is the DENOMINATOR — a zero-row census over zero files is a fact about the query.
    `missing` names scoped directories that do not exist, and `warns` carries every file that
    could not be read, so neither absence reads as a clean file.
    """

    rows: tuple[Row, ...]
    warns: tuple[str, ...]
    scanned: int
    missing: tuple[str, ...]

    @property
    def deps(self) -> tuple[Row, ...]:
        """Return the rows that are dependencies — used as a path, or an import."""
        return tuple(r for r in self.rows if r.is_dep)

    @property
    def mentions(self) -> tuple[Row, ...]:
        """Return the residue — the word in a string that is not used as a path."""
        return tuple(r for r in self.rows if not r.is_dep)


def _skipped(path: Path) -> bool:
    """Report whether a file sits under a directory the walk skips (substring test)."""
    parent = str(path.parent)
    return any(fragment in parent for fragment in SKIP)


def _files(base: Path) -> list[Path]:
    """Return every `.py` under `base`, walk-skipped, in a deterministic order."""
    return sorted(p for p in base.rglob("*.py") if not _skipped(p))


def _rows_of(path: Path, root: Path) -> tuple[list[Row], tuple[str, ...]]:
    """Classify every hit in one file, joining the wide scan against the narrow one."""
    scan = sr.scan_file(path)
    deps = sr.dependency_sites(path)
    rel = str(path.relative_to(root))
    rows = [
        Row(
            rel,
            h.lineno,
            h.kind,
            sr.guard_depth(path, h.lineno),
            h.snippet,
            h.lineno in deps or h.kind == sr.IMPORT,
        )
        for h in scan.hits
    ]
    return rows, scan.warns


def census(scope: list[str], root: Path) -> Census:
    """Scan every `.py` under each scoped directory and classify what it found."""
    rows: list[Row] = []
    warns: list[str] = []
    missing: list[str] = []
    scanned = 0
    for d in scope:
        base = root / d
        if not base.is_dir():
            missing.append(d)
            continue
        for path in _files(base):
            scanned += 1
            found, w = _rows_of(path, root)
            rows.extend(found)
            warns.extend(w)
    return Census(tuple(rows), tuple(warns), scanned, tuple(missing))


def diagnostics(found: Census) -> list[str]:
    """Return the stderr half: missing directories and unreadable files, in the origin's words."""
    lines = [MISSING.format(d=d) for d in found.missing]
    lines += [f"  scratch-independence: WARN {w}" for w in found.warns]
    return lines


def inside_outside(scope: list[str], roots: tuple[str, ...] = ROOTS) -> tuple[list[str], list[str]]:
    """Split the scope by whether each directory sits under a promoted project."""
    inside = [d for d in scope if any(d == r or d.startswith(r + "/") for r in roots)]
    return inside, [d for d in scope if d not in inside]


def _empty_line(found: Census, scope: list[str]) -> str:
    """Render the one-line report for a census that found nothing."""
    return (
        f"scratch-independence --scope: {found.scanned} .py scanned across "
        f"{'/'.join(scope)}, 0 live scratch/ ref(s)."
    )


def render_mentions(found: Census, scope: list[str]) -> list[str]:
    """Render the `--mentions` listing: the residue, enumerated, per file."""
    if not found.rows:
        return [_empty_line(found, scope)]
    by_file: dict[str, list[tuple[int, str]]] = {}
    for r in found.mentions:
        by_file.setdefault(r.relpath, []).append((r.lineno, r.snippet))
    head = (
        f"scratch-independence --scope --mentions: {len(found.mentions)} mention(s) of "
        f"'scratch' in {len(by_file)} file(s) that are NOT used as a path."
    )
    lines = [head]
    for rel in sorted(by_file):
        lines.append(f"  {rel}")
        lines += [f"      :{ln:<5} {snip}" for ln, snip in sorted(by_file[rel])]
    return [*lines, "", _MENTION_TAIL]


def _verdict(scope: list[str], roots: tuple[str, ...]) -> list[str]:
    """Render the computed inside/outside-ROOTS verdict for the scope."""
    inside, outside = inside_outside(scope, roots)
    lines = [""]
    if inside:
        lines.append(_INSIDE.format(inside="/".join(inside), roots="/".join(roots)))
    if outside:
        lines.append(_OUTSIDE.format(outside="/".join(outside)))
        lines.append(_OUTSIDE_WHY)
    return lines


def render(
    found: Census, scope: list[str], *, quiet: bool, roots: tuple[str, ...] = ROOTS
) -> list[str]:
    """Render the `--scope` report: dependencies by file, the mention count, the verdict."""
    if not found.rows:
        return [_empty_line(found, scope)]
    deps = found.deps
    hard = sum(1 for r in deps if r.depth == sr.HARD)
    by_file: dict[str, list[tuple[int, str, str, str]]] = {}
    for r in deps:
        by_file.setdefault(r.relpath, []).append((r.lineno, r.kind, r.depth, r.snippet))
    head = (
        f"scratch-independence --scope: {len(deps)} DEPENDENC(Y/IES) on scratch/ "
        f"in {len(by_file)} of {found.scanned} .py file(s) across {'/'.join(scope)}"
    )
    split = f"  ⚑ {hard} HARD ({_HARD_NOTE}), {len(deps) - hard} guarded ({_GUARDED_NOTE})."
    lines = [head, split]
    if not quiet:
        for rel in sorted(by_file):
            marks = by_file[rel]
            tag = " ⚑HARD" if any(m[2] == sr.HARD for m in marks) else ""
            lines.append(f"  {rel}{tag}")
            lines += [
                f"      :{ln:<5} [{kind}] {depth:<7} {snip}"
                for ln, kind, depth, snip in sorted(marks)
            ]
    mention = f"  + {len(found.mentions)} MENTION(S) — {_MENTION_NOTE}"
    return [*lines, "", mention, _MENTION_KEPT, *_verdict(scope, roots)]
