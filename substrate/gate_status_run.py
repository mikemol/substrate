# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Run a gate, or one gate under each of its flag modes, and say what it answered.

⚑ DRAINED FROM `scripts/gate_status.py` (W330); the process runner is a PARAMETER, so every case
here can be proved against a canned outcome without starting a gate.

⚑ THE VERDICT IS NOT THE LAST LINE (T15). The ratchet family prints its `refuse_hint` after the
census, so a tail-line reader reports advice — 9 of 12 red gates showed generic prose. Both
`run_gate` and `modes` read `facts.verdict_line`, one rule shared by the two views, so they cannot
disagree about what a gate said.

⚑ `modes` EXISTS BECAUSE THE QUESTION A GATE EDIT ACTUALLY ASKS HAD NO HOME. After changing a
gate's CLI the check is never "does it exit 0" — it is *does each MODE still do its own job*:
default reports the verdict, `--quiet` suppresses the frozen line, `--list` enumerates the census.
The LINE COUNT is reported beside the verdict because only the modes SIDE BY SIDE make a doubled
listing visible (`check_claims --list` printed all 14 claims twice, and the first run showed it).
`sample=N` returns the first N census rows so a rendering is inspectable from the same command.

⚑ READ-ONLY BY CONSTRUCTION. `SUBSTRATE_RATCHET_WRITE` is removed from the child's environment, so
no baseline can move: a sweep runs a gate once per mode, and a gate that banked debt on each read
would launder a transient into a permanent baseline several times over.

⚑ A WRITE-DEFAULT TOOL IS SWEPT IN `--check` ONLY. Its other modes REGENERATE its artifact once per
mode — measured on `sppf_node_index.py`. Skipping is the cheap error; writing is not.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

from substrate import gate_status_facts as facts

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from substrate.gate_status_exec import Runner

#: Per-command wall limit for one gate, or one mode of one gate.
GATE_TIMEOUT_S = 600

#: The environment variable that lets a ratchet move its baseline; a sweep must never set it.
WRITE_ENV = "SUBSTRATE_RATCHET_WRITE"

_RUN_WIDTH = 120
_MODE_WIDTH = 100
_DEFAULT = "(default)"
_TIMEOUT_TEXT = f"TIMEOUT after {GATE_TIMEOUT_S}s"
_INDENTS = (" ", "\t")


class Host(NamedTuple):
    """Where a sweep runs: the tree, the interpreter that runs a gate script, the environment."""

    tree: facts.Tree
    python: str
    environ: Mapping[str, str]


class ModesRequest(NamedTuple):
    """Which modes to sweep, how many census rows to keep, and whether writes are allowed."""

    which: tuple[str, ...] = facts.MODES
    sample: int = 0
    allow_writes: bool = False


class ModeRow(NamedTuple):
    """One mode's answer: exit status, non-blank line count, verdict, and sampled census rows."""

    mode: str
    rc: int
    nlines: int
    verdict: str
    rows: list[str]


def run_gate(argv: str, host: Host, runner: Runner) -> tuple[int, str]:
    """Return `(exit_code, first_meaningful_line)` — the gate's own verdict, not a guess."""
    root: Path = host.tree.root
    outcome = runner(facts.expand(argv, root), root, host.environ, GATE_TIMEOUT_S)
    if outcome.timed_out:
        return outcome.rc, _TIMEOUT_TEXT
    blob = (outcome.stdout + outcome.stderr).strip().split("\n")
    tail = [line for line in blob if line.strip()]
    return outcome.rc, facts.verdict_line(tail)[:_RUN_WIDTH]


def narrowed(which: tuple[str, ...]) -> tuple[str, ...]:
    """Return the modes a write-default tool is swept in: `--check` alone."""
    return tuple(m for m in which if m == facts.CHECK_MODE) or (facts.CHECK_MODE,)


def modes(script: str, host: Host, request: ModesRequest, runner: Runner) -> list[ModeRow]:
    """Return one `ModeRow` per flag mode of `script`, each run as a child of `host.python`."""
    root = host.tree.root
    path = facts.script_path(script, root)
    env = dict(host.environ)
    env.pop(WRITE_ENV, None)
    # ⚑ NARROW THE SWEEP BEFORE RUNNING, NOT AFTER.
    write_default = (False, "") if request.allow_writes else facts.write_default(script, root)
    which = narrowed(request.which) if write_default[0] else request.which
    out: list[ModeRow] = []
    for m in which:
        outcome = runner([host.python, path, *([m] if m else [])], root, env, GATE_TIMEOUT_S)
        name = m or _DEFAULT
        if outcome.timed_out:
            out.append(ModeRow(name, outcome.rc, 0, _TIMEOUT_TEXT, []))
            continue
        lines = [ln for ln in (outcome.stdout + outcome.stderr).split("\n") if ln.strip()]
        # census rows are the INDENTED lines; the verdict and hints sit at col 0
        census = [ln for ln in lines if ln[:1] in _INDENTS][: request.sample]
        rows = census if request.sample else []
        verdict = facts.verdict_line(lines)[:_MODE_WIDTH]
        out.append(ModeRow(name, outcome.rc, len(lines), verdict, rows))
    return out
