# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.transcript_units`, over a synthetic transcript — never a real one."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from substrate import transcript_units as tu

_ASK = "please measure the thing"
#: The assistant record below carries two text blocks.
_TEXT_BLOCKS = 2

_RECORDS: list[dict[str, object]] = [
    {"type": "user", "message": {"role": "user", "content": _ASK}},
    {
        "type": "assistant",
        "message": {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "measuring now"},
                {"type": "tool_use", "id": "a", "name": "Bash", "input": {"command": "ls"}},
                {"type": "text", "text": "second block"},
            ],
        },
    },
    {
        "type": "user",
        "message": {
            "role": "user",
            "content": [{"type": "tool_result", "tool_use_id": "a", "content": "file.txt"}],
        },
    },
    {
        "type": "user",
        "message": {"role": "user", "content": "<system-reminder>plumbing only</system-reminder>"},
    },
    {"type": "mode", "mode": "auto"},
]


def _cases(path: Path) -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    got = tu.split(path)
    turns = tu.assistant_turns(got)
    texts = tu.record_texts(path)
    return [
        ("the human turn is found, on its 1-based line", got.human == [(1, _ASK)]),
        ("a harness-only user record is NOT a human turn", len(got.human) == 1),
        ("assistant prose is one unit per text block", len(got.assistant) == _TEXT_BLOCKS),
        ("assistant_turns joins a record's blocks", turns == [(2, "measuring now\nsecond block")]),
        (
            "a tool call's text is its input as JSON",
            [json.loads(t) for _l, t in got.tool_use] == [{"command": "ls"}],
        ),
        ("a tool result is taken from the user envelope", got.tool_result == [(3, "file.txt")]),
        ("record_texts covers every record, bookkeeping included", len(texts) == len(_RECORDS)),
        ("a bookkeeping record's speaker is unknown", texts[-1][1] == "unknown"),
    ]


def selftest() -> bool:
    """Run every case over a temporary transcript, reporting failures by name."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "t.jsonl"
        path.write_text("".join(json.dumps(r) + "\n" for r in _RECORDS), encoding="utf-8")
        cases = _cases(path)
    ok = sum(1 for _label, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"transcript-units selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(0 if ("--selftest" in sys.argv or len(sys.argv) == 1) and selftest() else 1)
