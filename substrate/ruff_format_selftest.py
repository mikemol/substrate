#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.ruff_format` — run ruff, never imitate it, and raise when it fails.

⚑⚑ THE LOAD-BEARING CASE IS THE FAILURE. A formatter that handed back its input on error would
give a generator unformatted text that LOOKS processed, and the generator's byte round-trip would
then fail somewhere else, far from the cause. So unparseable source must RAISE, and a case says so.

⚑ AND IDEMPOTENCE IS ASSERTED, because a generator runs this on every `--compile`: formatting
already-formatted text must change nothing, or the committed file churns on every regeneration.
"""

from __future__ import annotations

import sys

from substrate import ruff_format

# Source ruff would change: single quotes and cramped spacing.
_RAW = "x = {'a':1,'b':2}\n"

# What ruff writes for it under this project's config.
_FORMATTED = 'x = {"a": 1, "b": 2}\n'

# Source ruff cannot parse.
_BROKEN = "def (:\n"


def _raises(text: str) -> bool:
    """Report whether formatting `text` raised FormatError."""
    try:
        ruff_format.format_source(text, "probe.py")
    except ruff_format.FormatError:
        return True
    return False


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    once = ruff_format.format_source(_RAW, "probe.py")
    twice = ruff_format.format_source(once, "probe.py")
    return [
        ("source is formatted as ruff writes it", once == _FORMATTED),
        ("formatting formatted source changes nothing", twice == once),
        ("unparseable source RAISES rather than returning its input", _raises(_BROKEN)),
    ]


def selftest() -> int:
    """Run every case, reporting failures by name, and return an exit code."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"ruff-format selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 1)
