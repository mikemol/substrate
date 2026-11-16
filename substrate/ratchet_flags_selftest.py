#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.ratchet_flags` — the argv contract every gate speaks through.

⚑ THE CASES LIVED INLINE IN `ratchet_flags.py` UNTIL ⟡n-split-the-tails. Operator: *"n-split
that crap. No more in-line/tail testing."* Inline cases cannot run without importing the module
under test, they inflate the file the per-file gate measures, and a module too dirty to edit
takes its own suite hostage — which is the same constraint that forced the n-split of `ratchet.py`
in the first place, arriving one layer down.

⚑ THE ARMS RUN WITH NO DESTINATION, because every refusal path calls `log_fallthrough` and a
selftest must not ship rows to the live stream — a test run would otherwise be indistinguishable
from real operator faults in the very census these events feed. The old redirect to a dead
endpoint (`ratchet_log.redirected`) has no counterpart in mtools' `refusal_log`, which keeps no
module state; the destination is now resolved per call by `vlogs_destination.destination`, so
patching THAT to `None` makes every event report not-emitted and ship nothing. It also keeps the
suite from asking luthen's resolver on every case.
"""

from __future__ import annotations

import sys
from unittest import mock

from substrate import vlogs_destination
from substrate.ratchet_flags import (
    TENANT_FLAGS,
    UNIVERSAL_FLAGS,
    arg_after,
    check_argv,
)


def _nowhere() -> str | None:
    """Stand in for the resolver: no destination, so nothing is emitted."""
    return None


def selftest() -> int:
    """Pin the argv contract."""
    cases: list[tuple[str, bool, str]] = []

    def ok(label: str, got: object, want: object) -> None:
        cases.append((label, got == want, f"{got!r} != {want!r}"))

    with mock.patch.object(vlogs_destination, "destination", _nowhere):
        # ⚑ THE MOTIVATING INCIDENT, AS A CASE. `--queit` returned rc=0 across five
        # gates: verbose-but-passing, with a flag none of them knew.
        ok("a typo'd flag is refused", check_argv(["g.py", "--queit"], {"--quiet"}, "p"), 2)
        ok("a declared flag passes", check_argv(["g.py", "--quiet"], {"--quiet"}, "p"), None)
        # ⚑ THE AUTHORITY'S OWN VOCABULARY IS KNOWN TO EVERY CALLER, so a gate that never
        # lists `--dry-run` must still accept it — the ten-call-site edit this retires.
        ok(
            "a universal flag needs no declaration",
            check_argv(["g.py", "--dry-run"], {"--quiet"}, "p"),
            None,
        )
        # ⚑ AND A TENANT FLAG IS NOT UNIVERSAL. A tool that opens no store accepting
        # `--live` is a flag that reads as meaningful and does nothing.
        ok(
            "an undeclared tenant flag is refused",
            check_argv(["g.py", "--live"], {"--quiet"}, "p"),
            2,
        )
        ok(
            "...and is accepted once the tool declares a store",
            check_argv(["g.py", "--live"], {"--quiet"}, "p", needs_store=True),
            None,
        )
        # ⚑ THE PRE-SLICED ARGV CASE, which made the guard INERT for one caller: a second
        # [1:] dropped the only flag, so nothing was examined and everything passed. A
        # guard that examines nothing passes everything.
        ok("a pre-sliced argv is still examined", check_argv(["--queit"], {"--quiet"}, "p"), 2)
        # ⚑ MUTATION AND TENANT CONTRACTS, refusing when unstated and when contradicted.
        ok(
            "an unstated mutation is refused",
            check_argv(["g.py"], {"--quiet"}, "p", mutates=True),
            2,
        )
        ok(
            "...and stated, passes",
            check_argv(["g.py", "--apply"], {"--quiet", "--apply"}, "p", mutates=True),
            None,
        )
        ok(
            "both mutation flags is a contradiction",
            check_argv(["g.py", "--apply", "--dry-run"], {"--quiet", "--apply"}, "p", mutates=True),
            2,
        )
        ok(
            "an unstated tenant is refused",
            check_argv(["g.py"], {"--quiet"}, "p", needs_store=True),
            2,
        )
        ok(
            "both tenant flags is a contradiction",
            check_argv(["g.py", "--live", "--sandbox"], {"--quiet"}, "p", needs_store=True),
            2,
        )

    # ⚑ `arg_after` — the capability that was four byte-identical private copies. The
    # absent-flag arm is the one NO COPY COULD HAVE PASSED: each called `.index`
    # unguarded, so a missing flag raised `ValueError` where the shared docstring
    # promised an empty string. It was unobservable because the copies read `sys.argv`,
    # a global no case can vary — CAPTIVE is exactly that defect.
    ok(
        "the value after a flag is returned",
        arg_after(["h.py", "--explain", "ls -l"], "--explain"),
        "ls -l",
    )
    ok(
        "an ABSENT flag yields empty, never ValueError",
        arg_after(["h.py", "--other", "x"], "--explain"),
        "",
    )
    ok("a flag in final position yields empty", arg_after(["h.py", "--explain"], "--explain"), "")
    # ⚑ THE DISCRIMINATOR AGAINST AN ALWAYS-EMPTY IMPLEMENTATION: a value that is itself
    # flag-shaped must come back verbatim, so "" cannot be mistaken for a pass.
    ok(
        "a flag-shaped value is returned verbatim",
        arg_after(["h.py", "--explain", "--weird"], "--explain"),
        "--weird",
    )
    # ⚑ argv[0] IS NOT A CANDIDATE. `_rest` drops a leading program path, so a caller
    # passing bare `sys.argv` reads the same as one passing a pre-sliced tail.
    ok("a pre-sliced argv reads identically", arg_after(["--explain", "ls"], "--explain"), "ls")

    cases.append(("the tenant vocabulary is declared", bool(TENANT_FLAGS), repr(TENANT_FLAGS)))
    cases.append(("universal flags are declared", bool(UNIVERSAL_FLAGS), repr(UNIVERSAL_FLAGS)))

    failed = [(n, d) for n, good, d in cases if not good]
    for n, d in failed:
        sys.stderr.write(f"  FAIL {n}: {d}\n")
    sys.stdout.write(f"ratchet_flags selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery):
# discovery keys on the literal `--selftest` appearing in the file, and ten promoted modules once
# ran correctly while being invisible to the runner.
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
