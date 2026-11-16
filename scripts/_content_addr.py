#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
# _content_addr.py — the single-source home for the content-address primitive the
# catalog tooling was copy-pasting (reuse_catalog.py, sppf_db.py). Surfaced by the
# reuse wedge (scratch/scripts_dedup.py: «_b64» |2 copies|). The id of an interned
# string IS base64(string) — a BIJECTIVE, reversible, collision-free content-address
# (NOT a hash); bounded because every interned string is bounded.
#
# ⚠ VERBATIM family representative. THE MODULE CARRIES NO DOCSTRING DELIBERATELY — the
# SPPF support is the identity the lift codemod matches, so adding one changes what that
# codemod sees.
#
# ⚑ AND NO EXEMPTION IS NEEDED FOR THAT, WHICH IS WORTH STATING BECAUSE THE OPPOSITE WAS
# ASSUMED. `D100` (undocumented-public-module) does not fire on a module whose first
# statement is a COMMENT block rather than a string — measured, this file is clean with
# no `pyproject.toml` entry. A first draft of this note claimed a path exemption existed;
# it did not, and the claim would have sent the next reader looking for one.
#
# ⚑ INVOKED AS `scripts/<tool>.py`, so a bare `from _content_addr import _b64` resolves
# via `sys.path[0]`. THIRTEEN CALL SITES ACROSS FIVE MODULES depend on that spelling
# (`--calls _b64`), so converting this provider to a package import breaks every one of
# them at once. The migration order is type-the-callee-THEN-name-it, and the naming step
# belongs with the consumers, not here — see the `[tool.setuptools]` note in
# pyproject.toml.
#
# ⚑⚑ AND A SECOND DEFINITION EXISTS AT `scratch/scope_store.py:69`, which is the exact
# defect this file was created to retire — one capability, two bodies, the `agda_files`
# shape. Recorded rather than fixed here: deduplicating it is a change to that module's
# consumers, not to this one.
import base64
import hashlib


def _b64(s: str | None) -> str:
    """Return the reversible base64 content-address of `s` (None reads as empty)."""
    return base64.b64encode(("" if s is None else s).encode("utf-8")).decode("ascii")


# ⚑⚑ THE SECOND PRIMITIVE, AND ITS WIDTH IS THE WHOLE REASON IT EXISTS (⑸, 2026-08-12).
# `_b64` is BIJECTIVE and therefore GROWS WITH WHAT IT NAMES — measured avg 16.4 / max 60
# characters over the sandbox's terms. On the LEADING COLUMN of the store's dominant
# indexes that is not free: MEASURED at 184k obs / 184k edge / 258k obs_node, the four
# `core_id`-led indexes go 25,722,880 B -> 61,562,880 B, a **2.39x**. On the live store
# those same indexes are 3.19 GB of a 4.01 GB total, at 5% of the corpus ingested.
#
# ⚑ `_addr` IS 8 BYTES OF SHA-256, BASE64, PADDING STRIPPED — **11 FIXED CHARACTERS**.
# Same measurement, same rows: 27,402,240 B, a **1.07x**. Three of the four indexes come
# out BYTE-IDENTICAL to the 4-character surrogate, because postgres page alignment
# absorbs the difference. So the width objection that motivated allocated ids does not
# reach this one.
#
# ⚑⚑ AND IT IS CONTENT-*DERIVED*, NOT CONTENT-*ADDRESSED* — the distinction is the
# collision. `_b64` is reversible and collision-free by construction; `_addr` is neither.
# What makes that admissible here is that the collision is **DETECTED, NEVER ASSUMED**:
# `terms` carries a PRIMARY KEY on `term_id` AND a UNIQUE index on `text`, and the
# interner inserts with `ON CONFLICT (text) DO NOTHING`. Two writers interning the SAME
# text conflict on the named arbiter and take the DO-NOTHING path; a genuine collision —
# DIFFERENT text, same 64 bits — finds no arbiter conflict, attempts the insert, and
# violates the PRIMARY KEY, which is not the named target. It RAISES. There is no path on
# which a collision is silently accepted.
#
# ⚑ WHY DERIVATION AT ALL, WHEN AN ALLOCATED ID ALSO WORKS: allocation is the thing that
# requires coordination between writers. A derived id is computed independently by every
# writer with no communication, so the same text yields the same handle and the insert is
# idempotent by construction — there is no race to handle because there is no allocation.
# Interning IS content-addressing; a leaf dictionary keyed by a counter was the odd one
# out.
#
# ⚑ AND THE ⓝ ARGUMENT AGAINST A DIGEST DOES NOT REACH A LEAF. It read: *"a
# content-complete node identity references its CHILDREN, and if a child is referenced by
# a key that carries its whole subtree then the parent's key carries the subtree twice
# over"* — an argument about RECURSIVE structure, correct for `node_id`, and applied to
# `terms`/`path_text` as well when it never touched them. `terms.text` has no children.
_ADDR_BYTES = 8


def _addr(s: str | None) -> str:
    """Return the 11-character content-DERIVED handle for an interned string.

    Collisions are detected by the store's PK+UNIQUE pair, never assumed away — see
    the block above.
    """
    h = hashlib.sha256(("" if s is None else s).encode("utf-8")).digest()[:_ADDR_BYTES]
    return base64.b64encode(h).decode("ascii").rstrip("=")
