#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Decide what a gate's WIRED INVOCATION is, so a verdict is about the gate and not its file.

⚑⚑⚑ WHY THIS EXISTS, AND IT TOOK THREE WRONG DIAGNOSES TO REACH (gate-G26, gate-G28, gate-G29).
`commit_refusal` reported `tool mode census in sync` as `101 added of 101 held` while
`toolmodes.py --check` reported the census FRESH. Two instruments, one subject, opposite
verdicts — and the census-sync gate's own `--check` is the correct one.

⚑⚑ THE CAUSE IS THAT A SCRIPT IS NOT A GATE. `scratch/toolmodes.py` carries TWO gate
mechanisms: `--nearmiss`, a real `set_ratchet` ratchet over `.nearmiss-baseline` whose own
docstring says it is **deliberately not wired** into pre-commit, and `--check`, the census-sync
drift gate the hook actually runs. `commit_refusal.verdict` keys on `gate.script`, finds the
unwired ratchet's key set and baseline, and renders that arithmetic under the wired gate's
name. The number is real; it is a measurement of the wrong mechanism.

⚑ THE ARGV WAS ALWAYS AVAILABLE AND WAS DISCARDED. `gate_status.gates()` yields
`(name, argv, conditional)` with the full invocation including flags; `hook_gates` matches the
script path out of it and drops the rest. So the distinguishing information sat one field away
from the verdict that needed it, which is why this is a narrow repair rather than a new reader.

⚑⚑⚑ WHAT THIS DOES NOT CLAIM, BECAUSE THE POPULATION IS ONE. `gate_status --list` shows SIX
gates wired as `--check`, and only toolmodes misreports — the others carry no `set_ratchet` call
for a census to find. So a `--check` invocation is not evidence of a defect, and this module
makes no claim that it is: it reports what the hook WIRES, and the caller decides. A predicate
that assumed every `--check` gate was miscensused would be a second wrong diagnosis in the
module written to fix the first one.
"""

from __future__ import annotations

import re

# A census-sync gate answers with its own exit code, not with a key diff. These are the spellings
# the hook uses for that contract — read from `gate_status --list`, not invented.
SYNC_FLAGS: tuple[str, ...] = ("--check", "--check-census")

# ⚑ ANCHORED, SO A FLAG IS A WORD. A bare `in` test would match `--check` inside `--check-census`
# and inside any future `--check-anything`, which is the substring-for-structure defect this repo
# files against. Both spellings are listed above deliberately rather than matched by prefix.
_ALTERNATION = "|".join(re.escape(flag) for flag in SYNC_FLAGS)
_FLAG = re.compile(r"(?<![\w-])(" + _ALTERNATION + r")(?![\w-])")


def sync_flag(argv: str) -> str:
    """Return the census-sync flag this invocation carries, or the empty string.

    ⚑ READS THE INVOCATION, NEVER THE SCRIPT. The whole point is that the same file can hold a
    ratchet the hook does not run; only the argv says which mechanism is wired.
    """
    found = _FLAG.search(argv)
    return found.group(1) if found else ""


def is_sync_gate(argv: str) -> bool:
    """Report whether the hook wires this gate as a census-sync drift check."""
    return bool(sync_flag(argv))


def why_not_census(argv: str) -> str:
    """Return why censusing this gate would measure the wrong mechanism, or the empty string.

    ⚑ THE MESSAGE NAMES THE WIRED MODE, because a verdict that says only "not censused" leaves
    the reader unable to tell a deliberate abstention from a reader that failed. The gate's real
    answer is its own exit code, and the row should say so.
    """
    flag = sync_flag(argv)
    if not flag:
        return ""
    return f"wired as `{flag}` — a census-sync gate answers with its own exit code, not a key diff"
