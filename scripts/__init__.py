# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""scripts — the gates, hooks and generators the commit path runs.

⚑ THIS MARKER EXISTS BECAUSE A CHECKER ASKED FOR IT, NOT BECAUSE A LAYOUT WANTED IT.
`hook_pycheck --check-file` on itself reported one irreducible finding:

    error: Cannot find implementation or library stub for module named
    "hook_shellcheck"  [import-not-found]

`hook_pycheck` imports its sibling to reuse `_post_edit_content` and `_emit` rather
than restate them. Without a package marker that import is resolvable ONLY by the
`sys.path.insert` sitting two lines above it — which mypy cannot follow and which is
the very construct this migration retires. **The hook could not pass its own bar
until the directory it lives in was importable**, so the first artifact of the
package migration is also its first proof.

⚑⚑ `scripts/` IS PROMOTED WHOLE, UNLIKE `scratch/`, AND THE ASYMMETRY IS THE POINT.
Residence in `scratch/` IS the not-yet-promoted status (`check_scratch_independence`,
Λ8) — packaging it in place would make that gate's invariant unstatable, which is why
`substrate/` was created as a separate destination. `scripts/` carries no such
meaning: it is where the commit path's gates already live, permanently, and Λ8
explicitly does NOT guard it (*"scripts/ is NOT guarded … the invariant is
scratch-freedom, not isolation"*). So making it importable renames nothing and
promises nothing about migration status.

⚑ AND IT IS A MARKER, NOT A FACADE. No re-exports, no `__all__`, no convenience
imports. A package `__init__` that pulls its modules up into itself makes every
consumer pay for every module's imports, and turns a flat directory into a hidden
dependency knot — the opposite of what the decomposition is for. Modules stay
addressed by their own names.
"""
