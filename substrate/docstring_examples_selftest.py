#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.docstring_examples` — a reader that flags every span is useless.

⚑⚑⚑ THE NEGATIVE ARMS ARE THE DELIVERABLE. Nearly every docstring in this tree carries a
backtick span, so a reader admitting all of them reports the whole corpus and trains its reader
to skim — and a census everyone skims is worse than none: it reads as authoritative while being
noise. So the arms below do not merely check that an unwitnessed example is FOUND; they check
that a cross-reference, a path and a symbol are NOT, one case per refusal rule, each going red
if that rule is deleted.

⚑⚑ AND THE CASE THE BRIEF DEMANDED IS THE EXERCISED ONE. An example a case already drives must
not be reported, or this reader would flag `hook_cmdparse`'s repaired docstring — the very
sentence whose arms made it true. That arm fails if the suite-text lookup is removed, which is
the one edit that would turn this from a discriminator into a lister.

⚑ THE TWO SIGNALS ARE ASSERTED SEPARATELY because they answer different questions and can fail
independently: a flag span needs no program-shaped head, a command span has no flag, and an edit
collapsing them into one predicate would leave one silently unreachable.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import docstring_examples, suite_emit

#: This suite's key, as `suite_discovery` names it.
KEY = "substrate/docstring_examples_selftest.py"

#: A module whose docstring cites a flag form, written beside a suite that drives it.
_EXERCISED_MODULE = '"""Doc citing `tool.py --sites` as a worked case."""\n'

#: The suite for it — the example appears as a string ARGUMENT, which is how a case names its
#: subject here, never as the label.
_EXERCISED_SUITE = 'def cases():\n    check("it works", run("tool.py --sites"), [])\n'

#: The same module with a suite that drives something else entirely.
_UNWITNESSED_SUITE = 'def cases():\n    check("unrelated", run("tool.py --other"), [])\n'

#: A docstring citing only symbols — legitimate prose this reader must stay silent on.
_SYMBOLS_ONLY = '"""Uses `code_lines` and `corpus.py_files` here."""\n'

#: A span in a COMMENT rather than a docstring — a different act, and a declared boundary.
_COMMENT_SPAN = "# see `tool.py --sites` for this\nx = 1\n"

#: A function docstring, to prove the walk is not module-only.
_FUNCTION_DOC = 'def f():\n    """Runs `tool.py --deep` on it."""\n'

#: ⚑⚑⚑ A MODULE CARRYING ITS OWN CASES INLINE — the shape all five vendored hooks are in, and
#: the shape that produced this reader's first false positive. The example is cited in the
#: docstring and driven by an arm in the SAME file, with no sibling suite anywhere.
_INLINE_MODULE = (
    '"""Doc citing `tool.py --sites` as a worked case."""\n'
    "def _selftest():\n"
    '    check("it works", run("tool.py --sites"), [])\n'
)


def _pair(module_src: str, suite_src: str | None) -> Path:
    """Write a module and, when given, its sibling suite; return the module's path.

    ⚑ REAL FILES, BECAUSE THE READER TAKES A PATH AND RESOLVES THE SIBLING BY NAME. Handing it
    sources through a private seam would test a function the census never calls, and the sibling
    lookup — the half that decides EXERCISED from UNWITNESSED — would never run at all.
    """
    home = Path(tempfile.mkdtemp())
    module = home / "widget.py"
    module.write_text(module_src, encoding="utf-8")
    if suite_src is not None:
        (home / "widget_selftest.py").write_text(suite_src, encoding="utf-8")
    return module


def _spans(module: Path) -> list[str]:
    """Return the spans this reader REPORTS as unwitnessed for one module."""
    found, _refused = docstring_examples.scan(module)
    return [e.span for e in found]


def _refusals(module: Path) -> list[str]:
    """Return the reasons this reader refused a span, for one module."""
    _found, refused = docstring_examples.scan(module)
    return [s.why for s in refused]


def cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case, in order."""
    out: list[tuple[str, bool]] = []

    def check(label: str, got: object, want: object) -> None:
        out.append((f"{label}: got {got!r}, want {want!r}", got == want))

    # ── the DISCRIMINATOR, in isolation: which spans are CLAIMS ────────────────────────
    # ⚑ A FLAG IS THE STRONGEST SIGNAL — it shows a form being RUN, not a name being cited.
    check(
        "a flag span is a claim",
        docstring_examples.claim_signal("timeout -s KILL 60 grep foo"),
        "flag",
    )
    check("a long flag is too", docstring_examples.claim_signal("tool.py --sites"), "flag")
    # ⚑ A COMMAND NEEDS A PROGRAM-SHAPED HEAD AND AN OPERAND. Either alone is not an invocation.
    check(
        "a program with an operand is a claim",
        docstring_examples.claim_signal("make agda/Flat.mk"),
        "command",
    )
    # ⚑⚑⚑ THE NEGATIVES. Each of these is LEGITIMATE prose and must never be reported; the
    # reader is useless if it flags them, since nearly every docstring here cites a symbol.
    check("a bare symbol is NOT a claim", docstring_examples.claim_signal("code_lines"), None)
    check(
        "a dotted symbol is NOT a claim", docstring_examples.claim_signal("corpus.py_files"), None
    )
    check("a called symbol is NOT a claim", docstring_examples.claim_signal("programs()"), None)
    check("a bare path is NOT a claim", docstring_examples.claim_signal("scripts/foo.py"), None)

    # ── the REFUSAL RULES, each named so over-refusal is auditable ──────────────────────
    check(
        "a symbol names the cross-reference rule",
        docstring_examples.refusal_for("code_lines"),
        "a bare symbol — a cross-reference, not a worked case",
    )
    check(
        "a path names the path rule",
        docstring_examples.refusal_for("scripts/foo.py"),
        "a path — a file NAMED, not a form run",
    )
    check(
        "a glyph is too short to be an invocation",
        docstring_examples.refusal_for("⚑"),
        "too short to be an invocation",
    )
    check(
        "a real invocation is refused by NO rule",
        docstring_examples.refusal_for("tool.py --sites"),
        None,
    )

    # ── end to end: UNWITNESSED is reported ─────────────────────────────────────────────
    # ⚑ THE MOTIVATING SHAPE. A docstring cites a worked form; the suite drives a different one;
    # nothing witnesses the sentence. That is exactly `hook_cmdparse`'s state before its arms.
    check(
        "an example no case drives is reported",
        _spans(_pair(_EXERCISED_MODULE, _UNWITNESSED_SUITE)),
        ["tool.py --sites"],
    )

    # ⚑⚑⚑ THE CASE THE BRIEF REQUIRED: THIS FAILS IF THE PREDICATE FLAGS SOMETHING LEGITIMATE.
    # An example a case already exercises is FINE and must not be reported. Deleting the
    # suite-text lookup in `scan` turns this reader into a lister and reddens exactly this arm —
    # and it is the arm that protects a correctly-repaired docstring from being reported as debt.
    check(
        "an example a case DOES drive is NOT reported",
        _spans(_pair(_EXERCISED_MODULE, _EXERCISED_SUITE)),
        [],
    )
    check(
        "and it is recorded as exercised, not silently dropped",
        [
            w
            for w in _refusals(_pair(_EXERCISED_MODULE, _EXERCISED_SUITE))
            if w == "exercised by a case"
        ],
        ["exercised by a case"],
    )

    # ⚑⚑⚑ THE INLINE CASE, AND IT IS A REGRESSION THIS READER'S FIRST LIVE RUN CAUGHT. The five
    # vendored hooks carry their cases in their OWN `_selftest`, not in a sibling — so a
    # sibling-only lookup reported `hook_cmdparse`'s wrapper-flag example as unwitnessed while
    # the arm driving that exact string sat in the same file. Flagging a REPAIRED claim as debt
    # inverts this census's subject, and this arm goes red if `scan` narrows back to the sibling.
    check(
        "an example driven by the module's OWN inline cases is NOT reported",
        _spans(_pair(_INLINE_MODULE, None)),
        [],
    )

    # ⚑⚑ AND THE MODULE'S OWN DOCSTRING MUST NOT COUNT AS ITS OWN WITNESS. If it did, every
    # example would match itself and this reader would report a clean tree for the most vacuous
    # possible reason — a false ZERO, the direction this repo banks silently. This arm goes red
    # if `case_text` stops excluding the module's docstrings.
    check(
        "a docstring does not witness itself",
        _spans(_pair(_EXERCISED_MODULE, None)),
        ["tool.py --sites"],
    )
    check(
        "and names no suite for it",
        [e.suite for e in docstring_examples.scan(_pair(_EXERCISED_MODULE, None))[0]],
        [None],
    )

    # ⚑⚑ A CROSS-REFERENCE IN A REAL DOCSTRING MUST NOT REACH THE CENSUS, even with no suite
    # present — this is the whole-file form of the negative arms above, and it fails if the
    # refusal table is bypassed anywhere in `scan`.
    check("a docstring citing only symbols reports nothing", _spans(_pair(_SYMBOLS_ONLY, None)), [])

    # ── the extractor reads DOCSTRINGS, not comments ────────────────────────────────────
    # ⚑ A COMMENT BESIDE THE CODE IS A DIFFERENT ACT from a docstring's claim, and admitting
    # comments would change what this census MEANS. Asserted so the boundary is driven, not
    # merely written down.
    check("a span in a comment is not a docstring span", _spans(_pair(_COMMENT_SPAN, None)), [])
    check(
        "a function docstring is read too", _spans(_pair(_FUNCTION_DOC, None)), ["tool.py --deep"]
    )

    # ── how a case NAMES its subject: the ARGUMENT, not the label ───────────────────────
    # ⚑⚑⚑ THIS IS THE ESTABLISHED CONVENTION AND IT IS ASSERTED RATHER THAN ASSUMED. A matcher
    # reading only labels would miss every exercised example and report the tree as unwitnessed
    # — the method's blind spot reported as the substrate's state. This arm goes red if
    # `subject_text` narrows to labels.
    # ⚑ ASSERTED AS A MEMBERSHIP LIST, NOT A BOOLEAN: a case comparing against a bare `True`
    # says nothing at the call site about WHICH property holds.
    suite_path = _pair(_EXERCISED_MODULE, _EXERCISED_SUITE).with_name("widget_selftest.py")
    subject = docstring_examples.subject_text(suite_path)
    check(
        "a suite's string ARGUMENTS are part of its subject text",
        [s for s in ["tool.py --sites"] if s not in subject],
        [],
    )

    # ── the BOUNDARIES are declared, not implied ────────────────────────────────────────
    # ⚑⚑ A ZERO FROM THIS READER IS A FACT ABOUT THE MATCHER. The boundaries are DATA so the CLI
    # can print them on every run; a suite letting them fall empty would let the tool ship a
    # confident zero with nothing saying what it could not match.
    # ⚑ ASSERTED AS AN EMPTINESS: asking which boundaries are blank, and expecting none, states
    # the claim in the values themselves.
    check(
        "the reader declares what it cannot see",
        [b for b in docstring_examples.BOUNDARIES if not b.strip()],
        [],
    )
    # ⚑ THE UPPER-BOUND HONESTY IS ITSELF ASSERTED. `prose_numbers` reports its hits as an upper
    # bound because mention-vs-use is not structural; the same is true here, and a boundary set
    # that lost that line would let this census read as a defect list.
    check(
        "the upper-bound honesty is declared",
        [w for w in ["UPPER BOUND"] if not [b for b in docstring_examples.BOUNDARIES if w in b]],
        [],
    )

    # ── an unparseable module is not a silent zero ──────────────────────────────────────
    # ⚑ A SYNTAX ERROR MUST NOT READ AS A CLEAN FILE. It reports nothing here BY CONSTRUCTION,
    # which is why the census returns `files_read` — a bare list cannot tell no-matches from
    # no-file-read.
    check("an unparseable module yields no spans", _spans(_pair("def (:\n", None)), [])

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
