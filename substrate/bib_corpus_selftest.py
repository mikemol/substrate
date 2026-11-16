# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.bib_corpus` — the origin's composed-corpus assertions, reproduced.

⚑⚑⚑ THE LOAD-BEARING PAIR IS ONE EDGE WITH TWO VERDICTS. C's premise lives in a sibling bib: read
alone it is DANGLING, read together it RESOLVES. Nothing about the edge changed — only what the
reader was given — and asserting just one half would pass against a reader that never composes.

⚑⚑ THE CONTROL IS AS LOAD-BEARING AS THE CASE. A collision warning that fired unconditionally would
pass every duplicate-key assertion while being useless, so disjoint bibs are asserted to report NO
collision. The origin's fixture also carries a DELIBERATE dangling edge, so *"no orphans"* is never
the right assertion — the claim is always about a NAMED edge.

⚑ AND ONE CASE IS A SEQUENCE, NOT A STATE. The origin held collisions in a module-level list, so a
stale one could leak into the next read. That is invisible if the clean read runs first: the
assertion only means something AFTER a dirty read. Here the value is returned rather than stashed,
so the leak is unrepresentable — and the case is kept anyway, because a future refactor could
reintroduce the store.
"""

from __future__ import annotations

from pathlib import Path

from substrate import bib_corpus

# The fixture corpus: three bibs, and every property below is a fact about how they COMPOSE.
# ⚑ `w` CARRIES A DELIBERATE DANGLER (`enables = {A, NOSUCH}`) so that a bare "no orphans"
# assertion can never be the thing under test.
_W = {
    "A": {"section": "s", "claim": "alpha", "check": "item:A"},
    "B": {
        "section": "s",
        "from": "A",
        "rests-on": "A",
        "enables": "A, NOSUCH",
        "claim": "beta",
        "check": "item:B",
    },
}
_W2 = {"C": {"section": "s", "rests-on": "A", "claim": "gamma", "check": "item:C"}}
_W3 = {"A": {"section": "s", "claim": "alpha-redeclared", "check": "item:A"}}

# ⚑ THE MENTION FIXTURES. `M` names `A` in PROSE where `B` declares an edge to it, so the two
# halves of "evidence, not a declaration" are separable. `M2` names `A-extended`, which CONTAINS
# `A` — the case that makes a bare substring search wrong.
_M = {"M": {"section": "s", "claim": "this rests on the A case", "check": "item:M"}}
_LONG = {
    "A-extended": {"section": "s", "claim": "the extended one", "check": "item:A-extended"},
    "M2": {"section": "s", "claim": "see A-extended for the rest", "check": "item:M2"},
}

_BIBS: dict[str, dict[str, dict[str, str]]] = {
    "w.bib": _W,
    "w2.bib": _W2,
    "w3.bib": _W3,
    "m.bib": _M,
    "long.bib": _LONG,
}


def _read(path: Path) -> dict[str, dict[str, str]]:
    """Return the fixture bib at `path`, standing in for the real parser."""
    return _BIBS[path.name]


def _compose(*names: str) -> bib_corpus.Corpus:
    """Compose the named fixture bibs."""
    return bib_corpus.compose([Path(n) for n in names], _read)


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    def dangling(corpus: bib_corpus.Corpus) -> set[tuple[str, str]]:
        return {(src, dst) for _kind, src, dst in bib_corpus.orphans(corpus)}

    # ── the same edge, two verdicts ──────────────────────────────────────────
    alone = _compose("w2.bib")
    both = _compose("w2.bib", "w.bib")
    check(
        "a premise in another bib is DANGLING when that bib is not passed",
        passed=("C", "A") in dangling(alone),
    )
    check("...and RESOLVES when both bibs are passed", passed=("C", "A") not in dangling(both))
    check(
        "...while the fixture's OWN deliberate dangler is still reported",
        passed=("B", "NOSUCH") in dangling(both),
    )

    # ⚑ THE COUNT CASE — the exact silent-drop signature. The broken origin reported the FIRST
    # file's entries and ignored the rest, so a byte-identical count across a widened input read
    # as "the finding survives."
    check(
        "every bib passed is counted",
        passed=len(_compose("w.bib", "w2.bib").entries) == len(_W) + len(_W2),
    )
    check(
        "and every bib passed is named as a source",
        passed=_compose("w.bib", "w2.bib").sources == ("w.bib", "w2.bib"),
    )

    # ── the duplicate key is reported, and the gap is named ──────────────────
    collided = _compose("w.bib", "w3.bib")
    check(
        "a key declared in two bibs is REPORTED",
        passed=[c.key for c in collided.collisions] == ["A"],
    )
    check("...and both homes are named", passed=collided.collisions[0].homes == ("w.bib", "w3.bib"))
    check(
        "...and the LATER declaration wins",
        passed=collided.collisions[0].winner == "w3.bib"
        and collided.entries["A"]["claim"] == "alpha-redeclared",
    )

    # ⚑⚑ THE TWO NUMBERS, AND CARRYING BOTH IS THE POINT. Distinct keys and declarations differ
    # by exactly the duplicates — the gap a peer had to rule out by hand.
    check(
        "distinct keys and declarations differ by the duplicate",
        passed=collided.declared == len(collided.entries) + 1,
    )
    line = collided.gap_line()
    check(
        "the gap is NAMED rather than left to be rediscovered",
        passed=line is not None and "more than one bib" in line,
    )
    check("...and the line says which key", passed=line is not None and "A" in line)
    check(
        "...and says the later declaration wins", passed=line is not None and "later wins" in line
    )

    # ⚑ THE CONTROL: a warning that fired unconditionally would pass every case above.
    disjoint = _compose("w.bib", "w2.bib")
    check("...while disjoint bibs report no collision", passed=disjoint.collisions == ())
    check("...and offer no gap line", passed=disjoint.gap_line() is None)
    check(
        "...and their declared count equals their distinct count",
        passed=disjoint.declared == len(disjoint.entries),
    )

    # ── the sequence case: a dirty read must not colour the next clean one ───
    # ⚑⚑ ONLY MEANINGFUL IN THIS ORDER. Running the clean read first passes against a reader that
    # never clears. The origin's collisions were module-level state, so this was a real leak.
    _compose("w.bib", "w3.bib")
    check(
        "a stale collision does NOT leak into the next clean read",
        passed=_compose("w.bib", "w2.bib").collisions == (),
    )

    # ── edges are read from one roster ───────────────────────────────────────
    kinds = {kind for kind, _s, _d in bib_corpus.edges(both)}
    check("every declared edge kind is walked", passed={"from", "rests-on", "enables"} <= kinds)
    check(
        "a comma-separated field yields one edge per target",
        passed=("enables", "B", "A") in bib_corpus.edges(both)
        and ("enables", "B", "NOSUCH") in bib_corpus.edges(both),
    )
    check(
        "an absent edge field yields nothing",
        passed=not [e for e in bib_corpus.edges(both) if e[0] == "consumes"],
    )

    # ── mentions: evidence from PROSE, never a declared edge ─────────────────
    # ⚑ THE FIXTURE IS BUILT FOR THIS CASE. `B` DECLARES `from = A` and `M` NAMES `A` in prose,
    # so the two halves are separable: a reader that reported both would be offering the author's
    # own declaration back as evidence for making it.
    prose = bib_corpus.compose([Path("w.bib"), Path("m.bib")], _read)
    named = {(other, field) for other, field, _ctx in bib_corpus.mentions(prose, "A")}
    check("prose naming a key is reported", passed=("M", "claim") in named)
    check(
        "but a DECLARED edge to it is not",
        passed=("B", "from") not in named and ("B", "rests-on") not in named,
    )
    check("and a key does not mention itself", passed=not any(other == "A" for other, _f in named))

    # ⚑⚑ THE LONGER-KEY CASE, AND IT IS WHY THE TEST IS NOT A BARE SUBSTRING SEARCH. `M2`'s prose
    # names `A-extended`, which CONTAINS `A` — reporting it as a mention of `A` would make every
    # key a mention of every prefix of itself.
    longer = bib_corpus.compose([Path("w.bib"), Path("long.bib")], _read)
    check(
        "a longer key containing this one is a different subject",
        passed=not [r for r in bib_corpus.mentions(longer, "A") if r[0] == "M2"],
    )
    check(
        "...while the longer key IS found under its own name",
        passed=any(r[0] == "M2" for r in bib_corpus.mentions(longer, "A-extended")),
    )

    # ⚑ SUBSTRING, NOT WORD BOUNDARY — a hyphenated key must be findable, which a regex word
    # boundary would miss at the hyphen.
    check(
        "a hyphenated key is found in prose",
        passed=any(r[0] == "M2" for r in bib_corpus.mentions(longer, "A-extended")),
    )

    check("a key nothing names has no mentions", passed=bib_corpus.mentions(prose, "NOSUCH") == ())

    # ── the empty corpus ─────────────────────────────────────────────────────
    # ⚑ NO ENTRIES IS NOT AN ERROR, and its orphan count is zero for a REASON the caller can
    # state — nothing was read. That distinction belongs to the report layer's denominator.
    empty = bib_corpus.compose([], _read)
    check("an empty corpus composes", passed=empty.entries == {} and empty.collisions == ())
    check("and has no orphans", passed=bib_corpus.orphans(empty) == ())

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"bib-corpus selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
