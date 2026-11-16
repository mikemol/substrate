#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.edge_witness` — the T28-edges family, and the silence it prevents.

⚑⚑⚑ THE MULTI-TARGET CASE IS THE SUBJECT. A declared consumer field arrives as the STRING
`'A, B'`, so a family that does not re-split resolves ONE target named `"A, B"` — dangling by
construction. It would then report a defect in the ENTRY when the defect is in the READER, and it
would do so without raising: the count stays plausible and only the membership is wrong.

⚑⚑ AND THE DENOMINATOR IS ASSERTED, NOT JUST THE VERDICT. A family reporting *"no unresolvable
targets"* over ZERO members is a fact about the read, not about the corpus — which is why an
edgeless corpus must report UNMEASURED rather than closed, and why a member roster is a case of
its own.

⚑ THE FIXTURES ARE WRITTEN HERE, NOT READ FROM THE LIVE CORPUS. Measured on live at the time of
writing: `bibstruct --orphans` reports 0 dangling of 107 edges over 45 entries, so a live-corpus
case for an unresolvable target could not fail at all — it would pin today's content and go green
the moment someone edited a bib for unrelated reasons.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from mikemol.witness import raw_bib

from substrate import edge_witness

# Two entries whose edges all resolve, one carrying a MULTI-TARGET declared consumer field.
_RESOLVES = """@misc{ALPHA,
  section  = {s},
  claim    = {a claim},
  enables  = {BETA, GAMMA},
  check    = {item:ALPHA}
}

@misc{BETA,
  section  = {s},
  claim    = {another claim},
  rests-on = {GAMMA},
  check    = {item:BETA}
}

@misc{GAMMA,
  section = {s},
  claim   = {a third claim},
  check   = {item:GAMMA}
}
"""

# One entry naming a target no entry defines.
_DANGLES = """@misc{ALPHA,
  section  = {s},
  claim    = {a claim},
  rests-on = {NOSUCH},
  check    = {item:ALPHA}
}
"""

# A corpus in which no entry carries an edge at all.
_NO_EDGES = """@misc{ALPHA,
  section = {s},
  claim   = {a claim with no relation},
  check   = {item:ALPHA}
}
"""

_MEMBER_COUNT = 2


def _corpus(where: str, text: str) -> raw_bib.Corpus:
    """Write a fixture bib and read it back."""
    path = Path(where) / "warrants.bib"
    path.write_text(text, encoding="utf-8")
    return raw_bib.read(path)


def a_multi_target_declared_field_resolves_every_target(out: list[str]) -> int:
    """Check both targets of `enables = {BETA, GAMMA}` resolve.

    ⚑⚑ THE CASE THIS MODULE EXISTS FOR. Without the re-split, this yields ONE target named
    `"BETA, GAMMA"` — matching no entry, reported as dangling, and blaming the entry for a defect
    in the reader. It raises nothing, so only a case catches it.
    """
    with tempfile.TemporaryDirectory() as where:
        got = edge_witness.parts(_corpus(where, _RESOLVES))
    if got != ():
        out.append(f"selftest: a resolvable multi-target edge was reported unresolved: {got!r}")
        return 1
    return 0


def a_dangling_target_is_reported(out: list[str]) -> int:
    """Check a target no entry defines is named — the POSITIVE CONTROL.

    ⚑ WITHOUT THIS, A PREDICATE THAT RESOLVED EVERYTHING would pass the case above. The pair says
    the family discriminates rather than reporting clean by construction.
    """
    with tempfile.TemporaryDirectory() as where:
        got = edge_witness.parts(_corpus(where, _DANGLES))
    if len(got) != 1 or got[0].target != "NOSUCH":
        out.append(f"selftest: a dangling target was not reported: {got!r}")
        return 1
    return 0


def a_reported_part_names_its_field(out: list[str]) -> int:
    """Check an unresolved part carries the entry AND the field it came from.

    ⚑ THE FIELD IS THE RELATION. `enables` and `rests-on` mean different things — when work
    becomes available versus what a claim is grounded on — so a part that names only the target
    sends a reader to find which of an entry's edges is at fault.
    """
    with tempfile.TemporaryDirectory() as where:
        got = edge_witness.parts(_corpus(where, _DANGLES))
    if not got:
        out.append("selftest: nothing to inspect — the dangling fixture reported no part")
        return 1
    bad = 0
    if got[0].entry != "ALPHA":
        out.append(f"selftest: the part names entry {got[0].entry!r}")
        bad += 1
    if got[0].field != "rests-on":
        out.append(f"selftest: the part names field {got[0].field!r}")
        bad += 1
    return bad


def a_part_carries_its_repair(out: list[str]) -> int:
    """Check a part says what to DO, not merely what is wrong.

    ⚑ A FINDING WITH NO ROUTE IS A FINDING A READER MUST RE-DERIVE. The route names both repairs,
    since a dangling target is as often a typo as a missing entry.
    """
    with tempfile.TemporaryDirectory() as where:
        got = edge_witness.parts(_corpus(where, _DANGLES))
    if not got or "NOSUCH" not in got[0].route:
        out.append(f"selftest: the part carries no actionable route: {got!r}")
        return 1
    return 0


