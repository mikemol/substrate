# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Splice the census blocks into the build-system skill, and gate them against drift.

⚑⚑⚑ DRAINED FROM `scripts/build_census.py` (W329). This is the host-file half: the marker pairs,
the splice, the sync and the drift check. What the blocks CONTAIN lives in `build_census_render`.

⚑ A TRACEBACK IS NOT A DIAGNOSIS (the lesson `sql_census` records). `BlockError` reports the host
file or a marker pair as missing, duplicated or inverted as a fact about the TREE, so a gate whose
HOST is absent reads as the tree lacking the file, not as a crashed tool.

⚑ ONLY THE STRUCTURAL BLOCK IS GATED. The observations block reads gitignored, hardware-specific
ledgers; gating it would fail on every machine and after every build, and a gate that cries wolf
gets disabled, taking this one with it.

⚑ EVERY ENTRY TAKES THE TREE. `root` is the repo and `scripts` its `scripts/` directory; the CLI
resolves them at call time, so a fixture tree can be censused without touching the real one.

⚑ `gen_build_makefiles` LOADS THE CLI SHIM AS A LIBRARY and calls `cmd_sync`/`cmd_check` with no
arguments, catching `BlockError`; the shim keeps those names and supplies the tree.
"""

from __future__ import annotations

import difflib
import sys
from typing import TYPE_CHECKING, Protocol, cast

from substrate import build_census_facts as facts
from substrate import build_census_render as render

if TYPE_CHECKING:
    from pathlib import Path

BEGIN = "--- BEGIN build-census ---"
END = "--- END build-census ---"
OBS_BEGIN = "--- BEGIN build-observations ---"
OBS_END = "--- END build-observations ---"
SKILL_REL = ".claude/skills/build-system/SKILL.md"
_SYNC_CMD = "`python3 scripts/gen_build_makefiles.py --sync-census`"


class _Snapshot(Protocol):
    def guard(self, name: str, paths: list[str], *, intent: str) -> object: ...


class BlockError(Exception):
    """The host file or a marker pair is missing, duplicated or inverted.

    ⚑ A fact about the TREE, reported as such rather than raised as a traceback.
    """


def read_skill(root: Path) -> str:
    """Return the skill's text, or refuse with the tree's missing host."""
    try:
        return (root / SKILL_REL).read_text(encoding="utf-8")
    except FileNotFoundError:
        msg = (
            f"{SKILL_REL} does not exist — the census has no host. Create the skill with the "
            f"marker lines (`{BEGIN}` … `{END}`) where the block belongs; --sync-census fills "
            "between them but will not create the file."
        )
        raise BlockError(msg) from None


def span(src: str, begin: str, end: str) -> tuple[int, int]:
    """Return `(body_start, body_end)` for a marker block; missing markers REFUSE, never insert."""
    i, j = src.find(begin), src.find(end)
    if i < 0 or j < 0:
        msg = (
            f"no `{begin}` … `{end}` pair in {SKILL_REL} — add the two marker lines where the "
            "block belongs; --sync-census fills between them but will not choose their place."
        )
        raise BlockError(msg)
    if src.count(begin) != 1 or src.count(end) != 1:
        msg = (
            f"{SKILL_REL} carries {src.count(begin)} `{begin}` and {src.count(end)} `{end}` "
            "marker(s); exactly one of each is required."
        )
        raise BlockError(msg)
    if j < i + len(begin):
        msg = f"`{end}` precedes `{begin}` — the markers are inverted."
        raise BlockError(msg)
    return i + len(begin), j


def splice(src: str, body: str, begin: str = BEGIN, end: str = END) -> str:
    """Return `src` with the marked block's body replaced by `body`."""
    a, b = span(src, begin, end)
    return src[:a] + "\n" + body + "\n" + src[b:]


def current_body(src: str, begin: str = BEGIN, end: str = END) -> str:
    """Return the text currently between a marker pair."""
    a, b = span(src, begin, end)
    return src[a:b]


def spliced_all(src: str, root: Path, scripts: Path) -> str:
    """Return `src` with both blocks applied: the structural one gated, the other refreshed."""
    structural = splice(src, render.render_block(root, scripts), BEGIN, END)
    return splice(structural, render.render_observations(root, scripts), OBS_BEGIN, OBS_END)


