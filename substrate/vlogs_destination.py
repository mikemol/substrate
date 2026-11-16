# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The refusal log's ingest URL, resolved BY NAME on every call (W38c).

⚑⚑ mtools' `mikemol.hooks.refusal_log.log_fallthrough` (row 5a) takes `destination` as a
REQUIRED argument and reads no environment: the `SUBSTRATE_VLOGS_URL` override and the
hard-coded `:30928` default both lived in substrate's `ratchet_log`, which is retiring. So the
destination is this repo's to resolve, and it resolves the way luthen's contract asks — by the
port's NAME (`victorialogs-http`), never a written-down address.

⚑ `None` MEANS UNRESOLVABLE, and that is what the emitter is told. It then reports the event as
not emitted (`Emission(emitted=False, why="no destination")`) rather than raising, which keeps
the property the old module guarded: a logging failure must never turn a refusal into a pass.

⚑ `log_fallthrough` HERE IS THE ADAPTER THE `scripts/ratchet.py` FACADE RE-EXPORTS, so its
callers (and the repos that adopt that facade by symlink) keep the four-argument spelling they
already use while the destination is supplied once, here.
"""

from __future__ import annotations

import subprocess

from mikemol.hooks import refusal_log

from substrate import vmagent_address

# luthen's name for the VictoriaLogs ingest port.
PORT = "victorialogs-http"

# The jsonline ingest path and the stream fields the refusal events carry.
INGEST = "/insert/jsonline?_stream_fields=tool,reason"


def destination() -> str | None:
    """Return the refusal-log ingest URL, or None when luthen cannot name the port.

    ⚑ `vmagent_address.DEFAULT_LUTHEN` IS USED HERE DELIBERATELY (regression fix, 2026-10-02):
    this function has no CLI entry point of its own to carry a `--luthen` override through
    (it is reached deep inside `ratchet_flags.check_argv`), so the one sanctioned default is
    the right call, not a parameter nothing above it could supply anyway.
    """
    try:
        host, port = vmagent_address.resolve(PORT, vmagent_address.DEFAULT_LUTHEN)
    except (vmagent_address.UnresolvedError, OSError, subprocess.TimeoutExpired):
        return None
    return f"http://{host}:{port}{INGEST}"


def log_fallthrough(
    tool: object, reason: object, typed: str = "", refusal: refusal_log.Refusal | None = None
) -> refusal_log.Emission:
    """Record a refused invocation at the by-name destination. Best-effort; never raises."""
    return refusal_log.log_fallthrough(tool, reason, typed, refusal, destination=destination())