def only_edge_carrying_entries_are_members(out: list[str]) -> int:
    """Check the roster counts participants, not every entry.

    ⚑ AN ENTRY WITH NO EDGE PASSING TRIVIALLY INFLATES THE DENOMINATOR, so a family over a corpus
    of non-participants would report a large green number measuring nothing.
    """
    with tempfile.TemporaryDirectory() as where:
        got = edge_witness.members(_corpus(where, _RESOLVES))
    if len(got) != _MEMBER_COUNT:
        out.append(f"selftest: the member roster is {got!r}, want the two edge-carrying entries")
        return 1
    return 0


def an_edgeless_corpus_has_no_members(out: list[str]) -> int:
    """Check a corpus where nothing carries an edge yields an EMPTY roster.

    ⚑⚑ WHICH THE WITNESS MUST READ AS UNMEASURED. Zero unresolvable targets over zero members is
    a fact about the read; reporting it as satisfied banks a green that measured nothing.
    """
    with tempfile.TemporaryDirectory() as where:
        got = edge_witness.members(_corpus(where, _NO_EDGES))
    if got != ():
        out.append(f"selftest: an edgeless corpus reported members {got!r}")
        return 1
    return 0


def the_declared_consumer_field_is_scanned(out: list[str]) -> int:
    """Check `enables` is in the family's field set.

    ⚑⚑ IT IS NOT IN THE ENGINE'S `_LIST`, so a family reading only the engine's roster skips the
    one field whose re-split is the defect this module exists for — and reports zero while doing
    it. This asserts the UNION is taken.
    """
    if "enables" not in edge_witness.edge_fields():
        out.append(f"selftest: `enables` is not scanned: {edge_witness.edge_fields()!r}")
        return 1
    return 0


def the_engines_own_fields_are_scanned(out: list[str]) -> int:
    """Check the engine's roster is included too — the other half of the union.

    ⚑ THE PAIR SAYS THE UNION IS A UNION. Asserting only the consumer field would pass on a
    family that had dropped the engine's roster entirely.
    """
    got = edge_witness.edge_fields()
    missing = [f for f in ("from", "rests-on") if f not in got]
    if missing:
        out.append(f"selftest: the engine's fields {missing!r} are not scanned: {got!r}")
        return 1
    return 0


def every_declared_member_is_a_real_arm(out: list[str]) -> int:
    """Check the family's declared members are arms this suite actually runs.

    ⚑⚑⚑ A FAMILY NAMING A MEMBER NOBODY RUNS IS THE FALSE-PROTECTION DEFECT THE SHAPE EXISTS TO
    CATCH, turned on the shape itself. The declaration is prose plus a name; nothing about
    writing it forces the named arm to exist, so a renamed or deleted arm leaves the family
    claiming coverage it does not have — and reading as MORE rigorous than an undeclared suite
    while being less.

    ⚑⚑ THE EDGE IS CHECKED HERE RATHER THAN AT CONSTRUCTION because `witness_family` deliberately
    does not run anything: it holds the shape, and only the suite knows what it dispatches. That
    split is why the check has to be a case rather than a validation inside `of()`.
    """
    arms = {arm.__name__ for arm in _ARMS}
    missing = [name for name in edge_witness.FAMILY.names if name not in arms]
    if missing:
        out.append(f"selftest: the family declares members with no arm: {missing!r}")
        return 1
    return 0


def the_familys_premises_all_resolve(out: list[str]) -> int:
    """Check no declared premise names a member the family does not hold.

    ⚑ A DANGLING PREMISE READS AS PROTECTED AND IS NOT. `witness_family` computes this; asserting
    it here is what makes the computation load-bearing for THIS family rather than merely
    available.
    """
    got = edge_witness.FAMILY.dangling_premises()
    if got != ():
        out.append(f"selftest: the family carries a dangling premise: {got!r}")
        return 1
    return 0


_ARMS = (
    a_multi_target_declared_field_resolves_every_target,
    a_dangling_target_is_reported,
    a_reported_part_names_its_field,
    a_part_carries_its_repair,
    only_edge_carrying_entries_are_members,
    an_edgeless_corpus_has_no_members,
    the_declared_consumer_field_is_scanned,
    the_engines_own_fields_are_scanned,
    every_declared_member_is_a_real_arm,
    the_familys_premises_all_resolve,
)

# ⚑ HAND-SUMMED, AND THAT IS THE OPEN ITEM (⟡case-count-derived). `witness_family.Family.count`
# derives this from a roster; this suite cannot use it yet because its `_ARMS` are FUNCTIONS while
# the family's members are DECLARATIONS, and the two are joined only by the case above. Reconciling
# them is the next step, not a thing to fake by writing the derived number here.
_CASE_COUNT = 1 + 1 + 2 + 1 + 1 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"edge-witness selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"edge-witness selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
