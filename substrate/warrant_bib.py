#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The worklist warrants' LOCATIONS and the project's own declaration — engine-free.

⚑⚑⚑ THE ENGINE HALF LIVES IN `substrate.warrant_records`, AND THE SPLIT WAS FORCED BY A BLOCKED
CONSUMER (gate-G209). This module used to `import paperkit.bib` at module scope and carry
`records`/`claim_of`/`tag` alongside the config reader. A peer measured that
`scratch/bibstruct.py` was then unreachable in EVERY mode without a paperkit venv — not one mode,
all of them — because the chain `bibstruct -> bibstruct_main -> bib_handlers -> warrant_bib ->
paperkit.bib` runs at MODULE LOAD. Both parties had reasoned about which modes touch the engine;
the answer was that importing the CLI at all does.

⚑⚑ SO THE SEAM IS THE ENGINE, NOT A FILE SIZE. `consumer_fields` reads the project's TOML with
the standard library and needs nothing installed. `records` calls paperkit's parser. Those are two
reachability classes that happened to share a module, and every consumer of the first was paying
the second's cost — invisibly, because the cost was an import three modules up a chain.

⚑⚑⚑ AND THE TOP-LEVEL IMPORT WAS KEPT RATHER THAN MADE LAZY, in the module that now owns it.
This file's prior docstring argued for module-scope against a recorded ruling — *"NOO. No sys.path
modification"* (operator, 2026-08-31) — and a declared dependency at module scope is what
paperkit's packaging exists to support. Deferring it into a function would have weakened that to
*declared where used* and hidden the dependency one level DEEPER. The split does the opposite: the
module that needs the engine says so in its own imports, and this one never pulls it.

⚑⚑⚑ THE GRAMMAR HAS ONE OWNER AND A PRIVATE COPY CANNOT BE SENSITIVE TO THE SAME CORRUPTIONS —
the reason the engine is used at all, kept here because it is why `warrant_records` exists.
`paperkit.bib` is the single source of truth for the warrant format, and its own docstring records
that it consolidated THREE parsers that had *"each re-derived the format and disagreed on which
fields survive."* A hand-rolled regex here was a fourth copy, and the cost was measured rather than
supposed: because that regex was not the engine's, the malformations it tested for were not the
ones the sandbox's mutations produce, so `keys-unique` graded `config/crash-sensitive only` — **it
was detecting its own module breaking rather than anything about the bib.**

⚑⚑ AND THE ENGINE ARRIVES BY INSTALLATION RATHER THAN BY ADJACENCY. The prior implementation
searched `$PAPERKIT` then `~/github/paperkit` and inserted whichever it found onto `sys.path`,
making the import work by rearranging the interpreter's search state instead of declaring what it
needs. That also settles a constraint the old code was protecting: a sandbox copies the PROJECT
and not the whole tree, so a witness depending on the surrounding layout stops running there —
which once turned two `behavioral` grades into `broken`.

