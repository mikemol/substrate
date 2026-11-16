#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Run a reader with the thing it reads kept quiet — so the REPORT is what reaches the terminal.

⚑⚑⚑ A CENSUS OVER NOISY AUTHORITIES IS UNREADABLE, AND AN UNREADABLE REPORT IS AN UNCONSULTED
ONE. Measured: `commit_refusal` censuses gates by importing them and calling `census()`, and
several of those print as they work — `import-shape: 4 genuinely-ambiguous names`,
`decl-shape-tag: 0 untagged`, and `law_motif_apex` emitting a scan of every retraction,
involution and idempotent in the Agda tree. The twelve-line verdict table arrived buried under
nineteen thousand characters of someone else's output.

⚑⚑ THAT IS NOT COSMETIC. The whole premise of the reader is that an operator consults it BEFORE
committing; a tool whose answer must be excavated is one nobody runs twice. The noise is also
not the authorities' fault — each is correct to narrate when invoked directly. The defect is
only in COMPOSING them, so the fix belongs at the composition, not in fifteen other files.

⚑ IT CAPTURES, IT DOES NOT DISCARD. The captured text is RETURNED alongside the value, because
throwing it away would make a genuine error message from an authority vanish — trading a noisy
report for a silent one, which is the worse failure. The caller decides what to surface.

⚑ STDERR IS LEFT ALONE, DELIBERATELY. A traceback or a warning during a read is information the
operator needs immediately, and it is never the routine chatter this exists to suppress.
"""

from __future__ import annotations

import contextlib
import io
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


def quietly[T](work: Callable[[], T]) -> tuple[T, str]:
    """Run `work` with stdout captured, returning its value and whatever it printed.

    ⚑ THE VALUE COMES BACK UNCHANGED. This wraps the CALL, not the result, so a caller cannot
    accidentally start depending on the capture — it stays a presentation concern.
    """
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        got = work()
    return got, buffer.getvalue()
