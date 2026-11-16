# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""The cases for `substrate.heading_key` — including the order-dependence a peer flagged unrun.

⚑⚑⚑ THE ADJACENCY ARMS EXIST BECAUSE A PEER ASKED A QUESTION I HAD NOT ANSWERED. `key` applies its
smart-punctuation table by SUCCESSIVE replacement, so the four classes can interfere: `---` must be
consumed before `--`, and a heading carrying both in sequence exercises that in a way a heading
carrying one never does. summit-13 flagged it and declined to run it because the file was mid-drain;
these are the arms, and one of them would have failed a naive table.

⚑⚑ EVERY CASE ASSERTS A KEY EQUALITY, NEVER A SPELLING. What the module owes its caller is that a
RENDERED heading and its RAW source line produce the same key — not that the key looks any
particular way. A suite asserting the normalised string would pin an implementation detail and
break on a table change that preserved the property.

⚑ AND THE NEGATIVE CONTROL IS LOAD-BEARING. A `key` that collapsed everything to one value would
satisfy every equality arm and anchor a heading to the wrong line, so two genuinely different
headings are asserted to produce DIFFERENT keys.
"""

from __future__ import annotations

import sys

from substrate import heading_key as hk

#: What pandoc renders each raw spelling as — the right-hand side of the comparison.
EM = "\N{EM DASH}"
EN = "\N{EN DASH}"
ELL = "\N{HORIZONTAL ELLIPSIS}"
APOS = "\N{RIGHT SINGLE QUOTATION MARK}"


def _pairs() -> list[tuple[str, str, str]]:
    """Return `(label, raw, rendered)` for each source spelling and what pandoc makes of it."""
    return [
        ("em dash", "Overview --- two layers", f"Overview {EM} two layers"),
        ("en dash", "Range -- inclusive", f"Range {EN} inclusive"),
        ("ellipsis", "Wait ... for it", f"Wait {ELL} for it"),
        ("apostrophe", "cassian's gate", f"cassian{APOS}s gate"),
    ]


def _single_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for one smart-punctuation class at a time."""
    out: list[tuple[str, bool]] = []
    for label, raw, rendered in _pairs():
        got, want = hk.key(raw), hk.key(rendered)
        out.append((f"{label}: raw and rendered agree ({got!r})", got == want))
    return out


def _adjacency_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for headings carrying SEVERAL classes at once.

    ⚑⚑⚑ THE CASE THAT MOTIVATED THIS SUITE. `a --- b -- c` contains `--` inside `---`, so a table
    applied in the wrong order turns the em dash into an en dash followed by a stray hyphen and the
    key stops matching. The dict is ordered longest-first for exactly this, and these arms are what
    make that ordering a checked property rather than a comment.
    """
    out: list[tuple[str, bool]] = []
    cases = [
        ("em then en", "a --- b -- c", f"a {EM} b {EN} c"),
        ("en then em", "a -- b --- c", f"a {EN} b {EM} c"),
        ("ellipsis abutting a dash", "a ...--- b", f"a {ELL}{EM} b"),
        ("dash abutting an ellipsis", "a ---... b", f"a {EM}{ELL} b"),
        ("apostrophe inside a dashed heading", "it's --- here", f"it{APOS}s {EM} here"),
        ("four hyphens are not an em dash plus one", "a ---- b", f"a {EM}- b"),
        ("every class at once", "it's a --- b -- c ... d", f"it{APOS}s a {EM} b {EN} c {ELL} d"),
    ]
    for label, raw, rendered in cases:
        got, want = hk.key(raw), hk.key(rendered)
        out.append((f"{label}: {got!r} vs {want!r}", got == want))
    return out


def _sensitivity_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` proving the adjacency arms would CATCH a wrong table order.

    ⚑⚑⚑ A PASSING ARM SAYS THE ORDER WORKS, NEVER THAT THE ORDER IS LOAD-BEARING. Every adjacency
    case above would also pass against a table that happened to be correct for an unrelated reason,
    so this arm REVERSES the table in a restored-afterwards mutation and asserts the key stops
    matching. Without it, `---` before `--` is a comment claiming to be a checked property.

    ⚑⚑ AND THE MUTATION IS RESTORED IN A `finally`, because a suite that leaves a module mutated
    poisons every case after it and the failure would surface somewhere unrelated.
    """
    out: list[tuple[str, bool]] = []
    raw, rendered = "a --- b -- c", f"a {EM} b {EN} c"
    original = hk.SMART
    try:
        hk.SMART = {"--": EN, "---": EM, "...": ELL, "'": APOS}
        broken = hk.key(raw) == hk.key(rendered)
        wrong = hk.key(raw)
    finally:
        hk.SMART = original

    out.append(
        (f"a shorter-first table BREAKS the match, as the ordering claims: {wrong!r}", not broken)
    )
    out.append(("and the correct table is restored afterwards", hk.key(raw) == hk.key(rendered)))
    return out


