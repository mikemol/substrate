#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.proof_only` — a module whose only consumer is its own proof.

⚑⚑⚑ THE OWN-SUITE DISCRIMINATOR IS THE ITEM, AND COLLAPSING IT IS WRONG IN THE EXPENSIVE
DIRECTION. A module used by some OTHER module's selftest has a real consumer — a fixture
exercising it as a dependency is evidence of use. A reader treating any suite as disqualifying
would report a genuinely-used helper as inert, and the output of this census is read as a list of
things to question the existence of. So the arms pin BOTH directions: this module's own suite does
not count as use, and a sibling's suite does.

⚑⚑ AND A MODULE NOTHING IMPORTS AT ALL IS NOT THIS CLASS. That one is visibly unused and reads as
such; this population is the one that reads as WORKING because a green suite disguises the
inertness. Requiring at least one suite consumer is what keeps the two separate, and an arm asserts
the zero-consumer module is excluded — without it the census would silently become a dead-code
report under a name that promises something narrower.

⚑ THE FIXTURES ARE CONSTRUCTED `Site` ROWS, NOT A LIVE CORPUS SCAN. `census()` asks
`module_importers` for the whole population, which is the expensive call gate-G301 is about; an arm
driving it per case would make this suite the thing the module exists to find.

⚑⚑ AND THE `Site` SHAPE IS READ FROM THE OWNING READER, NOT GUESSED. A first cut of this suite
invented the fields (`module=`, `dotted=`) and the gate refused it — the row is `path, line, form,
names, spelling`. A fixture built on an imagined shape agrees with itself and with nothing else.
"""

from __future__ import annotations

import sys

from substrate import module_importers, proof_only


def _site(path: str) -> module_importers.Site:
    """Return a Site naming one consumer path, built from the owning reader's own type.

    ⚑ THE TYPE COMES FROM THE READER. A local stand-in would let this suite pass against a Site
    shape the real reader no longer produces — a fixture agreeing with itself.
    """
    return module_importers.Site(path=path, line=1, form="import", names=("agree",))


def its_own_suite_is_not_use(out: list[str]) -> int:
    """Check a module consumed only by its own selftest reads INERT — THE WHOLE ITEM.

    ⚑⚑⚑ THIS IS THE MEASURED INSTANCE. `md_hkey.agree` had 16 reads in 1 of 1593 files, every one
    inside `md_hkey_selftest`, while the live defect it would have repaired went unfixed. The
    suite is what disguises the inertness, so the suite is what this keys on.
    """
    found = proof_only.consumers_of("substrate.md_hkey", (_site("substrate/md_hkey_selftest.py"),))
    if not found.inert():
        out.append(f"selftest: a suite-only module read as used: {found!r}")
        return 1
    return 0


def a_siblings_suite_is_use(out: list[str]) -> int:
    """Check another module's selftest counts as a real consumer — THE POSITIVE CONTROL.

    ⚑⚑ WITHOUT THIS ARM a reader treating any `_selftest` consumer as disqualifying passes the
    case above and reports every helper a fixture touches as inert. That is the direction that
    generates deletion work against modules which are in fact exercised.
    """
    found = proof_only.consumers_of("substrate.md_hkey", (_site("substrate/md_lint_selftest.py"),))
    if found.inert():
        out.append(f"selftest: a sibling suite read as non-use: {found!r}")
        return 1
    return 0


def a_production_consumer_is_use(out: list[str]) -> int:
    """Check an ordinary importer disqualifies a module from the population."""
    found = proof_only.consumers_of(
        "substrate.md_hkey", (_site("substrate/md_hkey_selftest.py"), _site("substrate/md_lint.py"))
    )
    if found.inert():
        out.append(f"selftest: a production consumer read as non-use: {found!r}")
        return 1
    return 0


def no_consumers_at_all_is_not_this_class(out: list[str]) -> int:
    """Check a module nothing imports is EXCLUDED — the two populations stay separate.

    ⚑⚑ A MODULE NOTHING IMPORTS IS VISIBLY UNUSED and reads as such; this census is for the one
    that reads as WORKING. Admitting it would quietly turn a narrow finding into a dead-code
    report, under a name that promises the narrower thing.
    """
    found = proof_only.consumers_of("substrate.orphan", ())
    if found.inert():
        out.append(f"selftest: a zero-consumer module read as proof-only: {found!r}")
        return 1
    return 0


def the_suite_name_must_match_the_module(out: list[str]) -> int:
    """Check `is_suite_of` keys on THIS module's leaf, not on the suffix alone.

    ⚑ A PREDICATE MATCHING ANY `_selftest` SUFFIX passes the own-suite arm and fails the sibling
    arm for the wrong reason — it would be right by accident on one case and wrong on the class.
    """
    if not proof_only.is_suite_of("substrate/md_hkey_selftest.py", "substrate.md_hkey"):
        out.append("selftest: a module's own suite was not recognised")
        return 1
    if proof_only.is_suite_of("substrate/md_lint_selftest.py", "substrate.md_hkey"):
        out.append("selftest: a sibling's suite was recognised as this module's")
        return 1
    return 0


def duplicate_sites_count_once(out: list[str]) -> int:
    """Check many import sites in one file are one consumer.

    ⚑ SITES ARE NOT CONSUMERS. `md_hkey` had SIXTEEN reads in ONE file; counting sites would have
    reported it as widely used by the number alone.
    """
    found = proof_only.consumers_of(
        "substrate.md_hkey",
        (_site("substrate/md_hkey_selftest.py"), _site("substrate/md_hkey_selftest.py")),
    )
    if len(found.consumers) != 1:
        out.append(f"selftest: duplicate sites yielded {found.consumers!r}")
        return 1
    if not found.inert():
        out.append(f"selftest: a deduped suite-only module read as used: {found!r}")
        return 1
    return 0


def the_account_names_the_suite(out: list[str]) -> int:
    """Check an inert row says WHICH consumer is the suite.

    ⚑ THE CENSUS IS A QUESTION TO OPEN, so the row must hand over the name a reader would go read.
    A bare verdict sends every reader back to re-derive what the census already knew.
    """
    found = proof_only.consumers_of("substrate.md_hkey", (_site("substrate/md_hkey_selftest.py"),))
    why = found.why()
    if "md_hkey_selftest" not in why:
        out.append(f"selftest: the account omits the suite: {why!r}")
        return 1
    if "PROOF-ONLY" not in why:
        out.append(f"selftest: the account omits the verdict: {why!r}")
        return 1
    return 0


def a_used_module_reports_its_non_suite_consumers(out: list[str]) -> int:
    """Check a used module's account names who uses it, not merely that it is used."""
    found = proof_only.consumers_of(
        "substrate.md_hkey", (_site("substrate/md_hkey_selftest.py"), _site("substrate/md_lint.py"))
    )
    why = found.why()
    if "md_lint.py" not in why:
        out.append(f"selftest: the account omits the real consumer: {why!r}")
        return 1
    return 0


