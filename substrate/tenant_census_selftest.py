#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.tenant_census` — and whether the join reproduces the hand rulings.

⚑⚑⚑ THE RULINGS ARM IS A HYPOTHESIS UNDER TEST, NOT A CLAIM. Seven rows in the pre-split
runner reach a store only through a DEFERRED edge, each carrying a hand-written verdict keyed
on filename. The proposal is that joining the two decorrelated lenses — import-reach for the
route, call-sites for whether a store-opener is NAMED — decides them mechanically. This arm
measures the agreement on the live tree and REPORTS it; it does not assert the hypothesis
holds.

⚑ AND A DISAGREEMENT WOULD BE THE FINDING, NOT A FAILURE. If the join splits a row the hand
ruled differently, that says either the ruling encoded something neither lens can see (which
is worth knowing precisely) or the ruling was wrong (also worth knowing). Writing this arm to
FAIL on disagreement would pressure the join toward reproducing whatever was written, which is
fitting the instrument to its own answer.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from mikemol.corpus import suite_discovery

from substrate import corpus, store_reach, tenant_census

# The pre-split hand rulings, transcribed: {basename: verdict-word}. Read from
# `run_selftests.IF_IT_RUNS_RULINGS` at the time of the split.
_HAND_RULINGS = {
    "query_builders.py": "not-owed",
    "sql_census.py": "not-owed",
    "sql_lift.py": "runs/not-owed",
    "pycodemod.py": "OWED-UNSTATABLE",
    "check_mypy_ratchet.py": "not-owed",
    "ddl_lifecycle.py": "runs/not-owed",
    "tier_readset.py": "not-owed",
}

# The trees the module index spans.
_TREES = ("scripts", "scratch", "jea", "catalog", "substrate", "tests")

# A suite importing a store seed at module scope.
_EAGER = "import store\n\nif __name__ == '__main__':\n    pass\n"

# A suite reaching a seed only from inside a function.
_DEFERRED = "def go():\n    import store\n    return store.connect()\n"

# A suite declaring a tenant it does not need.
_STRAY = "# selftest-tenant: sandbox\nprint('hi')\n"


def _seed_tree(d: str) -> None:
    """Create the fixture tree with a stub `store` module."""
    root = Path(d)
    (root / "scripts").mkdir(exist_ok=True)
    (root / "scripts" / "store.py").write_text("def connect(): ...\n", encoding="utf-8")


def _index(d: str) -> dict[str, str]:
    """Build a module index over a fixture tree — AFTER every suite has been written.

    ⚑⚑ THE INDEX IS A SNAPSHOT, AND CALLING IT FIRST COST THREE DEBUGGING ROUNDS. The helper
    originally created the tree AND indexed it, so suites written afterwards were absent from
    the index and the walk could not resolve a hop to them. The symptom was `via=()` — a route
    that looks like "does not reach" and is really "could not resolve" — which is the
    method-reported-as-substrate shape, in a fixture.

    ⚑ AND IT MASQUERADED AS A CODE BUG for two rounds: an isolating case reported *"the loose
    walk missed a seed one hop away"*, which reads as a defect in the walk. It was a defect in
    the setup. The isolating case was still the right move — it narrowed two layers to one —
    but the layer it named was not the guilty one.
    """
    _seed_tree(d)
    return store_reach.module_index(Path(d), ("scripts",))


def _suite(d: str, name: str, src: str) -> str:
    """Write a fixture suite and return its path."""
    _seed_tree(d)
    path = Path(d) / "scripts" / name
    path.write_text(src, encoding="utf-8")
    return str(path)


