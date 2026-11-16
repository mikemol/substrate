#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""check_ban_ratchet.py — the import ban as a GATE rather than prose.

THE BAN. A `Substrate.*` import may not carry `using`, `renaming`, `hiding`, or `as`. You may
decline to import something; you may not FILTER, RENAME, or ALIAS what you do import. The repair
is always the same: SPLIT UPSTREAM so the module you import holds exactly what you need, and bind
names at their OWNER.

WHY IT IS A GATE. This ban lived in prose, which means it was enforced by attention — and it
leaked, to five figures of accumulated directives. That is not a hygiene problem but a
MECHANIZATION one: every directive defeats the splitting machinery. Splitting a module whose
consumers alias it, or rename out of it, silently unbinds those use sites, because the rewrite
cannot know which leaf now owns the name. Each alias is a place the split has to stop. So the ban
is the PRECONDITION that unblocks upstream splitting, which is the lever that brings the
per-module elaboration peak under the cap.

THE FORM. A "no ANY" ban cannot be enforced as a cliff against the existing population, so it is a
PAYDOWN-ONLY RATCHET over a materialized census — the repo's standing pattern. A NEW directive is
REFUSED, a removed one AUTO-LOWERS the baseline, and the target is 0.

NOTE — the apparent conflict, and its resolution: RENAME UPSTREAM. `check_import_shape.py`
REQUIRES `renaming (Name to Name⟦shape⟧)` on a genuinely-ambiguous bare import — it mandates what
this gate forbids. The resolution is not to weaken either gate but to move the disambiguation
where it belongs: rename at the DEFINITION, so the name is globally unique and no import site has
to say which one it meant. Renaming at the import is a per-consumer patch over an upstream
collision — it multiplies with the consumer count, and each instance is a place the splitting
machinery has to stop. Both gates reach 0 together, via rename-upstream + split-upstream.

⚑⚑⚑ THE CENSUS AND THE WALK NOW COME FROM THE PACKAGE, AND THAT IS THE POINT (gate-F72, F73, F74).
This file previously carried a private `_span_end` that reached `agda_lex._depth_after` and
`agda_lex._continues` — flagged three times as `SLF001` — one line below importing the module that
exported `span_end` publicly, under a comment reading *"span via the ONE authority, not
re-derived"* while re-deriving it. The census is now `substrate.ban_census`, whose key set was
proved IDENTICAL to this gate's over the whole tree before the swap, and the walk is
`substrate.agda_walk`, proved to enumerate the same population.

⚑⚑ THE SWAP WAS SAFE ONLY BECAUSE BOTH WERE DIFFERENCED FIRST. A mis-parsing gate launders its own
bug into a paydown-only baseline, where it can never be un-banked — so "the code looks equivalent"
is not the standard. Set equality over the live corpus is, and both suites assert it with a
positive control so agreement cannot be vacuous.

⚑ WHAT STAYS HERE: the baseline path, the argv contract, and the ratchet call. Those are the
application — where the census is a pure function of text, and the walk of a root.
"""

from __future__ import annotations

import sys
from pathlib import Path

from scripts import ratchet
from substrate import agda_walk, ban_census

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "agda" / "Substrate"

# ⚑⚑⚑ `BASELINE` IS A `str`, AND MAKING IT A `Path` SILENTLY BROKE A READER (gate-F76). The gate
# itself was unaffected — `main` stringifies it — but `ratchet_census.baseline_path` narrows the
# attribute with `isinstance(declared, str)` and reports a non-string as NO baseline. So
# `commit_refusal` read the baseline as EMPTY and rendered `7411 added of 7411 held`, i.e. every
# key as a new offender, while the gate's own output was byte-identical across the swap.
#
# ⚑⚑ THE NARROWING IS CORRECT AND ITS DOCSTRING SAYS WHY: a gate declaring a `BASELINE` that is
# not a path string is reported as having none *"rather than reaching the filesystem with
# whatever it declared."* This is a DECLARED INTERFACE between a gate and the readers that
# census it, and a type change to a module-level constant is an interface change.
BASELINE = str(ROOT / "scripts" / "ban_ratchet_baseline.txt")


def census() -> set[str]:
    """Return the SET of `<relpath>::<imported module>::<directive>` over the whole tree.

    ⚑ THE PATHS ARE REPO-RELATIVE because that is what the committed baseline holds. An absolute
    path would read as a new offender for every key at once, and a paydown-only ratchet would
    then refuse every commit while defending a phantom population forever.
    """
    pairs = [(str(Path(path).relative_to(ROOT)), text) for path, text in agda_walk.sources(SRC)]
    return ban_census.census(pairs)


def main() -> int:
    """Run the ratchet over the ban census."""
    rc = ratchet.check_argv(sys.argv, {"--quiet", "--list"}, "check_ban_ratchet")
    if rc is not None:
        return int(rc)
    return int(
        ratchet.set_ratchet(
            census(),
            BASELINE,
            "ban-ratchet",
            "--quiet" in sys.argv,
            list_keys="--list" in sys.argv,
            noun="banned import directive(s) (using/renaming/hiding/as) on Substrate imports",
            refuse_hint="A Substrate import may not FILTER, RENAME or ALIAS. "
            "SPLIT UPSTREAM so the imported module holds what you need, and bind "
            "at the OWNER. Every alias is a place the splitting machinery has to stop.",
        )
    )


if __name__ == "__main__":
    sys.exit(main())
