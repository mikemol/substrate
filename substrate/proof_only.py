# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Modules whose ONLY consumer is their own proof — permanently green, permanently inert.

⚑⚑⚑ A GREEN THAT CANNOT BE WRONG BECAUSE NOTHING CALLS IT. A module imported only by its own
selftest passes every arm, regresses never, and is falsifiable by no production path. The
verdict is real and it is about nothing — the same family as a cache replay standing in for a
measurement, or a linter reporting zero findings because it could not run. **Absence of a
failure is not evidence of use.**

⚑⚑ THE MEASURED INSTANCE THAT MOTIVATED THIS. `substrate/md_hkey` folds smart typography and
exposes `agree(raw, rendered)` — precisely the predicate a live heading-matching defect needed
(gate-G297). `attr_reads md_hkey.agree` reported 16 reads in 1 of 1593 files, EVERY one inside
`md_hkey_selftest`. The repair existed, tested, in the same tree as the defect, reachable by
nothing, while the defective reader kept calling a function that could not answer. A peer
named the class: *an instrument whose only caller is its own proof.*

⚑⚑ SO THIS IS NOT A DEAD-CODE CENSUS, AND THE DIFFERENCE IS THE POINT. A module nothing imports
at all is visibly unused and reads as such. A module with a green suite and no other consumer
reads as WORKING — it has arms, they pass, a runner counts them — and that is what makes it
survive review. The suite is what disguises the inertness, so the suite is what this keys on.

⚑ WHAT IT DOES NOT CLAIM. A member of this population is not thereby dead: it may be a
deliberate library awaiting a consumer, a capability published for adopters, or a module whose
callers this reader cannot resolve. **It is a QUESTION — why does nothing use this? — not a
verdict**, and the report says so rather than implying a deletion.

⚑⚑ AND IT CONSUMES `module_importers` RATHER THAN RE-DERIVING IMPORTS. That reader already
states the shapes it cannot resolve, and a second implementation here would either repeat those
blind spots or invent different ones — two readers disagreeing about one question, which is the
defect this whole arc has been paying down. Inheriting its bounds means inheriting its honesty
about them.

⚑⚑⚑ AND IT ASKS THAT READER **ONCE**, WHICH IT DID NOT AT FIRST. The first cut called `sites`
per candidate, and `sites` parses the whole corpus per question — ~700 candidates over 1593
files, two runs killed at 120 seconds (gate-G301). A census for modules nothing calls, whose
own only consumer would be a run nobody completes. `all_sites` was added to the owning reader
so the parse happens once and every candidate is answered from it.
"""

from __future__ import annotations

import sys
from typing import NamedTuple

from substrate import module_importers

#: The mode this module has, named so a bare run prints the spelling a reader needs next.
MODE = "--proof-only"

#: What a bare or unknown invocation exits with — usage, not a verdict about the tree.
USAGE_EXIT = 2

#: How a suite names itself here. ⚑ ONE CONVENTION, READ FROM THE TREE'S OWN PRACTICE: every
#: suite in this package is `<module>_selftest.py`, which is what `run_selftests` discovers on.
SUITE = "_selftest"


class Module(NamedTuple):
    """One module, its consumers, and whether any of them is something other than its proof."""

    dotted: str
    consumers: tuple[str, ...]
    suite_only: tuple[str, ...]

    def inert(self) -> bool:
        """Report whether every consumer is this module's own proof.

        ⚑ A MODULE WITH NO CONSUMERS AT ALL IS NOT THIS CLASS. That one is visibly unused and
        reads as such; this population is the one that reads as WORKING because a suite is
        green. Requiring at least one suite consumer is what keeps the two separate.
        """
        return bool(self.suite_only) and len(self.suite_only) == len(self.consumers)

    def why(self) -> str:
        """Return a one-line account of this module's consumer population."""
        if self.inert():
            return (
                f"{self.dotted}  PROOF-ONLY — {len(self.consumers)} consumer(s), "
                f"all its own suite: {', '.join(self.suite_only)}"
            )
        other = [c for c in self.consumers if c not in self.suite_only]
        return f"{self.dotted}  used by {len(other)} non-suite consumer(s): {', '.join(other)}"


def is_suite_of(consumer: str, dotted: str) -> bool:
    """Report whether `consumer` is the suite belonging to `dotted`.

    ⚑⚑ IT MUST BE *THIS* MODULE'S SUITE, NOT ANY SUITE. A module used by some OTHER module's
    selftest has a real consumer — the fixture is exercising it as a dependency, which is
    evidence of use. Collapsing the two would report a genuinely-used helper as inert, and the
    report would then be wrong in the direction that generates deletion work.
    """
    leaf = dotted.rsplit(".", 1)[-1]
    stem = consumer.removesuffix(".py").rsplit("/", 1)[-1]
    return stem == f"{leaf}{SUITE}"


