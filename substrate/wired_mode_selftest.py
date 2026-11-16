#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pin the wired-mode predicate against the hook's own invocations.

⚑⚑⚑ THE LOAD-BEARING CASE READS THE LIVE HOOK THROUGH ITS OWN PARSER. The claim this module
exists to support is that `tool mode census in sync` is wired as `--check` and never as
`--nearmiss`. A fixture asserting that would only prove the predicate agrees with my
transcription of the hook.

⚑⚑ AND THE FIRST CUT OF THAT CASE FAILED, WHICH IS THE FINDING. It filtered the hook's lines by
substring for `toolmodes.py` and reported an invocation that is not a sync gate — while
`gate_status --list` shows exactly one toolmodes row, wired `--check`. A raw line scan sees
comments and non-`run` lines that the shell-aware parser correctly excludes, so the disagreement
was between MY reader and the AUTHORITY, not within the hook. The case now goes through
`gate_status.gates()`, which refuses outright on a hook that does not parse as shell.

⚑ THE NEGATIVE CONTROL IS THE ONE MOST LIKELY TO BE MISSING. Six gates are wired as `--check`
and only toolmodes was misreported, so a predicate that flagged every sync gate as defective
would satisfy every positive case here and be wrong about five of them. The suite asserts the
ratchet gates are NOT sync gates, against the same parsed roster.

⚑ THE ANCHORING CASES EXIST BECAUSE `--check` IS A PREFIX OF `--check-census`. A substring test
passes every case above and silently conflates two distinct contracts.
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import commit_refusal, wired_mode

ROOT = Path(__file__).resolve().parent.parent

Case = tuple[str, bool]

_TOOLMODES = 'python3 "$ROOT/scratch/toolmodes.py" --check'
_SQL = 'python3 "$ROOT/jea/metalanguage/sql_lift.py" --check-census'
_RATCHET = 'python3 "$ROOT/scripts/check_ban_ratchet.py" --quiet'
_BARE = 'python3 "$ROOT/scripts/decl_shape_tag.py"'


def _flag_cases() -> list[Case]:
    """Return the cases pinning which flag a given invocation carries."""
    return [
        ("a --check invocation is a sync gate", wired_mode.is_sync_gate(_TOOLMODES)),
        ("it reports the flag it found", wired_mode.sync_flag(_TOOLMODES) == "--check"),
        ("a --check-census invocation is a sync gate", wired_mode.is_sync_gate(_SQL)),
        # ⚑ THE TWO SPELLINGS STAY DISTINCT. A prefix match would report `--check` here.
        ("it is not confused with --check", wired_mode.sync_flag(_SQL) == "--check-census"),
    ]


def _negative_cases() -> list[Case]:
    """Return the control without which a constant-True predicate would pass.

    ⚑ A RATCHET GATE MUST NOT READ AS A SYNC GATE, or the repair would abstain from censusing
    the gates whose key diff is the whole point of their verdict.
    """
    return [
        ("a --quiet ratchet gate is NOT a sync gate", not wired_mode.is_sync_gate(_RATCHET)),
        ("a bare invocation is NOT a sync gate", not wired_mode.is_sync_gate(_BARE)),
        ("a non-sync gate reports no reason", wired_mode.why_not_census(_RATCHET) == ""),
        # ⚑ THE FLAG MUST BE A WORD, not a substring of a longer token.
        (
            "a --checkpoint flag is NOT a sync flag",
            not wired_mode.is_sync_gate("python3 tool.py --checkpoint"),
        ),
        (
            "a --no-check flag is NOT a sync flag",
            not wired_mode.is_sync_gate("python3 tool.py --no-check"),
        ),
    ]


def _reason_cases() -> list[Case]:
    """Return the cases pinning that the abstention names the wired mode."""
    why = wired_mode.why_not_census(_TOOLMODES)
    return [
        ("a sync gate gives a reason", why != ""),
        ("the reason names the wired flag", "--check" in why),
        # ⚑ THE READER MUST BE ABLE TO TELL ABSTENTION FROM FAILURE.
        ("the reason says the gate answers with its exit code", "exit code" in why),
    ]


def _wired() -> list[tuple[str, str]]:
    """Return `(name, argv)` for every gate the hook wires, via the hook's own parser."""
    out: list[tuple[str, str]] = []
    for row in commit_refusal.call_rows(commit_refusal.authority("gate_status"), "gates"):
        name, argv = commit_refusal.field(row, 0), commit_refusal.field(row, 1)
        if name is None or argv is None:
            continue
        out.append((str(name), str(argv)))
    return out


def _live_cases() -> list[Case]:
    """Read the wired roster, so the claim is about what the hook RUNS."""
    wired = _wired()
    if not wired:
        return [("the hook parser yields a roster", False)]

    toolmodes = [argv for _n, argv in wired if "toolmodes.py" in argv]
    ratchets = [argv for _n, argv in wired if "check_ban_ratchet.py" in argv]
    return [
        ("the hook wires toolmodes", len(toolmodes) > 0),
        # ⚑ THE CLAIM gate-G28 RESTS ON: the wired invocation is --check, not --nearmiss.
        (
            "every wired toolmodes invocation is a sync gate",
            all(wired_mode.is_sync_gate(a) for a in toolmodes),
        ),
        (
            "no wired toolmodes invocation names --nearmiss",
            all("--nearmiss" not in a for a in toolmodes),
        ),
        # And the control, against the same parsed roster.
        ("the hook wires the ban ratchet", len(ratchets) > 0),
        (
            "no wired ban-ratchet invocation is a sync gate",
            not any(wired_mode.is_sync_gate(a) for a in ratchets),
        ),
        # ⚑ THE SYNC POPULATION IS LARGER THAN THE ONE GATE THAT MOTIVATED THIS, so a reader
        #   treating `--check` as evidence of a defect would be wrong about the rest.
        (
            "more than one wired gate is a sync gate",
            sum(1 for _n, a in wired if wired_mode.is_sync_gate(a)) > 1,
        ),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = _flag_cases() + _negative_cases() + _reason_cases() + _live_cases()
    bad = [label for label, holds in cases if not holds]
    print(f"wired_mode: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
