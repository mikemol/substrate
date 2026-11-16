#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Locating the paperkit engine and running one of its entry points — the subprocess boundary.

⚑⚑⚑ THIS IS THE SMALLER HALF OF `scripts/wg_engine.py`, AND THE HALF THAT NAME DESCRIBED. Of the
54 attribute reads `substrate/attr_reads.py wg_engine.*` finds, eight reach the machinery here
and forty-six reach three path constants that had no reason to live behind a subprocess import.
Those went to `substrate.worklist_paths`; what stayed is everything that touches ANOTHER PROGRAM —
where it lives, what environment its child gets, where its scratch goes, and how its transcript is
summarised. Nothing here knows what a worklist ITEM is, which is what made the original seam
separable and is preserved unchanged.

⚑⚑ IT IS TYPED, AND THAT IS THE POINT OF DRAINING IT FIRST RATHER THAN THE ORDER BEING COSMETIC.
`pyproject.toml`'s law is *type-the-callee, THEN name-it*: converting a call site whose callee is
untyped turns a silent hole into a BLOCKED EDIT, strictly worse than leaving it. The superseded
module is stdlib-only (`pycodemod --imports` reports STDLIB=6, zero first-party), so it is a true
leaf — nothing beneath it needed draining first, and the law is satisfiable here. A prior drain
stalled precisely because its callee sat under an untyped hub this package may not import.

⚑⚑ `Invocation` EXISTS BECAUSE THE PER-FILE GATE SAID SO, AND IT WAS RIGHT. The superseded `run`
takes entry, extra, quiet, out and scratch as five loose parameters; carrying the two this version
needs besides pushed it to six, and `PLR0913`/`PLR0917` fired. A function accumulating optional
knobs is a REQUEST that has not been named — so the request is now a frozen record, which also
makes it something a caller can build, inspect and pass around rather than re-spell at each site.
The gate that keeps firing says the unit is wrong; the fix is to match its grain.

⚑ `run` RETURNS A RECORD, NOT A BARE EXIT CODE. The superseded function prints the transcript as a
side effect and returns an int, so a caller that wants the text — a case asserting what was
summarised, a report embedding it — has to capture stdout or re-run the child. Separating WHAT
HAPPENED from WHERE IT IS WRITTEN is what makes the summariser testable without spawning anything.

