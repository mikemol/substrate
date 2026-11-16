# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.store_launch` — the patch lands on the module, and nothing connects.

⚑ EVERY CASE RUNS ON A STAND-IN MODULE, NEVER ON `jea.metalanguage.store`. The subject is what
`patch` writes; asserting it against the real store would need a live tenant and would mutate a
module other suites import.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from substrate import store_endpoint, store_launch

if TYPE_CHECKING:
    from collections.abc import Callable

_RESOLVED_HOST = "resolved.fixture"
_RESOLVED_PORT = 46432
_USAGE_CODE = 2


def _nothing() -> str | None:
    """Stand in for the old credential source."""
    return None


class _StandIn:
    """A module-shaped stand-in carrying the old, dead wiring; records what it is asked to do.

    ⚑ Its members are ASSIGNED CALLABLES annotated with the Protocol's EXACT types: the module
    attributes `patch` replaces are settable, and a settable Protocol member is invariant — an
    inferred function type (named parameters) does not satisfy a declared positional Callable.
    """

    def __init__(self) -> None:
        """Start with the retired listener, no credentials, and an empty call log."""
        calls: list[str] = []
        self.calls = calls

        def old_connect(reset: bool) -> object:  # noqa: FBT001 - the original's signature
            calls.append(f"old-connect reset={reset}")
            return None

        def sandbox_reset(con: object) -> None:
            del con
            calls.append("reset")

        def lens_record(a: str, b: str, c: str, d: str) -> None:
            del a, b, c, d
            calls.append("lens")

        self.PG_HOST: str = "127.0.0.1"
        self.PG_PORT: int = 30432
        self.PG_CREDENTIAL: Callable[[], str | None] = _nothing
        self.PG_SANDBOX_CREDENTIAL: Callable[[], str | None] = _nothing
        self.sandbox_connect: Callable[[bool], object] = old_connect
        self.sandbox_reset: Callable[[object], None] = sandbox_reset
        self._lens_record: Callable[[str, str, str, str], None] = lens_record


def _bare_store_origin() -> str | None:
    """Prepare the path for an `sppf_db`-shaped script, then locate the BARE `store`.

    ⚑⚑ THE t86 REGRESSION: a script that puts `jea/metalanguage` on its OWN path left the bare
    `store` unresolvable at patch time, so the patch skipped it and the script imported an
    UNPATCHED copy that dialled 127.0.0.1. `find_spec` locates without importing, so no module
    is loaded and nothing connects; `sys.path` is restored whatever happens.
    """
    saved = list(sys.path)
    try:
        home = store_launch.STORE_HOME
        sys.path[:] = [p for p in sys.path if Path(p).resolve() != home]
        store_launch.prepare_path(home.parent.parent / "scripts" / "sppf_db.py")
        spec = importlib.util.find_spec(store_launch.BARE)
        return None if spec is None else spec.origin
    finally:
        sys.path[:] = saved


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    mod = _StandIn()
    old_connect = mod.sandbox_connect
    ep = store_endpoint.Endpoint(host=_RESOLVED_HOST, port=_RESOLVED_PORT, as_of="fixture")
    store_launch.patch(mod, ep)
    check("the host is the resolver's, not 127.0.0.1", passed=mod.PG_HOST == _RESOLVED_HOST)
    check(
        "the port is the resolver's, not the retired NodePort", passed=mod.PG_PORT == _RESOLVED_PORT
    )
    check("sandbox_connect is REPLACED", passed=mod.sandbox_connect is not old_connect)
    check(
        "both credential sources are rebound",
        passed=mod.PG_CREDENTIAL is not _nothing and mod.PG_SANDBOX_CREDENTIAL is not _nothing,
    )
    # ⚑ The credential sources are LAZY and the connector was not called: patching read no
    # Secret and opened no connection.
    check("patching read nothing and connected to nothing", passed=mod.calls == [])
    check(
        "a non-.py operand is refused with usage, before any patch",
        passed=store_launch.main(["not-a-script"]) == _USAGE_CODE,
    )
    check("no operand is refused with usage", passed=store_launch.main([]) == _USAGE_CODE)
    origin = _bare_store_origin()
    check(
        "the bare `store` resolves to jea/metalanguage/store.py after prepare_path",
        passed=origin is not None
        and Path(origin).resolve() == store_launch.STORE_HOME / "store.py",
    )
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"store-launch selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(0 if ("--selftest" in sys.argv or len(sys.argv) == 1) and selftest() else 1)
