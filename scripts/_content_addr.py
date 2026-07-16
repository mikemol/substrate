#!/usr/bin/env python3
# _content_addr.py — the single-source home for the content-address primitive the catalog tooling was
# copy-pasting (reuse_catalog.py, sppf_db.py). Surfaced by the reuse wedge (scratch/scripts_dedup.py:
# «_b64» |2 copies|). The id of an interned string IS base64(string) — a BIJECTIVE, reversible,
# collision-free content-address (NOT a hash); bounded because every interned string is bounded.
#
# ⚠ VERBATIM family representative (no docstring — the SPPF support is the identity the lift codemod matches).
# Invoked as `scripts/<tool>.py`, so a bare `from _content_addr import _b64` resolves (scripts/ = sys.path[0]).
import base64


def _b64(s): return base64.b64encode(("" if s is None else s).encode("utf-8")).decode("ascii")