⚑ THE ENVIRONMENT IS INJECTED, NEVER READ AT IMPORT. The superseded module evaluates
`os.environ.get("PAPERKIT")` and `PAPERKIT_TMPDIR` at module scope, so the search path is frozen by
whatever the first importer's environment held and a case cannot vary it without reimporting. Here
every environment read is a defaulted PARAMETER, which is the same capability with the freeze
removed — and it is why this module's suite can drive the refusal path with no checkout present.
"""

from __future__ import annotations

import contextlib
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from substrate import worklist_paths

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

#: The engine file whose presence identifies a paperkit checkout.
MARKER = Path("paperkit") / "gate.py"

#: The environment variable that pins a checkout, and the conventional fallback location.
PIN = "PAPERKIT"
CONVENTIONAL = "~/github/paperkit"

#: The scratch root when nothing overrides it, and the variable that does.
SCRATCH_PIN = "PAPERKIT_TMPDIR"
SCRATCH_DIRNAME = ".paperkit-tmp"

#: Keep the sandbox tree after a run, for debugging.
KEEP_PIN = "PAPERKIT_KEEP_SCRATCH"

# ⚑ ONLY Delta NEEDS A SANDBOX. The first cut of the superseded module redirected TMPDIR for EVERY
# entry point and created the directory eagerly, so `--figures` and `--items` — which spawn nothing
# and mutate nothing — still minted a scratch dir. Redirecting a resource a mode does not use is
# how a scratch dir becomes permanent without anyone deciding it should.
NEEDS_SANDBOX = frozenset({"discriminate.py"})

#: The prefix the engine tags its own verdict lines with.
VERDICT_PREFIX = "paperkit-"

#: The exit code for "could not measure" — distinct from the engine's own pass/fail.
CANNOT_MEASURE = 2


@dataclass(frozen=True, slots=True)
class Located:
    """Where the engine is, or why it could not be found.

    ⚑ THE REFUSAL CARRIES THE PLACES TRIED, NOT JUST A FLAG. "No engine found" that does not say
    where it looked is unactionable: the two failure causes — nothing cloned, versus a `PAPERKIT`
    pointing somewhere stale — are indistinguishable without the list, and they need opposite
    fixes.
    """

    root: Path | None
    tried: tuple[Path, ...]

    @property
    def found(self) -> bool:
        """Report whether a checkout was located."""
        return self.root is not None

    @property
    def why(self) -> str:
        """Explain the miss, naming every place looked and how to fix it."""
        if self.root is not None:
            return ""
        where = ", ".join(str(p) for p in self.tried) or "<nothing>"
        return (
            f"no paperkit engine found (looked in: {where}). Paperkit is an engine you point "
            f"at a project; set {PIN}=<checkout> or clone it to {CONVENTIONAL}."
        )


@dataclass(frozen=True, slots=True)
class Invocation:
    """One request to the engine: which entry point, with what arguments and placement.

    ⚑ THIS IS THE NAMED REQUEST THE SUPERSEDED SIGNATURE LEFT IMPLICIT — see the module note. A
    caller building one can hand it around, compare two, or assert on it; five loose optional
    parameters could only be re-spelled at every site.

    ⚑ `quiet` IS KEYWORD-ONLY BECAUSE A BARE `True` AT A CALL SITE SAYS NOTHING. `run(entry, args,
    True)` is unreadable at the point it matters most, and a boolean's meaning is carried entirely
    by its name.
    """

    entry: str
    extra: tuple[str, ...] = ()
    scratch: Path | None = None
    project: Path | None = None
    quiet: bool = field(default=False, kw_only=True)

    @property
    def sandboxed(self) -> bool:
        """Report whether this entry point needs a scratch sandbox at all."""
        return self.entry in NEEDS_SANDBOX

    def where(self) -> Path:
        """Resolve the project directory this invocation measures."""
        return worklist_paths.PROJECT if self.project is None else self.project


@dataclass(frozen=True, slots=True)
class Outcome:
    """What one engine invocation did: its exit code and the transcript it produced.

    ⚑ THE TRANSCRIPT IS A VALUE, NOT A SIDE EFFECT. The superseded `run` prints and returns an int,
    so asserting what it summarised meant capturing stdout. Returning the text lets the summariser
    be checked directly, and lets a caller choose the destination afterwards.
    """

    code: int
    text: str

    @property
    def located(self) -> bool:
        """Report whether the engine was found, as opposed to the run being refused."""
        return self.code != CANNOT_MEASURE


def locate(pin: str | None = None, conventional: str = CONVENTIONAL) -> Located:
    """Find the paperkit checkout, reporting every candidate that was tried.

    ⚑ THE PIN WINS SO A DIFFERENT ENGINE VERSION CAN BE SELECTED WITHOUT EDITING THIS FILE, and it
    is a PARAMETER rather than a module-level `os.environ` read so a case can drive both arms. The
    default `None` means "consult the environment", which keeps the caller's spelling unchanged.
    """
    raw = os.environ.get(PIN) if pin is None else pin
    tried: list[Path] = []
    for candidate in (raw, conventional):
        if not candidate:
            continue
        here = Path(candidate).expanduser()
        tried.append(here)
        if (here / MARKER).is_file():
            return Located(root=here, tried=tuple(tried))
    return Located(root=None, tried=tuple(tried))


def scratch_root(override: str | Path | None = None) -> Path:
    """Choose where the engine's sandbox trees are made.

    ⚑⚑ THE SCRATCH DIRECTORY IS CHOSEN, NOT INHERITED, AND THE VOLUME FILLED TWICE PROVING IT.
    `discriminate.py` grades a check by COPYING the project to a sandbox and mutating one file at a
    time, so its disk cost scales with (project size x input count) while the other entry points
    need almost none. On this box `/tmp` is a small tmpfs shared with the editor and the agent
    harness; Delta filled it and every child then failed at spawn with ENOSPC, which reads as "the
    tool is broken" rather than "the volume is full". Same shape as `membudget` owning the memory
    ceiling: the resource a tool needs is part of knowing how to invoke it.
    """
    if override is not None:
        return Path(override)
    pinned = os.environ.get(SCRATCH_PIN)
    if pinned:
        return Path(pinned)
    return worklist_paths.ROOT / SCRATCH_DIRNAME


@contextlib.contextmanager
def sandbox(request: Invocation, *, keep: bool | None = None) -> Iterator[dict[str, str]]:
    """Yield the child's environment, REMOVING the scratch tree afterwards.

    ⚑⚑ BOTH TIMES THE VOLUME FILLED, THE DEFECT WAS THE SAME SHAPE: a temp directory created as a
    side effect and owned by nobody. Delta copies the project once per mutated input and NOTHING
    was deleting it between runs. So the scratch is a CONTEXT, not a location — created only for
    the entry that needs it, and torn down on the way out even when the child crashes. That is the
    same discipline as `membudget` releasing a lease on exit: a resource acquired by a tool is
    released by that tool, never left for a human to notice when the volume fills.
    """
    env = dict(os.environ)
    if not request.sandboxed:
        yield env
        return
    base = scratch_root(request.scratch)
    base.mkdir(parents=True, exist_ok=True)
    made = tempfile.mkdtemp(prefix="run-", dir=str(base))
    for var in ("TMPDIR", "TEMP", "TMP"):
        env[var] = made
    keeping = bool(os.environ.get(KEEP_PIN)) if keep is None else keep
    try:
        yield env
    finally:
        if keeping:
            sys.stdout.write(f"worklist-gate: kept scratch {made}\n")
        else:
            shutil.rmtree(made, ignore_errors=True)


def scratch_size(path: str | Path | None = None) -> int:
    """Total the bytes currently held by the scratch tree — 0 when it does not exist.

    ⚑ EXISTS SO THE QUESTION IS ASKABLE. "Is something filling the disk" was answered by the volume
    filling, twice. A tool that acquires space should be able to report how much it is holding.
    """
    base = scratch_root(path)
    total = 0
    for found in base.rglob("*"):
        with contextlib.suppress(OSError):
            if found.is_file():
                total += found.stat().st_size
    return total


def verdicts(text: str) -> str:
    """Select the engine's own verdict lines from a transcript.

    ⚑⚑ THE VERDICT IS NOT RELIABLY THE LAST LINE, which is the exact defect found in
    `gate_status.run_gate` keeping `tail[-1]` while the ratchet family printed its hint last. A
    caller reaching for `| tail` is applying reasoning the tool should carry, so the lines the
    engine tags with its own name are SELECTED here and everything else is working detail.
    """
    return "\n".join(line for line in text.splitlines() if line.startswith(VERDICT_PREFIX))


def emit(text: str, out: str | Path | None = None) -> str:
    """Write a report to `out`, or return it for the caller's own stdout.

    ⚑ `--out=<file>` EXISTS BECAUSE A CALLER'S STDOUT IS NOT ALWAYS A PLACE THE RESULT CAN GO.
    Delta's report is long, and it was being produced correctly while the surrounding spool could
    not hold it — so the tool looked broken when the volume was. Naming the destination is the same
    move as a census persisting to a file instead of printing: a result worth computing is worth
    putting somewhere the next command can read.
    """
    body = text if text.endswith("\n") else text + "\n"
    if out is None:
        return body
    target = Path(out)
    target.write_text(body, encoding="utf-8")
    return f"worklist-gate: wrote {target} ({len(body.splitlines())} lines)\n"


def run(request: Invocation, located: Located | None = None) -> Outcome:
    """Invoke one paperkit entry point against the worklist project.

    ⚑ IT REFUSES RATHER THAN REPORTING CLEAN when the engine cannot be found. An unmeasurable check
    that exits 0 is indistinguishable from a passing one, and this repo reads a green gate as a
    fact about the tree — so the absent-engine case gets its own code and says so.

    ⚑ `located` IS INJECTED so a caller that already resolved the checkout does not re-search, and
    so a case can drive the refusal arm without manipulating the environment.
    """
    found = locate() if located is None else located
    if found.root is None:
        return Outcome(code=CANNOT_MEASURE, text=found.why)
    where = request.where()
    # ⚑ THE ENGINE RUNS AS A PACKAGE, NEVER BY PATH (paperkit:W297). The package directory stays on
    # the path beside the checkout until paperkit:W296 removes the engine's flat sibling imports.
    module = "paperkit." + request.entry.removesuffix(".py")
    cmd = [sys.executable, "-m", module, str(where)]
    cmd.extend(request.extra)
    with sandbox(request) as env:
        here = [str(found.root), str(found.root / "paperkit")]
        merged = dict(env)
        merged["PYTHONPATH"] = os.pathsep.join([*here, *filter(None, [merged.get("PYTHONPATH")])])
        completed = subprocess.run(
            cmd, cwd=str(where), capture_output=True, text=True, env=merged, check=False
        )
    text = (completed.stdout or "") + (completed.stderr or "")
    return Outcome(code=completed.returncode, text=verdicts(text) if request.quiet else text)


def environment(located: Located, env: Mapping[str, str] | None = None) -> dict[str, str]:
    """Build the child's environment for a located engine, without spawning anything.

    ⚑ SPLIT OUT SO THE ENVIRONMENT IS INSPECTABLE. What a child process is handed is a decision
    worth asserting on its own; folding it into `run` makes it observable only by spawning, which
    is exactly the coupling that made the superseded module's behaviour hard to pin down.
    """
    base = dict(os.environ if env is None else env)
    if located.root is not None:
        base[PIN] = str(located.root)
    return base
