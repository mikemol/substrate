# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The reply contract of luthen's endpoint resolver, as DATA (substrate:W320).

One input and one expected outcome per row. Two parties run the same table: substrate's
`luthen_resolver_selftest` runs it against `substrate.luthen_resolver`, and luthen receives it as
the acceptance cases for its own thin client (their W777), so "the client works" is a thing both
repos run rather than a claim. `python -m substrate.luthen_resolver_cases` prints the table as JSON.

The contract: the resolver prints ONE JSON line. Success is exit 0 AND state "answered" with a
non-empty string host and an integer port (`as_of` optional). Exit 1 is a refused query, exit 2 an
unreadable declaration. Every other outcome is a refusal that quotes what came back, and there is
NEVER a fallback to loopback.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Literal

Kind = Literal["answer", "no-answer", "unusable"]


@dataclass(frozen=True, slots=True)
class Case:
    """One resolver outcome: what the process printed, and what a consumer must conclude."""

    label: str
    code: int
    stdout: str
    kind: Kind
    host: str = ""
    port: int = 0
    as_of: str = ""
    quotes: str = ""


_ANSWER = (
    '{"state": "answered", "host": "postgres.example.svc", "port": 5432,'
    ' "as_of": "2026-09-22T00:00:00Z"}'
)

CASES: tuple[Case, ...] = (
    Case(
        "an answered record resolves to host, port and as_of",
        0,
        _ANSWER,
        "answer",
        host="postgres.example.svc",
        port=5432,
        as_of="2026-09-22T00:00:00Z",
    ),
    Case(
        "as_of is optional",
        0,
        '{"state": "answered", "host": "h", "port": 1}',
        "answer",
        host="h",
        port=1,
    ),
    Case("exit 1 (refused query) is a refusal", 1, '{"state": "refused"}', "no-answer"),
    Case("exit 2 (unreadable declaration) is a refusal", 2, '{"state": "unreadable"}', "no-answer"),
    Case(
        "a non-answered state is a refusal that quotes the state",
        0,
        '{"state": "refused"}',
        "no-answer",
        quotes="'refused'",
    ),
    Case(
        "an answer with no host is unusable",
        0,
        '{"state": "answered", "port": 5}',
        "unusable",
    ),
    Case(
        "an answer with a non-integer port is unusable",
        0,
        '{"state": "answered", "host": "h", "port": "5"}',
        "unusable",
    ),
    Case(
        "garbage stdout is a refusal that quotes it", 0, "not json", "no-answer", quotes="not json"
    ),
    Case("empty stdout is a refusal", 0, "", "no-answer"),
    Case("a launch failure (exit -1) quotes its message", -1, "boom", "no-answer", quotes="boom"),
    Case(
        "a refusal that carries a loopback host is still a refusal",
        1,
        '{"state": "refused", "host": "127.0.0.1", "port": 1}',
        "no-answer",
    ),
    Case("a bare loopback string is a refusal", 0, "127.0.0.1:30432", "no-answer"),
)


def row(case: Case) -> dict[str, object]:
    """Return one case as a plain mapping, field by field so every value keeps a concrete type."""
    return {
        "label": case.label,
        "code": case.code,
        "stdout": case.stdout,
        "kind": case.kind,
        "host": case.host,
        "port": case.port,
        "as_of": case.as_of,
        "quotes": case.quotes,
    }


def main() -> int:
    """Print the table as JSON, one object per case, for a peer to run against its own client."""
    sys.stdout.write(json.dumps([row(case) for case in CASES], indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
