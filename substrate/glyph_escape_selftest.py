# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""The cases for `substrate.glyph_escape` — over the REAL roster prose, not invented strings.

⚑⚑⚑ THE LIVE ARM RUNS ON THE CONTENT THIS EXISTS TO MOVE. A fixture of my own devising proves
the escaper handles glyphs I thought of; only the actual worklist descriptions prove it handles
the ones the corpus uses. The transformation is applied in memory and discarded — nothing here
writes.

⚑⚑ AND EVERY VERDICT PRINTS ITS COMPONENTS, which is an operator ruling: *anywhere you assert an
expression, you must print the expression's components — that makes it a [dis]proof-carrying
artifact.* So a failing arm here does not say "did not round-trip"; it names the index, the
original slice and the decoded slice, because a failure nobody can read is a complaint rather
than a disproof.

⚑⚑⚑ AND THIS SUITE WRITES ITS OWN FIXTURES IN THE ESCAPES IT TESTS, because the gate refused it
otherwise — a file containing the flagged glyphs literally is itself flagged. That is the remedy
applied at a third layer (module docstring, then this suite's data), and it is a stronger check
than the one I designed: the fixtures are only correct if the escape spelling really does denote
the character, so a wrong escape breaks the arms rather than passing them.

⚑ THE NEGATIVE CONTROL IS LOAD-BEARING. An escaper that returned its input unchanged would round
-trip perfectly and clear nothing, so the cases assert the output ACTUALLY CHANGED and that the
flagged glyph is gone from the source — two facts a round-trip check alone cannot distinguish.
"""

from __future__ import annotations

import sys

from substrate import glyph_escape as ge

#: The characters ruff flags in the live roster, taken from its own findings rather than guessed:
#: `pycheck_show scripts/worklist.py` names each one in a RUF001/RUF002 message.
#: ⚑ SPELLED AS ESCAPES because this file would otherwise carry the very glyphs it is about.
FLAGGED = frozenset(
    "\N{DOUBLE-STRUCK CAPITAL Z}\N{DOUBLE-STRUCK CAPITAL R}\N{DOUBLE-STRUCK CAPITAL N}"
    "\N{GREEK CAPITAL LETTER IOTA}\N{GREEK CAPITAL LETTER BETA}"
    "\N{GREEK CAPITAL LETTER EPSILON}\N{DIVIDES}"
)

#: One flagged character, named once so the arms below read as claims about a character rather
#: than about a spelling.
ZED = "\N{DOUBLE-STRUCK CAPITAL Z}"

#: Prose taken VERBATIM from the live worklist roster — the hardest real input, carrying several
#: flagged glyphs, an em dash, and mathematical operators that are NOT flagged.
LIVE_PROSE = (
    f"full {ZED}-power ExpLogCodec (ZPow.{ZED}-power-codec): L={ZED} group via "
    f"_+{ZED}_, expL z=g\N{MODIFIER LETTER SMALL Z}, mixed-sign exp-\N{CIRCLED PLUS} "
    "\N{EM DASH} codec-antipode fires non-trivially"
)


def _escape_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the character-level substitution."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    got = ge.escape_name(ZED)
    check(f"a flagged glyph names itself: {got!r}", passed=got == "\\N{DOUBLE-STRUCK CAPITAL Z}")

    # ⚑⚑ AN UNFLAGGED GLYPH MUST SURVIVE UNTOUCHED. Escaping everything non-ASCII would make the
    # record unreadable while clearing no finding — the transformation is driven by the checker's
    # objections, not by a character being unusual.
    plain = "\N{RIGHTWARDS ARROW} \N{CIRCLED PLUS} \N{BLACK FLAG}"
    kept = ge.escape_chars(plain, FLAGGED)
    check(f"unflagged glyphs are untouched: {kept!r}", passed=kept == plain)

    swapped = ge.escape_chars(f"x {ZED} y", FLAGGED)
    check(
        f"a flagged glyph is replaced: {swapped!r}",
        passed=swapped == "x \\N{DOUBLE-STRUCK CAPITAL Z} y",
    )
    # ⚑ AND THE SURROUNDING BYTES ARE EXACT — the spaces and the ASCII survive in place.
    check(
        "the surrounding bytes are exact",
        passed=swapped.startswith("x ") and swapped.endswith(" y"),
    )

    # ⚑ AN UNNAMEABLE CHARACTER IS KEPT, NOT DROPPED. A surrogate has no Unicode name, so this is
    # the branch where a careless implementation would silently lose content.
    lone = "\udc80"
    check(
        f"an unnameable char has no escape: {ge.escape_name(lone)!r}",
        passed=ge.escape_name(lone) is None,
    )
    check(
        "and is kept rather than dropped",
        passed=ge.escape_chars(f"a{lone}b", frozenset({lone})) == f"a{lone}b",
    )
    found = ge.unescapable(frozenset({lone, ZED}))
    check(f"unescapable reports it up front: {len(found)} of 2", passed=found == frozenset({lone}))

    return out


def _backslash_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for text carrying backslashes the escaper never wrote.

    ⚑⚑⚑ THE FIXTURE WHOSE ABSENCE HID A REAL DEFECT (gate-G212). Every case in this suite was
    backslash-free, so a verifier that decoded EVERY escape sequence — not only the ones this
    module emits — read 22/22 while reporting a false divergence on the live roster, which
    carries a pre-existing escaped quote. The suite passed on inputs its author chose and failed
    on the corpus it was built for.

    ⚑⚑ SO THESE ARMS ARE THE REPAIR'S ONLY REAL EVIDENCE. A targeted inverse and a general
    decoder agree on every input WITHOUT a foreign backslash; they differ exactly here.
    """
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ⚑ THE EXACT SHAPE THE ROSTER CARRIES: an escaped quote inside a string, beside a flagged
    # glyph that must still be escaped.
    quoted = f'a {ZED} and a \\" quote'
    trip = ge.round_trip(quoted, FLAGGED)
    check(f"text with a pre-existing escaped quote round-trips — {trip.why()}", passed=trip.ok)
    check("and the foreign backslash SURVIVES in the source", passed='\\"' in trip.escaped)
    check(
        "while the flagged glyph is still escaped",
        passed="\\N{DOUBLE-STRUCK CAPITAL Z}" in trip.escaped,
    )

    # ⚑⚑ A LONE BACKSLASH AND A NEWLINE ESCAPE — the other sequences a general decoder would
    # resolve. Each must pass through untouched, because this module never wrote them.
    for label, sample in (
        ("a newline escape", f"line\\n{ZED}"),
        ("a tab escape", f"col\\t{ZED}"),
        ("a doubled backslash", f"path\\\\to\\\\{ZED}"),
    ):
        got = ge.round_trip(sample, FLAGGED)
        check(f"{label} round-trips — {got.why()}", passed=got.ok)

    # ⚑⚑⚑ THE POSITIVE CONTROL FOR THE REPAIR ITSELF: the inverse must actually undo the escape,
    # not merely leave everything alone. A no-op inverse would pass every arm above.
    check(
        "the inverse undoes the escape",
        passed=ge.unescape_chars(ge.escape_chars(f"q {ZED}", FLAGGED), FLAGGED) == f"q {ZED}",
    )
    check(
        "and leaves a foreign escape alone",
        passed=ge.unescape_chars('\\" kept', FLAGGED) == '\\" kept',
    )

    return out


def _trip_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the round-trip verdict and its components."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    simple = f"x {ZED} y"
    trip = ge.round_trip(simple, FLAGGED)
    check(f"a simple escape round-trips — {trip.why()}", passed=trip.ok)
    # ⚑⚑ THE VERDICT CARRIES ITS COMPONENTS, asserted rather than assumed: a `Trip` whose fields
    # were empty would still report `ok` and tell a reader nothing.
    check(
        f"and carries the escaped source ({len(trip.escaped)} chars)",
        passed=bool(trip.escaped) and trip.escaped != trip.text,
    )
    check("and carries the decoded text", passed=trip.decoded == simple)
    check("and names no divergence point when equal", passed=trip.at is None)

    # ⚑⚑⚑ THE DISPROOF SIDE. A verdict type that could only report success would satisfy every
    # arm above, so a deliberately broken pair is checked to produce a READABLE failure.
    broken = ge.Trip("abc", "abd", "abd", ge.first_difference("abc", "abd"))
    check(f"a divergence is located: {broken.why()}", passed=not broken.ok and broken.at == 2)  # noqa: PLR2004 — the fixture's own index
    check("and the reason names both sides", passed="vs decoded" in broken.why())
    undec = ge.Trip("x", "\\N{NO SUCH NAME}", None, None)
    check(
        f"an undecodable escape reports as such: {undec.why()}",
        passed=not undec.ok and "UNDECODABLE" in undec.why(),
    )

    check(
        "first_difference returns None for equal strings",
        passed=ge.first_difference("same", "same") is None,
    )
    check(
        "and the shorter length when one is a prefix", passed=ge.first_difference("ab", "abc") == 2
    )  # noqa: PLR2004 — the fixture's length

    return out


def _live_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` over prose taken verbatim from the live roster.

    ⚑⚑⚑ THIS IS THE ARM THAT MATTERS, because the escaper's job is to move THIS content. Every
    component is printed: how many flagged characters were found, the round-trip verdict with its
    divergence point if any, and the proof that the output actually changed.
    """
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    present = sorted(c for c in FLAGGED if c in LIVE_PROSE)
    check(f"the live prose carries {len(present)} distinct flagged glyph(s)", passed=bool(present))

    blocked = ge.unescapable(frozenset(present))
    check(f"and every one of them is nameable ({len(blocked)} unescapable)", passed=not blocked)

    trip = ge.round_trip(LIVE_PROSE, FLAGGED)
    check(f"the live prose round-trips — {trip.why()}", passed=trip.ok)

    # ⚑ THE POSITIVE CONTROL: an escaper that did nothing would round-trip perfectly and clear no
    # finding, so assert the source CHANGED and no flagged glyph survives in it.
    check(
        f"the escaped source differs from the original "
        f"({len(LIVE_PROSE)} -> {len(trip.escaped)} chars)",
        passed=trip.escaped != LIVE_PROSE,
    )
    left = sorted(c for c in FLAGGED if c in trip.escaped)
    check(f"and {len(left)} flagged glyph(s) remain in the source", passed=not left)

    # ⚑⚑ THE UNFLAGGED MATHEMATICS SURVIVES IN THE SOURCE. The em dash and the circled-plus are
    # content too, and escaping them would be damage that clears nothing.
    unflagged = ("\N{CIRCLED PLUS}", "\N{EM DASH}")
    kept = [c for c in unflagged if c in trip.escaped]
    check(
        f"unflagged mathematics survives unescaped: {len(kept)} of {len(unflagged)}",
        passed=len(kept) == len(unflagged),
    )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _escape_cases() + _backslash_cases() + _trip_cases() + _live_cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"glyph-escape selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
