#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read the harness's untyped payload, and report whether the hook is armed.

⚑ A HOOK THAT MIS-READS ITS OWN INPUT RENDERS A VERDICT ABOUT SOMETHING OTHER THAN
WHAT RAN, which is why this is its own responsibility: it changes when the HARNESS's
contract changes, not when a checker, a message or a verdict does.
"""

from __future__ import annotations

import os


def as_record(value: object) -> dict[str, object]:
    """Return `value` as a string-keyed record, or an empty one if not a mapping.

    ⚑ `object` IS THE HONEST TYPE OF AN UNTRUSTED VALUE; `Any` IS THE DISHONEST ONE
    (linux-sources, 2026-08-30). The payload arrives as untyped JSON; rebuilding the
    mapping with a declared return type forces its values to `object`, and every read
    is then narrowed with a real runtime `isinstance` at the use site — a check, not
    an assertion. `isinstance(x, dict)` alone narrows to `dict[Any, Any]`, so every
    read through it inherits the `Any` the house bar exists to refuse.
    """
    if not isinstance(value, dict):
        return {}
    return {str(k): v for k, v in value.items()}


def text_of(value: object) -> str:
    """Return `value` when it is a string, else an empty string."""
    return value if isinstance(value, str) else ""


def armed() -> bool:
    """Report whether this hook is set to DENY — own switch first, then the shared one.

    ⚑ ARMED ON THE COMMAND LINE, NOT BY THE ENV BLOCK ALONE. A session already running
    when `settings.json` changes never re-reads it, so a hook armed only in the env
    block keeps exiting 0 — detecting every violation and reporting none, reading as
    armed in review and off in fact. Set `PYCHECK_HOOK_BLOCK=1` inline in the command
    string. Both peers volunteered this trap independently.
    """
    own = os.environ.get("PYCHECK_HOOK_BLOCK")
    if own is not None:
        return own == "1"
    return os.environ.get("STRUCT_HOOK_BLOCK") == "1"