def owed_and_stray(out: list[str]) -> int:
    """Check the 2x2: reaching-without-declaring is OWED, declaring-without-reaching is STRAY.

    ⚑ STRAY IS WHAT MAKES A DECLARATION FALSIFIABLE. Without it a wrong tenant sits forever,
    since nothing contradicts a claim nobody checks.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as d:
        idx = _index(d)
        owed = tenant_census.row("owed", _suite(d, "owed.py", _EAGER), idx)
        stray = tenant_census.row("stray", _suite(d, "stray.py", _STRAY), idx)
    if owed.verdict != "OWED":
        out.append(f"selftest: a reaching, undeclared suite is {owed.verdict!r}, not OWED")
        bad += 1
    if stray.verdict != "STRAY":
        out.append(f"selftest: a declaring, non-reaching suite is {stray.verdict!r}")
        bad += 1
    return bad


def deferred_is_its_own_class(out: list[str]) -> int:
    """Check a deferred-only reacher is neither OWED nor clear.

    ⚑ IT IS THE ROW THE HAND RULINGS EXIST FOR. Calling it OWED would refuse suites that
    cannot abort; calling it clear would certify ones that can.
    """
    with tempfile.TemporaryDirectory() as d:
        idx = _index(d)
        got = tenant_census.row("lazy", _suite(d, "lazy.py", _DEFERRED), idx)
    if not got.deferred_only:
        out.append(f"selftest: a deferred-only reacher was not marked: {got}")
        return 1
    if not got.verdict.startswith("if-it-runs"):
        out.append(f"selftest: a deferred-only reacher is {got.verdict!r}")
        return 1
    return 0


def call_lens_splits_the_deferred(out: list[str]) -> int:
    """Check the call lens separates a deferred reacher that OPENS from one that is inert.

    ⚑ THIS IS THE JOIN THE HAND RULINGS WERE DOING. `_DEFERRED` calls `store.connect()`, so it
    names an opener; a file that merely imports lazily and never calls does not.
    """
    bad = 0
    inert = "def go():\n    import store\n    return 1\n"
    with tempfile.TemporaryDirectory() as d:
        idx = _index(d)
        opens = tenant_census.row("opens", _suite(d, "opens.py", _DEFERRED), idx)
        quiet = tenant_census.row("quiet", _suite(d, "quiet.py", inert), idx)
    if opens.verdict != "if-it-runs/opens":
        out.append(f"selftest: a deferred opener is {opens.verdict!r}")
        bad += 1
    if quiet.verdict != "if-it-runs/inert":
        out.append(f"selftest: a deferred non-opener is {quiet.verdict!r}")
        bad += 1
    return bad


def rulings_agreement(out: list[str]) -> int:
    """REPORT how the join compares with the seven hand rulings on the live tree.

    ⚑ REPORTS, NEVER REFUSES. A disagreement is a finding about the rulings or about the
    lenses, and failing here would pressure the join toward reproducing whatever was written —
    fitting the instrument to its own answer.
    """
    index = store_reach.module_index(corpus.ROOT, _TREES)
    suites = suite_discovery.discover(corpus.ROOT)
    by_name = {Path(p).name: (label, p) for label, p in suites}

    agree = disagree = unseen = 0
    for name, hand in sorted(_HAND_RULINGS.items()):
        found = by_name.get(name)
        if found is None:
            unseen += 1
            continue
        got = tenant_census.row(found[0], found[1], index)
        # The hand vocabulary maps onto the join: OWED-UNSTATABLE means it opens; the
        # not-owed variants mean it does not.
        joined_opens = got.verdict == "if-it-runs/opens"
        hand_opens = hand == "OWED-UNSTATABLE"
        if got.deferred_only and joined_opens == hand_opens:
            agree += 1
        else:
            disagree += 1
            out.append(
                f"  note: {name} hand={hand} join={got.verdict} "
                f"opens={sorted(got.opens)} via={got.via}"
            )
    sys.stdout.write(f"  rulings: {agree} agree, {disagree} differ, {unseen} not discovered\n")
    return 0


def opener_past_a_cut_is_not_credited(out: list[str]) -> int:
    """Check an opener beyond a deferred hop is NOT counted — on fixtures, not on rulings.

    ⚑⚑⚑ THIS ARM EXISTS BECAUSE THE RULINGS ARM CANNOT JUSTIFY THE RULE IT MEASURES. The
    eager-prefix predicate was introduced after a join disagreed with seven hand rulings, and
    then agreement went 3/7 -> 7/7. That sequence is indistinguishable from fitting the
    instrument to its own answer, so the rule needs a case whose expected value comes from the
    STATED SEMANTICS rather than from the table under review.

    ⚑ THE SEMANTICS: a `~` hop fires only if a function runs, so everything past it is
    conditional on that. `mid` imports `deep` from inside a function; `deep` opens a store.
    Importing `entry` executes NOTHING in `deep`, so `entry` names no reachable opener — a
    fact about Python, checkable without reference to any adjudication.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as d:
        idx = _index(d)
        _suite(d, "deep.py", "import store\n\ndef go():\n    return store.connect()\n")
        _suite(d, "mid.py", "def later():\n    import deep\n    return deep.go()\n")
        entry = _suite(d, "entry.py", "import mid\n\ndef run():\n    return mid.later()\n")
        got = tenant_census.row("entry", entry, idx)

    if "connect" in got.opens:
        out.append(
            f"selftest: an opener past a deferred hop was credited: via={got.via} "
            f"opens={sorted(got.opens)}"
        )
        bad += 1

    # ⚑⚑ AND THE MIRROR, WHICH THE FIRST DRAFT GOT WRONG IN AN INSTRUCTIVE WAY. I wrote a
    # chain of EAGER imports ending at `store` and asserted the opener was credited — but a
    # fully-eager reacher is `OWED`, not `if-it-runs`, and `opens` is only consulted for the
    # deferred class. The case failed for a reason about the FIXTURE rather than the code, and
    # it failed while the rulings arm read 7/7. **A case that fails on its own setup is still
    # worth more than one that passes: it is the only reason I checked what `via` held.**
    #
    # ⚑ AND THE SECOND DRAFT FAILED THE SAME WAY, WHICH IS THE FINDING. Any chain whose store
    # import is EAGER makes the row `OWED` — so a deferred-only row with a non-empty eager
    # prefix requires the store hop to be the lazy one while an EARLIER, eagerly-imported hop
    # names the opener. Getting that fixture right took three attempts, and each wrong one
    # passed the rulings arm at 7/7: **agreement with the table says nothing about whether the
    # cases underneath it are testing what they claim.**
    with tempfile.TemporaryDirectory() as d:
        _suite(d, "opener.py", "def go():\n    import store\n    return store.connect()\n")
        entry = _suite(d, "front.py", "import opener\n")
        idx = _index(d)
        got = tenant_census.row("front", entry, idx)
    if not got.deferred_only:
        out.append(f"selftest: the mirror fixture is not deferred-only: via={got.via}")
        bad += 1
    elif "connect" not in got.opens:
        out.append(
            f"selftest: an opener on the eager prefix was not credited: via={got.via} "
            f"opens={sorted(got.opens)}"
        )
        bad += 1
    return bad


