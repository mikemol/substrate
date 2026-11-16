#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.prose_numbers` — a discriminator that flags everything is useless.

⚑⚑⚑ EVERY POSITIVE ARM IS PAIRED WITH A NEGATIVE ONE, AND THE NEGATIVES ARE THE POINT. A reader
that flags a line reference, a date, a version pin or a label ordinal trains its reader to skim,
and a census everyone skims is worse than no census: it reads as authoritative while being
noise. So the arms below do not merely check that a measured number is FOUND — they check that
an ordinary number is NOT, one case per exemption, each of which goes red if that exemption is
deleted.

⚑⚑ THE DISCRIMINATOR IS THE DELIVERABLE, SO THE CASES ARE ABOUT IT AND NOT ABOUT THE WALK.
Extracting prose is `code_lines`' problem and is already proven by its own suite; what is new
here is the judgement about which NUMBER is a measurement. A suite that mostly exercised the
corpus walk would report green on the half nobody doubted.

⚑ THE TWO SIGNALS ARE ASSERTED SEPARATELY because they answer different questions and can fail
independently: a ratio needs no unit noun, a unit hit needs one, and an edit collapsing them
into a single predicate would leave one of the two silently unreachable.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import prose_numbers, suite_emit

#: This suite's key, as `suite_discovery` names it.
KEY = "substrate/prose_numbers_selftest.py"


def tmp_python() -> Path:
    """Write a two-line python fixture — one comment, one statement — and return its path.

    ⚑ A REAL FILE, BECAUSE THE EXTRACTOR TAKES A PATH AND TOKENIZES IT. Handing the tokenizer
    a string through a private seam would test a function the census never calls.
    """
    path = Path(tempfile.mkdtemp()) / "fixture.py"
    path.write_text("# 56 cases\nx = 1\n", encoding="utf-8")
    return path


def tmp_markdown() -> Path:
    """Write a markdown fixture whose fence hides a number, and return its path."""
    path = Path(tempfile.mkdtemp()) / "fixture.md"
    path.write_text("56 cases ran\n\n```\n999 rows inserted\n```\n", encoding="utf-8")
    return path


def _numbers(text: str) -> list[str]:
    """Return the numbers `scan_line` flags in one line of prose."""
    found, _refused = prose_numbers.scan_line("t.py", 1, text)
    return [f.number for f in found]


def _refusals(text: str) -> list[str]:
    """Return the exemption names that refused a number in one line of prose."""
    _found, refused = prose_numbers.scan_line("t.py", 1, text)
    return [e.why for e in refused]


def cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case, in order."""
    out: list[tuple[str, bool]] = []

    def check(label: str, got: object, want: object) -> None:
        out.append((f"{label}: got {got!r}, want {want!r}", got == want))

    # ── the UNIT signal: a number beside a noun some tool re-derives ────────────────────
    check("a count beside a unit noun is measured", _numbers("a 56 case suite"), ["56"])
    check("the plural spelling too", _numbers("57 cases ran"), ["57"])
    # ⚑ AN ADJECTIVE BETWEEN THE NUMBER AND ITS NOUN DOES NOT STOP IT BEING A MEASUREMENT.
    # An adjacency-only matcher misses "57 green cases", which is how these are actually
    # written, so the two-word gap is asserted rather than left to chance.
    check("an adjective between number and noun is spanned", _numbers("57 green cases ran"), ["57"])
    check("two intervening words still reach the noun", _numbers("8 newly declared gates"), ["8"])

    # ⚑⚑⚑ THE BRIEF'S OWN WORKED EXAMPLE, PINNED — AND THE FIRST CUT MISSED IT. The measured
    # instance this reader was commissioned to find is `suite_declared.py`'s `why=`, reading
    # "a 56-case suite". A hyphen makes `56-case` ONE token, so a word-gap scan has no
    # whitespace to cross and reported nothing; the file still appeared in the census on the
    # strength of a DIFFERENT line, so the miss was invisible from the output. A census that
    # misses its own worked example is a fact about the METHOD — which is why the example
    # belongs in a case rather than only in the brief.
    check("a hyphen-bound unit is measured", _numbers("a 56-case suite"), ["56"])
    check("a hyphen-bound non-unit is not", _numbers("a 3-way split"), [])
    # ⚑ AND IT MUST NOT DOUBLE-REPORT. The hyphen arm and the word-gap arm can both reach the
    # same number when a unit noun also follows; one written figure is one finding.
    check(
        "a hyphen-bound unit followed by another unit reports once",
        _numbers("a 56-case suite of cases"),
        ["56"],
    )

    # ── the RATIO signal: needs no unit noun at all ─────────────────────────────────────
    # ⚑ A SEPARATE SIGNAL, and requiring a unit word would miss it entirely — which matters
    # because `N of M` is the form this repo's tools PRINT and therefore the form a writer
    # copies into prose.
    check("N of M is measured with no unit noun", _numbers("59 of 130 were unread"), ["59/130"])
    check("N/M is measured too", _numbers("the suite went 55/56"), ["55/56"])
    # ⚑ ONE WRITTEN FIGURE IS ONE FINDING. "59 of 130 files" must not report twice — under
    # double-counting every holder's total inflates by however often its author wrote a ratio,
    # which is a fact about phrasing rather than about drift.
    check(
        "a ratio carrying a unit noun is ONE finding, not two",
        _numbers("59 of 130 files"),
        ["59/130"],
    )

    # ── the NEGATIVES. Each goes red if its exemption is deleted. ───────────────────────
    # ⚑⚑⚑ THE LINE REFERENCE IS THE CASE THE BRIEF NAMED, and it is the most common number in
    # this corpus's commentary. Without this exemption the census is almost entirely citations.
    check(
        "a path-and-line reference is NOT measured",
        _numbers("see scripts/foo.py:107 for the branch"),
        [],
    )
    check("a symbol-and-line reference is NOT measured", _numbers("the rule is membudget:104"), [])
    check("a line RANGE is NOT measured", _numbers("membudget:104-112 is the rule"), [])
    # ⚑ A DATE IS A STAMP: it does not drift, it ages. Flagging one would put every dated
    # incident note in this repo into the census.
    check("a date is NOT measured", _numbers("corrected 2026-09-03 after a re-read"), [])
    check("a bare year is NOT measured", _numbers("measured in 2026 by the gate"), [])
    # ⚑ AN IDENTIFIER CARRYING DIGITS NAMES A THING RATHER THAN COUNTING ONE.
    check("a version pin is NOT measured", _numbers("pinned at 1.2.3 for the run"), [])
    check("a PEP number is NOT measured", _numbers("a PEP 508 direct reference"), [])
    check("an error code is NOT measured", _numbers("refused by SC2012 today"), [])
    check("a label ordinal is NOT measured", _numbers("Ⓝ133 names the thread"), [])
    check("a size unit is NOT measured", _numbers("capped at 128 MiB per module"), [])
    # ⚑ A NUMBER IN A CODE SPAN IS AN INVOCATION'S ARGUMENT, not a claim the prose is making.
    check(
        "a number inside a code span is NOT measured",
        _numbers("run it with `--min 3` to widen"),
        [],
    )

    # ⚑⚑ AND THE EXEMPTIONS MUST NOT EAT A REAL MEASUREMENT ON THE SAME LINE. This is the arm
    # that catches an over-broad exemption: masking preserves length, so a genuine count sitting
    # beside a citation still reports. A delete-the-span implementation passes every case above
    # and fails this one.
    check(
        "a measured number SURVIVES beside a line reference",
        _numbers("scripts/foo.py:107 declares 56 cases"),
        ["56"],
    )
    check("and beside a date", _numbers("on 2026-09-03 the census read 42 modules"), ["42"])

    # ── the REFUSALS are reported, so the discriminator can be audited ──────────────────
    # ⚑ AN INSTRUMENT THAT CANNOT SAY WHICH RULE REFUSED CANNOT BE CHECKED FOR OVER-REFUSAL,
    # and over-refusal is invisible in the census by construction: it makes the tree look clean.
    check("a refusal names its rule", _refusals("see scripts/foo.py:107"), ["line reference"])
    check("a date refusal names the date rule", _refusals("on 2026-09-03"), ["date"])
    check("nothing is refused when nothing is exempt", _refusals("56 cases"), [])

    # ── rhetorical enumeration is NOT a measurement ─────────────────────────────────────
    # ⚑ "3 ways" and "2 halves" are the writer's own structure, which no tool re-derives and
    # which therefore cannot drift. Admitting them would swamp the census with prose the rule
    # has no claim on — the reason `UNIT_WORDS` is narrow rather than "every noun".
    check("a number beside a non-unit noun is not measured", _numbers("there are 3 ways in"), [])
    check("even when the noun is plural", _numbers("the 2 halves disagree"), [])

    # ── the BOUNDARIES are declared, not implied ────────────────────────────────────────
    # ⚑⚑ A ZERO FROM THIS READER IS A FACT ABOUT THE DISCRIMINATOR. The boundaries are DATA so
    # the CLI can print them on every run; a suite that let them fall empty would let the tool
    # ship a confident zero with nothing saying what it could not match.
    # ⚑ ASSERTED AS AN EMPTINESS, NOT AS A BOOLEAN. A case comparing against a bare `True`
    # says nothing at the call site about WHICH property holds; asking for the boundaries that
    # are empty, and expecting none, states the claim in the values themselves.
    check(
        "the reader declares what it cannot see",
        [b for b in prose_numbers.BOUNDARIES if not b.strip()],
        [],
    )
    check("every exemption carries a name", [n for n, _rx in prose_numbers.EXEMPTIONS if not n], [])
    # ⚑ THE WORD-COUNT BOUNDARY IS REAL AND IS ASSERTED AS SUCH, rather than left for a reader
    # to discover as a surprise: a count spelled in words is invisible here BY DESIGN, because
    # number words cannot be told from rhetorical enumeration structurally.
    check(
        "a count spelled in WORDS is invisible, as declared",
        _numbers("a three case suite existed"),
        [],
    )

    # ── the prose extractors read the right half of each artifact ──────────────────────
    # ⚑⚑ A COMMENT IS PROSE AND A STATEMENT IS NOT. These DRIVE the extractors over a real
    # file rather than trusting them: an inversion would make the census read code and miss
    # every comment, which looks like a small population rather than a broken extractor.
    src = tmp_python()
    check(
        "a comment line is prose",
        [t for _i, t in prose_numbers.python_prose(src) if t.startswith("#")],
        ["# 56 cases"],
    )
    check(
        "a statement is NOT prose",
        [t for _i, t in prose_numbers.python_prose(src) if t.startswith("x =")],
        [],
    )

    # ⚑ A FENCED BLOCK IS A TRANSCRIPT, NOT A CLAIM. Admitting fences would make the markdown
    # census mostly recorded tool output — the one place a number is SUPPOSED to be.
    doc = tmp_markdown()
    fenced = [t for _i, t in prose_numbers.markdown_prose(doc) if "999" in t]
    check("a number inside a markdown fence is not read as prose", fenced, [])
    body = [t for _i, t in prose_numbers.markdown_prose(doc) if "56" in t]
    check("a number in the body IS read as prose", body, ["56 cases ran"])

    return out


def selftest() -> int:
    """Run every case and report through the typed record; return 0 when all pass."""
    rows = cases()
    bad = [label for label, ok in rows if not ok]
    for label in bad:
        sys.stderr.write(f"  FAIL {label}\n")
    return suite_emit.report(KEY, len(rows) - len(bad), len(rows))


if __name__ == "__main__":
    raise SystemExit(selftest())
