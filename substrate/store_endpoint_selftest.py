# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.store_endpoint` — answer or refuse, never guess; names, never values.

⚑ EVERY CASE RUNS ON A FIXTURE RUNNER. A suite that reached the real resolver or the cluster
would go red when luthen moved the store — reporting the owner's change as our defect — and a
suite that read a real Secret would put a credential into a test log.
"""

from __future__ import annotations

import base64
import json
import sys
from typing import TYPE_CHECKING

from substrate import store_endpoint as se

if TYPE_CHECKING:
    from collections.abc import Callable

_ANSWER = json.dumps(
    {
        "state": "answered",
        "name": "postgres",
        "side": "host",
        "host": "postgres.example.svc",
        "port": 5432,
        "address": "postgres.example.svc:5432",
        "as_of": "2026-09-22T00:00:00Z",
    }
)
_FIXTURE_VALUE = "fixture-not-real"
_OBJECT = json.dumps(
    {
        "data": {
            se.DATA_KEY: base64.b64encode(_FIXTURE_VALUE.encode()).decode(),
            "username": base64.b64encode(b"substrate").decode(),
        }
    }
)


def _fixed(code: int, out: str) -> Callable[[list[str]], tuple[int, str]]:
    """Return a runner that always answers `(code, out)`."""

    def runner(_argv: list[str]) -> tuple[int, str]:
        return code, out

    return runner


def _refuses(call: Callable[[], object], kind: type[BaseException]) -> bool:
    """Report whether `call` raises `kind` (or a subclass)."""
    try:
        call()
    except kind:
        return True
    return False


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    ep = se.resolve(_fixed(0, _ANSWER))
    check(
        "an answered record resolves to its host and port",
        passed=(ep.host, ep.port) == ("postgres.example.svc", 5432),
    )
    check("and carries the resolver's as_of", passed=ep.as_of == "2026-09-22T00:00:00Z")

    # ⚑⚑ THE REFUSALS ARE THE POINT: every path that is not an answer raises, none returns a
    # loopback default — the defect this module exists to retire.
    check(
        "a refused query (exit 1) raises, not a default",
        passed=_refuses(
            lambda: se.resolve(_fixed(1, json.dumps({"state": "refused"}))), se.NoAnswerError
        ),
    )
    check(
        "an unreadable declaration (exit 2) raises",
        passed=_refuses(
            lambda: se.resolve(_fixed(2, json.dumps({"state": "unreadable"}))), se.NoAnswerError
        ),
    )
    check(
        "exit 0 with a non-answered state still raises",
        passed=_refuses(
            lambda: se.resolve(_fixed(0, json.dumps({"state": "refused"}))), se.NoAnswerError
        ),
    )
    check(
        "an answer without a port raises",
        passed=_refuses(
            lambda: se.resolve(_fixed(0, json.dumps({"state": "answered", "host": "h"}))),
            se.UnusableAnswerError,
        ),
    )
    check(
        "a launch failure (exit -1, no JSON) raises",
        passed=_refuses(lambda: se.resolve(_fixed(-1, "boom")), se.NoAnswerError),
    )
    check(
        "the resolver is invoked by absolute path, with no shell",
        passed=se.resolve_argv()[1].startswith("/") and "sh" not in se.resolve_argv()[0],
    )

    # ⚑ THE CREDENTIAL SOURCE IS LAZY: building it reads nothing.
    calls: list[list[str]] = []

    def counting(argv: list[str]) -> tuple[int, str]:
        calls.append(argv)
        return 0, _OBJECT

    source = se.credential(se.LIVE, runner=counting)
    check("building a credential source reads nothing", passed=not calls)
    check("calling it decodes the named key", passed=source() == _FIXTURE_VALUE and len(calls) == 1)
    check(
        "each call re-reads, so a rotation is followed",
        passed=source() == _FIXTURE_VALUE and len(calls) == 2,
    )  # noqa: PLR2004 - two calls

    # ⚑⚑ A MISSING KEY NAMES THE KEYS PRESENT AND NEVER A VALUE.
    missing = se.credential(se.LIVE, key="pgpass", runner=_fixed(0, _OBJECT))
    try:
        missing()
        said = ""
    except se.MissingKeyError as exc:
        said = str(exc)
    check(
        "a missing key refuses and lists the keys present",
        passed=se.DATA_KEY in said and "username" in said,
    )
    check("and the refusal carries no value", passed=_FIXTURE_VALUE not in said and bool(said))
    check(
        "an unreadable object refuses",
        passed=_refuses(se.credential(se.SANDBOX, runner=_fixed(1, "")), se.UnreadableObjectError),
    )
    # ⚑⚑ THE LIVE SHAPE: kubectl pretty-prints. A fixture written on one line hid that the
    # reader parsed nothing from the real object (first live run, 2026-09-22).
    pretty = json.dumps(json.loads(_OBJECT), indent=4)
    check(
        "a pretty-printed (multi-line) object is read",
        passed=se.data_keys(se.LIVE, runner=_fixed(0, pretty)) == sorted([se.DATA_KEY, "username"]),
    )
    check(
        "data_keys lists names only",
        passed=se.data_keys(se.LIVE, runner=_fixed(0, _OBJECT))
        == sorted([se.DATA_KEY, "username"]),
    )
    # ⚑ k8s object names cannot carry `_`: the sandbox tenant's object is hyphenated while its
    # role and database keep the underscore (luthen, 2026-09-22).
    check(
        "the sandbox object name is hyphenated",
        passed=se.object_name(se.SANDBOX) == "pg-tenant-substrate-sandbox",
    )
    check(
        "and the object read uses that name",
        passed="pg-tenant-substrate-sandbox " in se.object_argv(se.SANDBOX)[-1]
        and "substrate_sandbox" not in se.object_argv(se.SANDBOX)[-1],
    )
    check(
        "the live object name is unchanged", passed=se.object_name(se.LIVE) == "pg-tenant-substrate"
    )
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"store-endpoint selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(0 if ("--selftest" in sys.argv or len(sys.argv) == 1) and selftest() else 1)