def _snapshot(root: Path, path: Path) -> None:
    """Arm `edit_snapshot` before rewriting a file we read.

    ⚑ THE ZERO-TOLERANCE SNAPSHOT RATCHET CAUGHT THIS MISSING IN THE ORIGIN, on the very module
    written to build a census: `cmd_sync` rewrites SKILL.md in place, the read-then-rewrite shape
    that made 33 files unrecoverable. Recovery is per-file and MANUAL by design.

    ⚑ `edit_snapshot` LIVES IN `scratch/`, NOT `scripts/`, and is loaded by LOCATION from there. A
    guard that always takes its except-branch protects NOTHING while looking armed.

    ⚑ `intent="apply"` IS ENTAILED BY THE CALLER: this is reached only from `cmd_sync`, past its
    `new == src` early exit, immediately above an unconditional write. `cmd_check`, the drift
    GATE, never calls it. And argv here may belong to ANOTHER tool (`gen_build_makefiles` reaches
    this as a library), so an argv-reading guard would decide on evidence about a different request.
    """
    try:
        snap = cast("_Snapshot", facts.load_script(root / "scratch", "edit_snapshot"))
        snap.guard("build_census", [str(path)], intent="apply")
    except (ImportError, OSError, AttributeError, RuntimeError, ValueError, TypeError) as exc:
        sys.stdout.write(f"   ⚠ snapshot unavailable ({exc}) — recover via git if needed\n")


def cmd_sync(root: Path, scripts: Path) -> int:
    """Rewrite both census blocks in the skill; exit code 0."""
    src = read_skill(root)
    new = spliced_all(src, root, scripts)
    if new == src:
        sys.stdout.write(
            f"gen_build_makefiles --sync-census: the census in {SKILL_REL} is already current.\n"
        )
        return 0
    _snapshot(root, root / SKILL_REL)
    (root / SKILL_REL).write_text(new, encoding="utf-8")
    sys.stdout.write(
        f"gen_build_makefiles --sync-census: rewrote the census in {SKILL_REL} "
        f"({len(src)} bytes -> {len(new)}).\n"
    )
    return 0


def cmd_check(root: Path, scripts: Path) -> int:
    """DRIFT GATE: return 1 unless the committed STRUCTURAL block is what `--sync` would write."""
    src = read_skill(root)
    fresh = render.render_block(root, scripts)
    if splice(src, fresh, BEGIN, END) == src:
        sys.stdout.write(
            f"gen_build_makefiles --check-census: the census in {SKILL_REL} is fresh.\n"
        )
        return 0
    diff = difflib.unified_diff(
        current_body(src, BEGIN, END).splitlines(),
        ("\n" + fresh + "\n").splitlines(),
        fromfile=f"{SKILL_REL} (committed)",
        tofile="derived just now",
        lineterm="",
    )
    for line in diff:
        sys.stdout.write(line + "\n")
    sys.stderr.write(
        f"\ngen_build_makefiles --check-census: the census in {SKILL_REL} is STALE — run "
        f"{_SYNC_CMD}\n"
    )
    return 1


def cmd_gates(root: Path) -> int:
    """Print the DECLARED gate roster partitioned by phase, the population `gate_ledger` lacks.

    ⚑ THIS MODE EXISTS BECAUSE THE QUESTION KEPT NEEDING A SHELL COMPOSITION. "Which gates run in
    which phase" was answerable only by eye over a 396-line hook, or by an inline `python3 -c`
    the no-chaining hook rightly refuses. The judgement belongs in a program.
    """
    gates = facts.gate_census(root)
    seen: str | None = None
    for name, phase in gates["gates"]:
        if phase != seen:
            sys.stdout.write(f"== {phase}\n")
            seen = phase
        sys.stdout.write(f"   · {name}\n")
    sys.stdout.write(
        f"\n{gates['count']} declared gate(s) across {len(gates['phases'])} phase(s).\n"
    )
    sys.stdout.write(
        "⚑ DECLARED, from the hook's own `run` call sites — `gate_ledger.py --report` ranks\n"
    )
    sys.stdout.write("  only what it has OBSERVED, which is a different and smaller number.\n")
    return 0
