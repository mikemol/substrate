#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.adopter_import` — what an adopter's wheel can and cannot reach.

⚑⚑⚑ THIS MODULE COMPUTES A BLOCKER THE MANIFEST REPORTS FOR THE WHOLE CORPUS. `intake_manifest`
calls `blocked_set()`, so a wrong verdict here moves the READY count for every module — the reach
is wide even though the blocker's own SOLE count is small. That asymmetry is why it is worth
pinning: a defect would be read as a fact about the tree rather than about this predicate.

⚑⚑ `_resolvable` HAS THREE ACCEPTANCE PATHS AND EACH MUST BE PINNED SEPARATELY. A packaged module,
a DOTTED name whose root is packaged, and a name the interpreter can already find — an arm covering
one leaves the others free to break, and the middle one is the easiest to lose because it looks
like a special case of the first.

⚑⚑⚑ AND ONE PATH READS MUTABLE STATE, WHICH BOUNDS WHAT MAY BE ASSERTED. `find_spec` answers about
what is INSTALLED, so an arm naming a third-party package would change polarity with the
environment — the witness-with-mutable-state hazard. The arms here use the stdlib (present in any
interpreter that can run them) and a name no distribution defines, so both verdicts hold by
construction rather than by what happens to be installed today.

⚑ THE RANKING IS ASSERTED AS AN ORDER, NEVER AS A LIST. `reach_backs` sorts by consumer count
descending then by name, and a case pinning today's members would go red the moment a drain lands
— reporting finished work as a defect.
"""

from __future__ import annotations

import sys

from substrate import adopter_import


def _fail(out: list[str], why: str) -> int:
    """Record one failure and return its contribution to the exit code."""
    out.append(f"selftest: {why}")
    return 1


def a_packaged_name_resolves(out: list[str]) -> int:
    """Check a module of the distribution itself is reachable — the first acceptance path."""
    if not adopter_import._resolvable("substrate", ("substrate",)):  # noqa: SLF001 — the predicate
        return _fail(out, "a packaged name did not resolve")
    return 0


def a_dotted_name_under_a_package_resolves(out: list[str]) -> int:
    """Check a submodule of a packaged root resolves — the path easiest to lose.

    ⚑⚑ IT LOOKS LIKE A SPECIAL CASE OF THE FIRST AND IS NOT. `substrate.corpus` is not itself in
    the packages tuple; the predicate splits on the first dot and asks about the ROOT. Dropping
    that clause would report every intra-package import as a reach into an unpackaged tree, which
    is the direction that manufactures an enormous blocker out of nothing.
    """
    if not adopter_import._resolvable("substrate.corpus", ("substrate",)):  # noqa: SLF001
        return _fail(out, "a dotted name under a packaged root did not resolve")
    return 0


def a_stdlib_name_resolves(out: list[str]) -> int:
    """Check a name the interpreter can find resolves even when unpackaged.

    ⚑ THE STDLIB IS USED RATHER THAN A THIRD-PARTY PACKAGE because `find_spec` reads what is
    INSTALLED — a witness whose command reads mutable state cannot hold a stable polarity, and
    `json` is present in any interpreter able to run this file.
    """
    if not adopter_import._resolvable("json", ("substrate",)):  # noqa: SLF001 — the predicate
        return _fail(out, "a stdlib name did not resolve")
    return 0


def an_unfindable_name_does_not_resolve(out: list[str]) -> int:
    """Check a name nothing provides is a reach — THE POSITIVE CONTROL.

    ⚑⚑⚑ WITHOUT THIS ARM a predicate returning True for everything passes all three above and
    reports the corpus as reaching for nothing, which is the flattering direction: the blocker
    empties and every module reads as one step closer to shippable.
    """
    if adopter_import._resolvable("no_such_top_level_pkg_at_all", ("substrate",)):  # noqa: SLF001
        return _fail(out, "an unfindable name resolved")
    return 0


def a_sibling_package_is_not_a_prefix_match(out: list[str]) -> int:
    """Check the root test splits on the dot rather than matching a prefix.

    ⚑⚑ `substrate_extra` SHARES A PREFIX WITH `substrate` AND IS A DIFFERENT DISTRIBUTION. A
    `startswith` would swallow it and report a genuine reach as packaged — the same flattering
    direction, arriving through a spelling rather than a predicate.
    """
    if adopter_import._resolvable("substrate_extra", ("substrate",)):  # noqa: SLF001
        return _fail(out, "a prefix-sharing sibling was treated as packaged")
    return 0


def thin_means_one_consumer(out: list[str]) -> int:
    """Check `thin` answers about consumer COUNT, not about the callee's size.

    ⚑ THE TWO RANK OPPOSITELY and the record's own docstring says so: a one-consumer edge is the
    cheapest drain, a many-consumer edge unblocks the most. An arm asserting only the true case
    would pass against a property returning True always, so both are pinned.
    """
    one = adopter_import.ReachBack("mod", ("a",))
    many = adopter_import.ReachBack("mod", ("a", "b"))
    if not one.thin:
        return _fail(out, "a single-consumer reach did not read as thin")
    if many.thin:
        return _fail(out, "a multi-consumer reach read as thin")
    return 0


def a_clean_probe_is_the_declared_verdict(out: list[str]) -> int:
    """Check `clean` defers to the module's CLEAN constant rather than a second spelling.

    ⚑ A LITERAL HERE WOULD DRIFT the first time the constant moved, and the suite would keep
    passing while the shipped predicate answered differently.
    """
    good = adopter_import.Probe("m", adopter_import.CLEAN, "")
    bad = adopter_import.Probe("m", "ImportError", "boom")
    if not good.clean:
        return _fail(out, "a CLEAN probe did not read as clean")
    if bad.clean:
        return _fail(out, "a failing probe read as clean")
    return 0


def by_verdict_drops_the_clean_ones(out: list[str]) -> int:
    """Check the grouping reports FAILURES, not the whole population.

    ⚑ THE CALLER OF A GROUPING WANTS WHAT TO ACT ON. Folding the clean modules in would put the
    largest group at the top of a paydown queue and bury every real failure under it.
    """
    rows = [
        adopter_import.Probe("a", adopter_import.CLEAN, ""),
        adopter_import.Probe("b", "ImportError", "no module"),
        adopter_import.Probe("c", "ImportError", "no module"),
    ]
    grouped = adopter_import.by_verdict(rows)
    if adopter_import.CLEAN in grouped:
        return _fail(out, "the grouping kept the clean modules")
    named = sorted(probe.module for probe in grouped.get("ImportError", []))
    if named != ["b", "c"]:
        return _fail(out, f"the grouping lost a failure: {named!r}")
    return 0


def the_ranking_is_by_consumer_count_then_name(out: list[str]) -> int:
    """Check the order is an ORDER, asserted structurally rather than as today's members.

    ⚑⚑⚑ A CASE PINNING THE LIVE MEMBERS WOULD GO RED THE MOMENT A DRAIN LANDS, reporting finished
    work as a defect — the census-keyed-on-today shape. What survives every tree state is the
    comparator: more consumers first, ties broken by name.
    """
    rows = adopter_import.reach_backs(("substrate",))
    keyed = [(-len(row.consumers), row.depended) for row in rows]
    if keyed != sorted(keyed):
        return _fail(out, "the reach-back ranking is not by consumer count then name")
    return 0


def every_reach_back_names_a_consumer(out: list[str]) -> int:
    """Check no reach is reported without saying who reaches — a RELATION, not a count.

    ⚑ A BLOCKER WITHOUT ITS CONSUMERS IS UNACTIONABLE: the remedy is to drain a consumer, and a
    row that named only the callee would send a reader back to re-derive what the reader knew.
    """
    for row in adopter_import.reach_backs(("substrate",)):
        if not row.consumers:
            return _fail(out, f"a reach-back names no consumer: {row.depended!r}")
        if not row.depended:
            return _fail(out, "a reach-back names no dependency")
    return 0


_ARMS = (
    a_packaged_name_resolves,
    a_dotted_name_under_a_package_resolves,
    a_stdlib_name_resolves,
    an_unfindable_name_does_not_resolve,
    a_sibling_package_is_not_a_prefix_match,
    thin_means_one_consumer,
    a_clean_probe_is_the_declared_verdict,
    by_verdict_drops_the_clean_ones,
    the_ranking_is_by_consumer_count_then_name,
    every_reach_back_names_a_consumer,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 1 + 2 + 2 + 2 + 1 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"adopter-import selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"adopter-import selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