def _markup_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the inline-markup class the origin already handled."""
    out: list[tuple[str, bool]] = []
    cases = [
        (
            "backticks",
            "Building the tree: `make -j` self-throttles",
            "Building the tree: make -j self-throttles",
        ),
        ("emphasis", "A *strong* claim", "A strong claim"),
        ("underscore", "A _quiet_ claim", "A quiet claim"),
        (
            "markup and smart punctuation together",
            "`make -j` --- the shim",
            f"make -j {EM} the shim",
        ),
    ]
    for label, raw, rendered in cases:
        got, want = hk.key(raw), hk.key(rendered)
        out.append((f"{label}: {got!r} vs {want!r}", got == want))
    return out


def _idempotence_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for applying the fold to already-rendered text.

    ⚑ THE PROPERTY THAT LETS ONE FUNCTION NORMALISE BOTH SIDES. `fold_smart` run on rendered text
    must find nothing to change, or a caller would have to know which side it held — and a caller
    that has to know is a caller that will eventually be wrong.
    """
    out: list[tuple[str, bool]] = []
    for label, _raw, rendered in _pairs():
        once = hk.fold_smart(rendered)
        out.append((f"{label}: folding rendered text is a no-op", once == rendered))
    twice = hk.key(hk.key("a --- b"))
    out.append((f"key is idempotent on its own output: {twice!r}", twice == hk.key("a --- b")))
    return out


def _control_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the negative controls.

    ⚑ A COLLAPSING KEY PASSES EVERY EQUALITY ARM ABOVE. If `key` returned a constant, every case
    in this suite would be green and every heading would anchor to the first line in the file.
    """
    out: list[tuple[str, bool]] = []
    a, b = hk.key("The first heading"), hk.key("The second heading")
    out.append((f"distinct headings keep distinct keys ({a!r} vs {b!r})", a != b))

    # ⚑ A SINGLE HYPHEN IS NOT SMART PUNCTUATION and must survive — pandoc does not rewrite it,
    # so folding it would make a hyphenated heading fail to match its own source line.
    out.append(("a single hyphen is untouched", hk.key("well-known case") == "well-known case"))

    # ⚑ AND THE MEASURED EXCEPTION IS ASSERTED AS AN EXCEPTION. Double quotes are NOT in the
    # table, and a heading carrying them anchors today. If pandoc's quote transform ever starts
    # breaking anchors, this arm is where the surprise surfaces.
    quoted = hk.key('a "quoted" heading')
    out.append((f"double quotes pass through unfolded: {quoted!r}", '"' in quoted))

    found = hk.unmatched(f"Overview {EM} two layers", ["## Overview --- two layers"])
    out.append((f"unmatched finds the raw line for a rendered heading: {found}", not found))
    missing = hk.unmatched("Nothing like this", ["## Overview --- two layers"])
    out.append((f"and reports a genuine miss: {missing}", missing))
    return out


def _boundary_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the collision a peer predicted — and it does NOT occur.

    ⚑⚑⚑ THE PREDICTION WAS THAT `## The rule --- restated` AND `## The rule -- restated` WOULD
    NORMALISE TO ONE KEY, giving this module a boundary like the one-delegate limit a peer found in
    their own witness. Measured, it does not: the two fold to an em dash and an en dash, which are
    different characters, so the keys differ and the anchorer distinguishes them correctly.

    ⚑⚑ THE PREDICTION WAS SOUND AND ITS PREMISE WAS WRONG, WHICH IS WHY THE ARM IS KEPT. It assumed
    normalisation COLLAPSES the smart-punctuation classes toward a common form; the table MAPS each
    class to a distinct rendered character instead, so information is translated rather than
    discarded. That distinction is invisible from the outside and is exactly what a reader would
    have to re-derive without this case.

    ⚑ WHERE THE MODULE DOES COLLAPSE IS CASE, WHITESPACE AND MARKUP, and those are cased here as
    the real boundary. Two headings differing only in emphasis DO produce one key — deliberately,
    since pandoc erases that difference and the raw line must still match. So the honest statement
    is that this key is lossy on markup and faithful on punctuation, and a caller relying on it to
    distinguish `*a*` from `a` is relying on something it does not promise.
    """
    out: list[tuple[str, bool]] = []

    em, en = hk.key("The rule --- restated"), hk.key("The rule -- restated")
    out.append((f"em-dash and en-dash headings keep DISTINCT keys: {em!r} vs {en!r}", em != en))

    # ⚑ AND THE RENDERED FORMS STAY DISTINCT TOO, which is the half that matters for anchoring:
    # pandoc hands back the rendered spelling, so both sides of the comparison must separate.
    out.append(
        (
            f"and their rendered forms also differ: {hk.key(f'The rule {EM} restated')!r}",
            hk.key(f"The rule {EM} restated") != hk.key(f"The rule {EN} restated"),
        )
    )

    # ⚑⚑ THE REAL COLLAPSE, ASSERTED AS A LIMIT RATHER THAN DISCOVERED AS A SURPRISE. Markup is
    # erased by pandoc, so the key MUST erase it, and two headings differing only there collide.
    marked, plain = hk.key("A *strong* claim"), hk.key("A strong claim")
    out.append((f"markup-only differences DO collide, by design: {marked!r}", marked == plain))
    cased = hk.key("THE RULE") == hk.key("the rule")
    out.append((f"and case-only differences collide too: {cased}", cased))
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _single_cases()
        + _adjacency_cases()
        + _sensitivity_cases()
        + _markup_cases()
        + _idempotence_cases()
        + _boundary_cases()
        + _control_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"heading-key selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
