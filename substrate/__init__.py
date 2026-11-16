# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""substrate — the tooling package, and the destination `scratch/` stages FOR.

⚑⚑⚑ THIS EXISTS BECAUSE THE PACKAGE WAS DECLARED AND NEVER POPULATED. `pyproject.toml`
names the project `substrate-tooling`, justifies sixteen dependencies across ~150 lines of
recorded incidents, and ends with `[tool.setuptools] py-modules = []` — **zero modules**.
So `uv sync` installs the dependencies and makes none of this repo's own code importable,
and every tool that needs another tool reaches it by mutating `sys.path` at runtime.

MEASURED 2026-08-28, `pycodemod --calls path.insert`: **556 call sites.** That number is
not a hygiene problem to sweep; it is the shape of an empty `py-modules` list. A module
that cannot be imported by name has exactly one way to be reached, and 556 authors each
found it independently.

⚑⚑ `scratch/` IS A STAGING AREA AND ITS RESIDENTS ARE NOT PROMOTED — that is what living
there MEANS (`check_scratch_independence`, Λ8). Packaging `scratch/` in place would have
cemented the temporary as permanent and made the gate's own invariant unstatable. The
operator's ruling (2026-08-28): *"create a different folder. we're trying to get stuff OUT
of scratch."*

⚑ AND FLAT, DELIBERATELY. No `substrate.agda` / `substrate.sql` / `substrate.gates`
sub-packages laid out in advance — *"n-split will create an emergent hierarchy"*. A
domain grouping chosen before the decomposition is a guess about where the seams are, and
the seams are what the split discovers. Modules land here flat and the hierarchy grows
from actual structure rather than from an author's taxonomy.

⚑ PROMOTION IS PER-MODULE AND GATED, NOT A DIRECTORY MOVE. `check_scratch_independence
--promotable scratch` REFUSES the wholesale case (measured: 209 live self-references, 224
type-census keys that would be added), and it is right to. The predicate a candidate must
meet is already written down in `promotion_report`:

    1. no live `scratch/` reference — this gate's own invariant, applied to it
    2. it ADDS NO CENSUS KEYS, `check_mypy_ratchet` first among them, because being
       annotated is part of what promotion already means

⚑ SO THE ORDER IS FORCED BY THE DEPENDENCY DAG, NOT BY PREFERENCE. Rule 1 means a module
importing something still in `scratch/` cannot move until that something has moved. The
leaves go first. `agda_lex` is the root of this DAG — 96 import sites across 60 files, and
it imports nothing but stdlib.
"""
