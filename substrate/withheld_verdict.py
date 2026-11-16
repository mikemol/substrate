#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Render a WITHHELD verdict: what could not be measured, and ONLY what was observed.

Extracted from `ratchet.py` as part of ⟡ratchet-seams. Refusing to answer is a distinct
responsibility from ratcheting a census — it belongs to any instrument that can come up
empty, which is most of them.

⚑⚑ THE WITHHOLD IS THE VALUABLE HALF; THE APPENDED CAUSE IS WHERE FABRICATION ENTERS.
Measured across three instruments 2026-08-21, each correctly refusing to answer and then
explaining the gap with something it never observed:

  · `schema.py --headroom` printed *"the data directory is not a local path, so the
    server is on another host or in a container … ask on the server's host"*. What it
    OBSERVED is that the server did not report `data_directory` (the role lacks
    `pg_read_all_settings`). The DSN in its own hand is a UNIX SOCKET — proof the server
    is local — and the volume sat one directory over. It sent the reader to "the server's
    host", which was this one.
  · `pycodemod --calls <name>` prints "⚑ DEAD CAPABILITY — defined and never called" when
    it means "not visible from the scope you asked about". Two live instances
    (`store.tenant` with 8 callers, `_pycodemod_census.aliases` with 1) — and this repo
    DELETES on `--dead`.
  · A roster lookup returned no peer by a name, and the reader reported "that session
    ended" — a fact about the CHANNEL asserted as a fact about the world. The session was
    running and holding files.

⚑ THE TOOLKIT MOSTLY GETS THIS RIGHT — 80 sites already say "a fact about the QUERY, not
about the code", and the good ones state a CHECKABLE cause ("none of these paths exist at
<ref>") rather than an inferred one. This helper exists so the distinction is structural
rather than remembered.

⚑ THE CASES LIVE IN `withheld_verdict_selftest.py`, NOT IN THIS FILE'S TAIL
(⟡n-split-the-tails). They were inline until a coverage census counted that as a convention
rather than as debt; operator: *"n-split that crap. No more in-line/tail testing."* Inline cases
cannot run without importing the module under test, and a module too dirty to edit takes its own
suite hostage.
"""

from __future__ import annotations


def withheld(label: str, question: str, measured: str, *, cause: str | None = None) -> str:
    """Render the verdict: `measured` is what the instrument SAW; `cause` is optional.

    ⚑ `cause` IS OPTIONAL AND, WHEN GIVEN, MUST BE SOMETHING THE INSTRUMENT CAN POINT AT.
    A caller with only a hypothesis passes none, and the message says so instead of
    inventing one. That asymmetry is the whole design: the observed half is cheap and
    always true, the causal half is where every one of the three measured failures above
    went wrong.
    """
    out = [f"⚑ {label}: {question} — WITHHELD.", f"  observed: {measured}"]
    if cause:
        out.append(f"  cause:    {cause}")
    else:
        # ⚑ NAMING THE ABSENCE OF A CAUSE IS THE POINT. A withhold with no explanation
        # reads as incomplete and invites the next reader to supply one; saying the cause
        # is unmeasured is what stops that being filled in with a guess.
        out.append(
            "  cause:    NOT MEASURED — this instrument cannot see why, and a "
            "guess here would\n            be the fabrication the withhold "
            "exists to avoid."
        )
    return "\n".join(out)