def deferred_reach_crosses_a_hop(out: list[str]) -> int:
    """Check the loose walk finds a seed imported lazily by an EAGERLY-imported module.

    ⚑⚑⚑ THIS IS THE SHAPE EVERY `if-it-runs` ROW HAS, and three fixture attempts failed to
    produce it before this case isolated why. `front` imports `opener` at module scope;
    `opener` imports `store` inside a function. Importing `front` executes nothing in the
    store, so the strict walk must say NO — and the loose walk must say YES, via `~store`.

    ⚑ ISOLATED FROM THE CENSUS DELIBERATELY. The census failure said `via=()`, which could be
    the walk, the index, or the fixture; asking the walk directly is what separates them. A
    case that reports through two layers cannot say which one is wrong.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as d:
        _suite(d, "opener.py", "def go():\n    import store\n    return store.connect()\n")
        entry = _suite(d, "front.py", "import opener\n")
        idx = _index(d)
        strict, strict_via = store_reach.reaches(entry, idx)
        loose, loose_via = store_reach.reaches(entry, idx, through_cuts=True)
    if strict:
        out.append(f"selftest: the strict walk reached a lazily-imported seed: {strict_via}")
        bad += 1
    if not loose:
        out.append(f"selftest: the loose walk missed a seed one hop away: {loose_via}")
        bad += 1
    return bad


def eager_prefix_truncates(out: list[str]) -> int:
    """Check the prefix stops at the FIRST cut, not at the last.

    ⚑ ONE `~` ANYWHERE MAKES EVERY LATER HOP CONDITIONAL. A filter that merely dropped the
    marked hops would keep the ones after them, which is the whole error being corrected.
    """
    got = store_reach.eager_prefix(("a", "b", "~c", "d", "e"))
    if got != ("a", "b"):
        out.append(f"selftest: the prefix did not truncate at the first cut: {got}")
        return 1
    return 0


_ARMS = (
    owed_and_stray,
    deferred_is_its_own_class,
    call_lens_splits_the_deferred,
    opener_past_a_cut_is_not_credited,
    deferred_reach_crosses_a_hop,
    eager_prefix_truncates,
    rulings_agreement,
)

_CASE_COUNT = 2 + 2 + 2 + 2 + 2 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if out:
        sys.stdout.write("\n".join(out) + "\n")
    if failures:
        sys.stderr.write(f"tenant-census selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"tenant-census selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
