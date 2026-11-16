# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Signatures for `scripts/check_scratch_independence.py` — now a SHIM over the package.

⚑⚑ A STUB IS WHAT MAKES AN UNPACKAGED MODULE IMPORTABLE-WITH-TYPES, AND IT WAS MISSED
ENTIRELY. `substrate/promote_agree.py` restated `ROOTS` as a hardcoded prefix tuple with a
comment claiming the authority "cannot be imported" — because reaching a module outside a
package yields `Any` and that `Any` propagates. That is true of the IMPLEMENTATION and false
as a conclusion: a `.pyi` supplies signatures independently of packaging, so the import is
typed even though the module is not. (Operator: *"isn't this what typing stubs are for?"*)

⚑⚑ AND THE FIRST DRAFT OF THIS FILE WAS WRONG IN TWO WAYS THAT `stubtest` CAUGHT IMMEDIATELY.
It declared `main(argv: list[str]) -> int` — invented from the shape of other gates rather
than read from this one, which took NO parameters — and it omitted `scan_file` entirely. The
first is the exact defect class the stub exists to prevent, committed inside the prevention:
**a stub is a CLAIM, and an unverified claim about types is worth less than no claim, because
it type-checks.**

⚑⚑⚑ AND THE MODULE THEN CHANGED SHAPE UNDER THE STUB, WHICH THE GATE CAUGHT THE SAME DAY
(2026-09-20, gate-G397). The origin was rewritten whole as a shim over five package modules:
`ROOTS` is now `substrate.promoted.ROOTS` — a TUPLE, the authority's declared form — where this
stub said `list[str]`; `scan_file` and `promotion_report` are gone (they live in
`substrate.scratch_refs` / `substrate.scratch_promotion`); `main` takes `argv`; and the shim
declares `__all__`. Every line below is read from the shim, and the stub is only as good as
⟡stub-authority, the gate that refused the stale one.

⚑ `_dep_sites` IS DECLARED THOUGH PRIVATE because `check_scratch_runtime` imports it by name;
the shim keeps it as a one-line delegator to `scratch_refs.dependency_sites` for exactly that
caller, and it retires with that caller's own drain.
"""

__all__ = ["ROOTS", "_dep_sites", "main"]

# The promoted projects — RE-EXPORTED from `substrate.promoted`, the authority; a tuple.
ROOTS: tuple[str, ...]

def _dep_sites(path: str) -> set[int]: ...
def main(argv: list[str]) -> int: ...
