#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""THE promoted-project roster: which trees are held to the migrated corpus's gates.

⚑⚑ ONE LIST, BEHIND A 360-FINDING FILE, BLOCKING ITS OWN EXTENSION. `ROOTS` lived in
`scripts/check_scratch_independence.py`, and adding `substrate` to it — a one-line edit,
approved, admitting zero new census keys — was REFUSED, because the per-file gate has no
partial-credit path and that file cannot be made clean in one edit. The authority could not
be edited by the edit that would extend it.

⚑ THAT IS THE STRUCTURAL FACT THE WHOLE MIGRATION KEEPS HITTING: a dirty file is immutable,
including to the change that would clean it, so the only motion available is a NEW clean
module plus delegation. Three separate items ran into it before it was named (⟡corpus-repoint
at `_pycodemod_core`, ⟡substrate-in-population here, and the `pycodemod --types` route).

⚑⚑ AND THE ROSTER IS EXACTLY THE RIGHT SIZE TO CUT. `--importers` measures three consumers
and all three want `ROOTS`; only one also wants `_dep_sites`, which stays with the scanner
that owns it. So this is not a decomposition of the gate — it is the extraction of the one
declaration the gate PUBLISHES, from the file that merely happens to house it.

⚑⚑⚑ A HAND-COPIED ROSTER IS THE DEFECT THIS PREVENTS, AND IT HAS ALREADY HAPPENED ONCE.
`check_mypy_ratchet`'s own selftest carries the case — *"If someone hand-copies ROOTS into
this file, a future promotion silently escapes the type gate — the four-`agda_files()`
class"* — and `substrate/promote_agree.py` did exactly that, justified by a comment claiming
the authority could not be imported. It could: a `.pyi` types an unpackaged import. **The
copy was made because the fix looked impossible, which is worse than a knowing duplication —
nothing prompts a recheck.**

⚑ `substrate` IS IN THIS ROSTER AND WAS NOT IN THE OLD ONE (⟡substrate-in-population). It is
the promotion TARGET, so until now everything promoted into it landed BESIDE the gates rather
than inside them — a module left `scratch/` (ungated by design) and arrived somewhere no gate
looked. The migration's own success state was going unmeasured. Admitting it costs zero
census keys because the package was cleaned FIRST (⟡substrate-package-clean, 21 → 0); the
ordering was deliberate, since admitting a dirty tree to a paydown-only ratchet banks its
debt as baseline. MEASURED through `promote_agree --mypy`: population 334 → 343 files, census
1144 → 1144 keys.

⚑⚑⚑ TWO ROSTERS EXIST RIGHT NOW AND THEY DISAGREE — SAY SO RATHER THAN LET IT BE FOUND.
`scripts/check_scratch_independence.ROOTS` still reads `["jea", "el-atlas"]`, because that
file carries 360 findings and CANNOT BE EDITED to add the third entry. So until its consumers
move here, `substrate` is in the population this module declares and NOT in the one the gates
compute. That is a real divergence, not a transitional detail: a gate keyed on the old roster
does not yet see `substrate/`.

⚑ THE DIVERGENCE IS ACCEPTABLE ONLY BECAUSE IT IS DIRECTIONAL AND MEASURED. This roster is a
SUPERSET, the extra member admits zero keys, and every consumer that migrates gets strictly
more coverage rather than different coverage. A divergence that could REMOVE a tree from a
gate's scope would not be acceptable on the same terms, and this one must not be allowed to
become that: the migration direction is consumers moving HERE, never entries being removed to
make the two agree.
"""

from __future__ import annotations

# The promoted projects: trees held to every gate the migrated corpus is held to.
#
# ⚑ A TUPLE, NOT A LIST — the roster is a declaration, and a mutable one invites a consumer to
# `.append()` a tree into scope for the length of its own process. `check_mypy_ratchet` builds
# `list(ROOTS) + ["scripts"]`, which copies rather than mutates, and that must stay the shape.
ROOTS: tuple[str, ...] = ("jea", "el-atlas", "substrate")

# The gate layer itself, beside the promoted projects.
#
# ⚑ DERIVED HERE SO THE "+ scripts" IS SPELLED ONCE. `check_mypy_ratchet` computes this
# inline; so did `promote_agree`, differently, as a prefix tuple. Two spellings of one
# population is how a census silently answers about a different set than its sibling.
POPULATION: tuple[str, ...] = (*ROOTS, "scripts")