⚑⚑⚑ AND THE PARSER MUST BE GIVEN THE PROJECT'S CONFIG, WHICH THIS MODULE WAS NOT DOING. The
worklist's `paper.toml` declares `consumer_fields = ["enables"]` — under forty-five lines arguing
for it — while every call passed a path alone, so the parser dropped `enables` on all fourteen
entries and warned about each, on every bib read in the repo. **A declaration nothing reads is
indistinguishable from one nobody made**, and the engine's warning was correct throughout: it
named the fix and pointed at a file that already contained it.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), which carries 1804 findings and
cannot be edited. What changed beyond the import: `Path` over `os.path`, typed returns, a
narrowed parser boundary, and exceptions instead of `SystemExit` — a library function does not
get to decide the whole process's fate from a place that cannot know the caller's context.
"""

from __future__ import annotations

from substrate import corpus

# The worklist project, whose config declares what its bib carries.
PROJECT = corpus.ROOT / "catalog" / "worklist"

# The warrants this project declares. ⚑ DERIVED FROM THE CORPUS ROOT, not from this file's own
# location: the module now lives in `substrate/` while the bib stays with the worklist.
BIB = PROJECT / "warrants.bib"

# Where the project states which non-engine fields its bib carries.
CONFIG = PROJECT / "paper.toml"

# ⚑⚑ `WarrantError` AND `consumer_fields` MOVED TO mtools (`mikemol.witness.warrant_bib`, W38),
# which takes the config as a REQUIRED argument. What remains here is the project's locations —
# themselves module-level root constants, owed under W36.


def speak() -> str:
    """Return what this module is, its entry points, and where the engine half went.

    ⚑ THE BIB AND CONFIG PATHS ARE READ FROM THE CONSTANTS. Typing them here would put a second
    spelling of the corpus-derived location into prose, which is the drift `BIB`'s own comment
    records — the module moved to `substrate/` while the bib stayed with the worklist.
    """
    return (
        "warrant_bib is a LIBRARY — the warrants' locations and the project's declaration.\n"
        "It is ENGINE-FREE: importing it does not require paperkit to be installed.\n"
        "\n"
        "  consumer_fields/WarrantError -> moved to mikemol.witness.warrant_bib (config required)\n"
        f"  BIB                    -> {BIB}\n"
        f"  CONFIG                   -> {CONFIG}\n"
        "\n"
        "⚑ THE ENGINE HALF IS `substrate.warrant_records` — records / claim_of / tag. It\n"
        "  imports paperkit at module scope, so a consumer without the engine installed can\n"
        "  reach everything here and nothing there. That split exists because a peer found\n"
        "  the CLI unreachable in EVERY mode when the two shared a module (gate-G209).\n"
        "\n"
        "⚑ IT IS NOT A WARRANT QUERY TOOL, AND THE NAME READS LIKE ONE. There is no lookup\n"
        "  mode here: a caller names a key in Python and handles WarrantError. Running this\n"
        "  bare, or with a key, would have to either fake a query or answer nothing — and\n"
        "  answering nothing is the silence this refusal replaces.\n"
        "\n"
        "usage: warrant_bib.py --selftest\n"
    )


# ⚑ `--selftest` DELEGATES TO THE SIBLING SUITE (⟡selftest-discovery); ANY other invocation
# REFUSES with exit 2 rather than exiting 0 in silence (⟡the-three-silent). A bare run printed
# nothing, which a reader cannot distinguish from a warrant lookup that found no match — and
# this module's whole subject is warrants a caller looks up by key.
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        # ⚑⚑ RESOLVED BY NAME AT RUNTIME, NOT BY A TYPE-CHECKED IMPORT, AND A DEADLOCK FORCED IT
        # (gate-G210). The per-file gate runs mypy package-wide, so a direct import here made
        # this module unwritable while its suite was absent AND the suite unwritable while this
        # module named it — each half refusing the write that would fix the other. A runtime
        # lookup breaks the cycle without weakening what a reader depends on: the delegation is a
        # `__main__` convenience, and its failure mode is a clear refusal at the one moment
        # someone runs `--selftest`, not a silent gap.
        #
        # ⚑ NARROWED THROUGH A `Protocol`, because a dynamically imported module is `Any` and
        # `hasattr` does not narrow it — measured, on the write before this one. The protocol
        # states the single name this delegation reads, which is also the honest statement of
        # what a rename would break.
        import importlib
        from typing import Protocol, runtime_checkable

        @runtime_checkable
        class _Suite(Protocol):
            """The one name this delegation reads off the suite module."""

            def selftest(self) -> int:
                """Run the suite and return an exit code."""
                ...

        found: object = importlib.import_module("substrate.warrant_bib_selftest")
        sys.exit(found.selftest() if isinstance(found, _Suite) else 2)
    sys.stderr.write(speak())
    sys.exit(2)