def an_empty_census_is_not_a_clean_bill(out: list[str]) -> int:
    """Check a zero over zero says so rather than reading as a clean corpus."""
    text = "\n".join(proof_only.Census((), 0, ()).lines())
    if "NOTHING WAS SCANNED" not in text:
        out.append(f"selftest: an unscanned census renders as {text!r}")
        return 1
    return 0


def the_census_carries_its_denominator(out: list[str]) -> int:
    """Check a scanned census prints the population it covered."""
    text = "\n".join(proof_only.Census((), 42, ()).lines())
    if "42 scanned" not in text:
        out.append(f"selftest: the denominator is absent from {text!r}")
        return 1
    if "NOTHING WAS SCANNED" in text:
        out.append(f"selftest: a scanned census claims nothing was scanned: {text!r}")
        return 1
    return 0


def proof_only_is_reported_as_a_question(out: list[str]) -> int:
    """Check the report refuses to present membership as a deletion order.

    ⚑ A MEMBER MAY BE A LIBRARY AWAITING ITS CONSUMER, a capability published for adopters, or a
    module whose callers this reader cannot resolve. A census implying otherwise manufactures work.
    """
    text = "\n".join(proof_only.Census((), 1, ()).lines())
    if "QUESTION" not in text:
        out.append(f"selftest: the report omits the question framing: {text!r}")
        return 1
    return 0


def the_blind_shapes_are_reported_in_band(out: list[str]) -> int:
    """Check an unresolvable import shape travels WITH the verdict.

    ⚑⚑ A MODULE REACHED ONLY BY A DYNAMIC IMPORT would read as proof-only here and is not. The
    bound is inherited from `module_importers` rather than re-derived, and a caveat kept in prose
    gets summarised away — so it prints beside the rows it qualifies.
    """
    text = "\n".join(proof_only.Census((), 1, ("dynamic-import",)).lines())
    if "dynamic-import" not in text:
        out.append(f"selftest: the blind shape is absent from {text!r}")
        return 1
    return 0


def a_clean_census_does_not_claim_blindness(out: list[str]) -> int:
    """Check the bound notice is absent when there is no unresolvable shape.

    ⚑ THE MIRROR OF THE ARM ABOVE. A notice printed unconditionally passes that case and tells
    every reader the census is bounded when this run was not.
    """
    text = "\n".join(proof_only.Census((), 1, ()).lines())
    if "CANNOT resolve" in text:
        out.append(f"selftest: a clean census claims blindness: {text!r}")
        return 1
    return 0


def suites_are_not_candidates(out: list[str]) -> int:
    """Check the SUITE constant is what the census excludes itself on.

    ⚑ A SELFTEST IS IMPORTED BY NOTHING BY DESIGN — a runner discovers it — so including suites
    would fill the report with modules that are correctly unreferenced and drown the signal in the
    tree's own convention.
    """
    if not proof_only.SUITE:
        out.append("selftest: no suite suffix declared")
        return 1
    if not proof_only.is_suite_of(f"substrate/thing{proof_only.SUITE}.py", "substrate.thing"):
        out.append(f"selftest: the declared suffix {proof_only.SUITE!r} does not recognise a suite")
        return 1
    return 0


_ARMS = (
    its_own_suite_is_not_use,
    a_siblings_suite_is_use,
    a_production_consumer_is_use,
    no_consumers_at_all_is_not_this_class,
    the_suite_name_must_match_the_module,
    duplicate_sites_count_once,
    the_account_names_the_suite,
    a_used_module_reports_its_non_suite_consumers,
    an_empty_census_is_not_a_clean_bill,
    the_census_carries_its_denominator,
    proof_only_is_reported_as_a_question,
    the_blind_shapes_are_reported_in_band,
    a_clean_census_does_not_claim_blindness,
    suites_are_not_candidates,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 2 + 2 + 2 + 1 + 1 + 2 + 1 + 1 + 1 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"proof-only selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"proof-only selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
