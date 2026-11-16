# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The one caller of luthen's endpoint resolver (W319: merged from two duplicate callers).

luthen publishes a resolver (`checks/endpoints_query.py`) over its own `endpoints.json`. The
contract this module honours: it prints ONE JSON line; success is exit 0 AND `state == "answered"`
with `host` a non-empty str and `port` an int (`as_of` optional); exit 1 is a refused query, exit 2
an unreadable declaration; any other state, garbage or empty stdout is a refusal that quotes what
came back. There is NEVER a fallback to loopback.

The runner is injected: `(argv) -> (exit code, stdout)`, a launch failure being exit -1. The real
launcher lives in `vmagent_address.run` (the one module whose subprocess call the lint config
sanctions); `store_endpoint` and `vmagent_address` are thin adapters over `resolve`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

#: The one sanctioned default checkout; callers with an entry point should take a flag instead.
DEFAULT_LUTHEN = Path.home() / "github" / "luthen-observability"

_ANSWERED = "answered"


class ResolverError(RuntimeError):
    """The owner could not be asked, or did not answer. Never a reason to guess an address."""


class NoAnswerError(ResolverError):
    """The resolver exited non-zero, printed nothing usable, or gave a non-answered state."""

    def __init__(self, name: str, code: int, state: object, reply: str = "") -> None:
        """Name the port, the exit code, the state and what came back."""
        self.code, self.state, self.reply = code, state, reply
        super().__init__(
            f"luthen's resolver did not answer for {name!r} (exit {code}, "
            f"state {state!r}, reply {reply.strip()!r}); refusing rather than guessing an address"
        )


class UnusableAnswerError(ResolverError):
    """The resolver answered, but without a usable host and port."""

    def __init__(self, record: dict[str, object]) -> None:
        """Quote the record the resolver returned."""
        self.record = record
        super().__init__(f"luthen's resolver answered without a usable host/port: {record!r}")


@dataclass(frozen=True, slots=True)
class Answer:
    """A port's address as its owner declares it today."""

    host: str
    port: int
    as_of: str


def argv(name: str, luthen: Path = DEFAULT_LUTHEN) -> list[str]:
    """Return the resolver invocation for `name`, by absolute path so no cwd is assumed."""
    return [
        str(luthen / ".venv" / "bin" / "python"),
        str(luthen / "checks" / "endpoints_query.py"),
        name,
        "--side",
        "host",
    ]


def record_of(text: str) -> dict[str, object]:
    """Return `text` as a JSON object, whole or as its first object LINE, or an empty record.

    ⚑ BOTH SHAPES ARE REAL. The resolver prints ONE line; `kubectl -o json` PRETTY-PRINTS over
    many. A line-only reader parsed nothing from kubectl (measured 2026-09-22).
    """
    try:
        whole: object = json.loads(text)
    except json.JSONDecodeError:
        whole = None
    if isinstance(whole, dict):
        return {str(k): v for k, v in whole.items()}
    for line in text.splitlines():
        try:
            got: object = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(got, dict):
            return {str(k): v for k, v in got.items()}
    return {}


def resolve(
    name: str,
    runner: Callable[[list[str]], tuple[int, str]],
    luthen: Path = DEFAULT_LUTHEN,
) -> Answer:
    """Ask luthen's resolver where `name` is. Refuse on anything but an answer."""
    code, out = runner(argv(name, luthen))
    rec = record_of(out)
    if code != 0 or rec.get("state") != _ANSWERED:
        raise NoAnswerError(name, code, rec.get("state"), out)
    host, port, as_of = rec.get("host"), rec.get("port"), rec.get("as_of")
    if not isinstance(host, str) or not host or not isinstance(port, int):
        raise UnusableAnswerError(rec)
    return Answer(host=host, port=port, as_of=as_of if isinstance(as_of, str) else "")
