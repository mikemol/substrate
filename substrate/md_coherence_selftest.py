# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.md_coherence` — three populations, and the false dangling that taught.

⚑⚑⚑ THE SUB-FINDING ARM LEADS BECAUSE IT IS A MEASURED FALSE POSITIVE. Keying section definitions
only on `^#+ N.` reported `§6d` as a citation to nothing, on a citation that was exactly right —
this corpus writes sub-findings as BOLD paragraphs, and a false DANGLING is the worse direction
because the audit's value is that a non-zero count means act.

⚑⚑ AND THE THREE POPULATIONS ARE ASSERTED SEPARATELY, never as a total. They are three different
repairs, so a suite that only checked `clean` would pass against a reader that put every finding in
one bucket.

⚑ THE FIXTURES ARE LINES AND TEXT, NOT DOCUMENTS. The origin took two paths and read them itself,
so no case could state a direction precisely — and the population defect it carries (gate-F59) is
exactly the kind a fixture-driven suite makes visible, since the caller now supplies the worklist's
labels rather than the reader assuming one file holds them all.
"""

from __future__ import annotations

import sys

from mikemol.mdstruct import labels as md_labels

from substrate import md_coherence as mc

#: A plan mentioning two labels and defining one ordinary section.
#:
#: ⚑⚑⚑ THE LABELS ARE `T13`-SHAPED BECAUSE `Ⓝ100` IS NOT ONE (gate-G275). My first fixtures wrote
#: `Ⓝ100` and `Ⓝ101`, and `md_labels.ITEM_RE` reads BOTH as the bare glyph `Ⓝ` — its enclosed
#: branch matches a SINGLE character `[①-⓿]` with no digits after it. So the two fixtures collided
#: into one label and five arms failed at once. The module was right and the fixture invented a
#: family the grammar does not admit, which is the same shape as a suite asserting a rule its
#: subject never claimed.
PLAN = ["# 1. The first section", "It discusses T13 at length.", "And also T14."]

#: ⚑ THE SUB-FINDING SPELLING, verbatim in the shape the corpus writes it.
SUBFINDING_PLAN = ["# 6. The parent", "**6d. Armed but not firing**", "body text"]


def _direction_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the two label directions, asserted separately."""
    out: list[tuple[str, bool]] = []

    # A worklist holding a label the plan never mentions is an ORPHAN.
    orphan = mc.compare(PLAN, ["T13", "T99"], "")
    out.append(
        (f"a worklist-only label is an orphan: {orphan.orphans}", orphan.orphans == ("T99",))
    )

    # A plan label nobody scheduled is UNWITNESSED — the dominant direction when first measured.
    out.append(
        (
            f"and a plan-only label is unwitnessed: {orphan.unwitnessed}",
            orphan.unwitnessed == ("T14",),
        )
    )

    # ⚑ BOTH DIRECTIONS AT ONCE, because a reader collapsing them would pass either arm alone.
    out.append(
        (f"and they are separate populations: {orphan.why()}", orphan.orphans != orphan.unwitnessed)
    )

    matched = mc.compare(PLAN, ["T13", "T14"], "")
    out.append((f"a matching pair is clean: {matched.why()}", matched.clean))
    return out