def consumers_of(dotted: str, found: tuple[module_importers.Site, ...]) -> Module:
    """Return `dotted`'s consumer population, split by whether each is its own suite.

    ⚑ THE SITES ARE PASSED IN, NOT FETCHED. An earlier cut called `sites` here, which parses
    the whole corpus per question — so a census over hundreds of candidates became hundreds of
    corpus parses and did not finish (gate-G301). The caller asks ONCE and hands each result
    down, which is the same data through a different loop nesting.
    """
    seen = tuple(sorted({site.path for site in found}))
    mine = tuple(c for c in seen if is_suite_of(c, dotted))
    return Module(dotted, seen, mine)


def _dotted(label: str) -> str:
    """Return the dotted module name for a repo-relative `label`."""
    return label.removesuffix(".py").replace("/", ".")


class Census(NamedTuple):
    """The proof-only population, with the denominator that makes a zero readable.

    ⚑ A BARE ZERO CANNOT DISTINGUISH *SCANNED AND CLEAN* FROM *NEVER SCANNED*. Carrying the
    population scanned makes the difference representable rather than something a reader has
    to ask for separately.
    """

    inert: tuple[Module, ...]
    scanned: int
    blind: tuple[str, ...]

    def lines(self) -> list[str]:
        """Return the report: the proof-only modules, the denominator, and the reader's bounds."""
        out = [m.why() for m in self.inert]
        out.append("")
        out.append(f"{len(self.inert)} proof-only module(s) over {self.scanned} scanned")
        # ⚑⚑ THE FINDING IS A QUESTION, NOT A DELETION ORDER. A member may be a library
        # awaiting its consumer or a capability published for adopters, and a census that
        # implied otherwise would manufacture work.
        out.append(
            "⚑ PROOF-ONLY IS A QUESTION — why does nothing use this — never a verdict "
            "that it is dead."
        )
        if self.blind:
            # ⚑ THE BLIND SHAPES ARE THE READER'S, INHERITED RATHER THAN RE-DERIVED. A module
            # reached only by a dynamic import would read as proof-only here and is not.
            out.append(
                f"⚑ {len(self.blind)} shape(s) the importer reader CANNOT resolve for "
                f"these members — one reached only that way is NOT proof-only:"
            )
            out.extend(f"    {shape}" for shape in self.blind)
        if not self.scanned:
            out.append("⚑ NOTHING WAS SCANNED — this zero is a fact about the invocation.")
        return out


def census(prefix: str = "substrate/") -> Census:
    """Return every module under `prefix` whose only consumers are its own suite.

    ⚑ THE SUITES THEMSELVES ARE NOT CANDIDATES. A selftest is imported by nothing by design —
    a runner discovers it — so including them would fill the report with modules that are
    correctly unreferenced, and the signal would drown in its own convention.
    """
    files = list(module_importers.population())
    labels = [
        label
        for _path, label in files
        if label.startswith(prefix) and label.endswith(".py") and not label.endswith(f"{SUITE}.py")
    ]

    # ⚑⚑ ONE PARSE FOR EVERY CANDIDATE. This is the line gate-G301 is about: asking per module
    # made the census correct and unrunnable, which is the class it was built to find.
    names = [_dotted(label) for label in sorted(labels)]
    every = module_importers.all_sites(names, files)
    inert = [found for dotted in names if (found := consumers_of(dotted, every[dotted])).inert()]

    # ⚑⚑⚑ TWO BULK READS, AND BOTH ARE THE POINT OF gate-G301. The first cut asked per
    # candidate and did not finish; the second added `all_sites` and STILL did not finish,
    # because the blind-shape call beside it was the same quadratic one layer over. ⚑ AND THE
    # THIRD CUT BUILT `all_unresolved` AND LEFT THIS LINE CALLING THE SINGULAR ONE — a bulk
    # reader written and not wired, which is the built-then-orphaned shape this very module
    # exists to census, committed inside it. Fixing one nested loop and leaving its twin is
    # how a performance defect survives its own repair.
    #
    # ⚑⚑ THE PER-MEMBER PRECISION SURVIVES THE INVERSION: `all_unresolved` still answers
    # *what could hide an importer of THIS module* for each name, so the bound reported is
    # about the members reported and not about the corpus in general.
    shapes = module_importers.all_unresolved([m.dotted for m in inert], files)
    blind = {line for found in shapes.values() for line in found}
    return Census(tuple(inert), len(labels), tuple(sorted(blind)))


def run(argv: list[str]) -> int:
    """Print the proof-only census, or the usage.

    ⚑ A NON-EMPTY CENSUS EXITS 1 so this can be wired as a gate later without rewriting the
    contract, and an UNSCANNED run exits 2 rather than 0 — exiting clean on a zero-over-zero
    would bank the false green this module exists to make unrepresentable.
    """
    if not argv or argv[0] != MODE:
        print(__doc__)  # noqa: T201 - the usage, for a bare or unknown invocation
        print(
            f"    proof_only.py {MODE} [prefix]   "  # noqa: T201
            f"# modules whose only consumer is their own suite"
        )
        return USAGE_EXIT
    found = census(argv[1] if len(argv) > 1 else "substrate/")
    for line in found.lines():
        print(line)  # noqa: T201 - this module IS the report
    if not found.scanned:
        return USAGE_EXIT
    return 1 if found.inert else 0


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