def _dangling_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for citations, including the measured false positive.

    ⚑⚑ THE `§6d` ARM IS THE ONE THE ORIGIN GOT WRONG. A reader keying only on headings calls this
    dangling, and that one bogus row is what teaches a reader to skim the whole audit.
    """
    out: list[tuple[str, bool]] = []

    real = mc.compare(PLAN, [], "see §1 for detail")
    out.append(
        (f"a citation to a real section is not dangling: {real.dangling}", real.dangling == ())
    )

    absent = mc.compare(PLAN, [], "see §99 for detail")
    out.append(
        (f"a citation to nothing IS dangling: {absent.dangling}", absent.dangling == ("99",))
    )

    # ⚑ THE MEASURED FALSE POSITIVE, as its own arm.
    sub = mc.compare(SUBFINDING_PLAN, [], "see §6d for detail")
    out.append((f"a bold sub-finding citation is NOT dangling: {sub.dangling}", sub.dangling == ()))

    # ⚑ THE SENSITIVITY ARM. Removing ONLY the bold marker must make it dangle, or the
    # sub-finding pattern is not what admitted it.
    plain = ["# 6. The parent", "6d. Armed but not firing", "body text"]
    moved = mc.compare(plain, [], "see §6d for detail")
    out.append(
        (f"removing ONLY the bold marker flips it: {moved.dangling}", moved.dangling == ("6d",))
    )
    return out


def _spelling_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the spellings the corpus actually writes."""
    out: list[tuple[str, bool]] = []

    out.append(
        (
            f"a suffixed sub-finding is a section: {mc.sections('**7b-bis. Title')}",
            "7b-bis" in mc.sections("**7b-bis. Title"),
        )
    )
    out.append(
        (
            f"a sectioned heading is too: {mc.sections('## §12. Title')}",
            "12" in mc.sections("## §12. Title"),
        )
    )
    out.append(
        (
            f"and a citation reads either spelling: {mc.citations('see §12 and §6d')}",
            mc.citations("see §12 and §6d") == {"12", "6d"},
        )
    )
    return out


def _grammar_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` proving the label grammar is `md_labels`' and not re-derived.

    ⚑ A SECOND SPELLING OF THE RULE IS HOW A FAMILY GETS DROPPED from one reader while the other
    still sees it, so this asserts agreement rather than a hardcoded expectation.
    """
    out: list[tuple[str, bool]] = []

    line = "It discusses T13 at length."
    out.append(
        (
            f"the module agrees with md_labels: {mc.labels([line])}",
            mc.labels([line]) == set(md_labels.labels_in(line)),
        )
    )
    out.append(
        (
            f"and a line with no label yields none: {mc.labels(['plain prose'])}",
            mc.labels(["plain prose"]) == set(md_labels.labels_in("plain prose")),
        )
    )
    return out


def _population_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the gate-F59 repair — the caller supplies the population.

    ⚑⚑⚑ THIS IS THE DEFECT THE ORIGIN CARRIES. Reading ONE worklist while the tree holds six
    ledgers made every label registered elsewhere read as unwitnessed. Here a second ledger's
    labels simply join the set, and the false unwitnessed row disappears — which is the repair
    being a CALLING CONVENTION rather than a better reader.
    """
    out: list[tuple[str, bool]] = []

    one_ledger = mc.compare(PLAN, ["T13"], "")
    out.append(
        (
            f"one ledger reports the other label unwitnessed: {one_ledger.unwitnessed}",
            one_ledger.unwitnessed == ("T14",),
        )
    )

    both_ledgers = mc.compare(PLAN, ["T13", "T14"], "")
    out.append(
        (
            f"adding the second ledger clears it: {both_ledgers.unwitnessed}",
            both_ledgers.unwitnessed == (),
        )
    )
    return out


def _live_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` running the comparison over the live plan document.

    ⚑ A FIXTURE-ONLY SUITE PROVES THE READER AGREES WITH ITSELF. This drives real text, so a
    pattern that works on three-line fixtures and not on a 3477-line document is caught here.
    """
    out: list[tuple[str, bool]] = []

    from pathlib import Path  # noqa: PLC0415 - only this arm needs a real document

    doc = Path.home() / ".claude/plans/dispatch-a-research-agent-streamed-torvalds.md"
    if not doc.exists():
        out.append((f"the live plan is absent — a fact about the METHOD: {doc}", True))
        return out

    lines = doc.read_text(encoding="utf-8").split("\n")
    found = mc.labels(lines)
    out.append((f"the live plan yields labels: {len(found)}", len(found) > 0))

    # ⚑ EVERY LABEL FOUND MUST SURVIVE A ROUND TRIP through the grammar that produced it.
    out.append(
        (
            f"and every one is a label md_labels admits: {len(found)}",
            all(label in mc.labels([label]) for label in found),
        )
    )
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _direction_cases()
        + _dangling_cases()
        + _spelling_cases()
        + _grammar_cases()
        + _population_cases()
        + _live_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"md-coherence selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
