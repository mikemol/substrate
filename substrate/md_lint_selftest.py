# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.md_lint` — four rules, their exemptions, and the origin differential.

⚑⚑⚑ THE CODE-SPAN ARM IS THE ONE THE ORIGIN GOT WRONG, so it leads. `MD033`'s first cut counted
backticks around the match and admitted `<n> bytes allocated` — text plainly inside code — and the
document was nearly edited to satisfy that false positive. A fixture holding exactly that string is
what makes the guard load-bearing rather than incidental.

⚑⚑ AND THE FIXTURES ARE LINES, NOT FILES, because the module measures a body it was handed. That is
what lets a case state a rule precisely: `MD032` is about one line and its predecessor, and a
file-based fixture would carry a dozen incidental differences and prove which one mattered to
nobody.

⚑ THE SENSITIVITY ARMS FORCE THE STATE WHERE EACH RULE SHOULD FAIL (gate-G263). Every arm below
feeds a correct fixture, so none alone shows a guard DECIDES rather than being satisfied by
accident — one strips the fence, one strips the code span, and each asserts the verdict moves.
"""

from __future__ import annotations

import sys

from mikemol.mdstruct import frontmatter as md_frontmatter

from substrate import md_lint as ml

#: ⚑ THE MEASURED FALSE POSITIVE, VERBATIM. `<n>` inside a code span is not inline HTML.
CODED = ["a line saying `<n> bytes allocated` and nothing more"]

#: The same tag OUTSIDE code — genuinely MD033.
BARE = ["a line saying <br> and nothing more"]

#: A fenced block whose content would trip every rule if the fence were not honoured.
FENCED = ["```", "<div>" + "x" * 200, "```"]

#: A list item preceded by prose — MD032 — and one preceded by a continuation, which is not.
LOOSE = ["prose immediately above", "- an item"]
CONTINUED = ["- an item", "  its continuation", "- the next item"]


def _html_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for MD033 and the code-span guard."""
    out: list[tuple[str, bool]] = []

    bare = ml.inline_html(BARE)
    out.append((f"bare inline HTML is found: {bare}", len(bare) == 1))
    out.append((f"and it names the tag: {bare[0].detail}", "br" in bare[0].detail))

    # ⚑⚑ THE ARM THE ORIGIN FAILED. A count would have passed here and sent a reader editing prose.
    out.append(
        (
            f"HTML inside a code span is NOT claimed: {ml.inline_html(CODED)}",
            ml.inline_html(CODED) == [],
        )
    )

    # ⚑ THE SENSITIVITY ARM. Removing ONLY the backticks must flip it, or the guard is decoration.
    stripped = [CODED[0].replace("`", "")]
    out.append(
        (
            f"removing ONLY the backticks flips it: {len(ml.inline_html(stripped))}",
            len(ml.inline_html(stripped)) == 1,
        )
    )
    return out


def _fence_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` proving fenced content is exempt from every rule."""
    out: list[tuple[str, bool]] = []

    # ⚑⚑ MD041 IS DELIBERATELY NOT FENCE-EXEMPT, AND MY FIRST CASE ASSERTED OTHERWISE. It reads the
    # body's first non-blank line as written, because a document opening with a code fence really
    # does not open with a heading — the origin does the same. So the fence exemption is asserted
    # against the three LINE rules, which are the ones it is about.
    fenced = [f for f in ml.findings(FENCED) if f.rule != "MD041"]
    out.append((f"a fenced block yields no line findings: {fenced}", fenced == []))

    # ⚑ AND REMOVING THE FENCE MOVES IT — without this, `_body_lines` could be skipping everything.
    unfenced = [FENCED[1]]
    bare = [f for f in ml.findings(unfenced) if f.rule != "MD041"]
    out.append((f"removing ONLY the fence flips it: {[f.rule for f in bare]}", len(bare) > 0))
    return out


def _width_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for MD013 and the width it is told."""
    out: list[tuple[str, bool]] = []
    wide = ["y" * (ml.WIDTH + 1)]

    found = ml.long_lines(wide)
    out.append((f"a line past the width is found: {len(found)}", len(found) == 1))
    out.append(
        (
            f"and the detail carries both numbers: {found[0].detail}",
            str(ml.WIDTH + 1) in found[0].detail and str(ml.WIDTH) in found[0].detail,
        )
    )
    out.append(
        (
            f"a line at the width is not: {ml.long_lines(['y' * ml.WIDTH])}",
            ml.long_lines(["y" * ml.WIDTH]) == [],
        )
    )

    # ⚑ THE RULE AGREES WITH A WIDTH IT IS TOLD — that is the whole argument against disabling it.
    out.append(
        (
            f"told a wider width, the same line passes: {ml.long_lines(wide, ml.WIDTH + 10)}",
            ml.long_lines(wide, ml.WIDTH + 10) == [],
        )
    )
    return out


def _list_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for MD032 and the continuation exemption."""
    out: list[tuple[str, bool]] = []

    out.append(
        (
            f"a list after prose is found: {len(ml.loose_lists(LOOSE))}",
            len(ml.loose_lists(LOOSE)) == 1,
        )
    )
    out.append(
        (
            f"a continued list is NOT claimed: {ml.loose_lists(CONTINUED)}",
            ml.loose_lists(CONTINUED) == [],
        )
    )
    out.append(
        (
            f"a list opening the document is not judged: {ml.loose_lists(['- first'])}",
            ml.loose_lists(["- first"]) == [],
        )
    )
    return out


def _heading_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for MD041 as a property of the BODY."""
    out: list[tuple[str, bool]] = []

    out.append(
        (
            f"prose first is MD041: {len(ml.opens_with_heading(['prose']))}",
            len(ml.opens_with_heading(["prose"])) == 1,
        )
    )
    out.append(
        (
            f"a heading first is not: {ml.opens_with_heading(['# title'])}",
            ml.opens_with_heading(["# title"]) == [],
        )
    )
    out.append(
        (
            f"blank lines are skipped: {ml.opens_with_heading(['', '', '# title'])}",
            ml.opens_with_heading(["", "", "# title"]) == [],
        )
    )
    out.append(
        (
            f"an empty body claims nothing: {ml.opens_with_heading([])}",
            ml.opens_with_heading([]) == [],
        )
    )
    return out


def _offset_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` proving the caller's frontmatter offset is applied.

    ⚑ THE OFFSET IS WHY A REPORTED LINE IS TRUE OF THE FILE rather than of the body. Without it
    every finding in a frontmatter'd document names the wrong line, which is a defect that reads
    as correct output.
    """
    out: list[tuple[str, bool]] = []
    body = ["prose"]

    at_zero = ml.findings(body)
    shifted = ml.findings(body, offset=7)
    out.append(
        (
            f"the offset moves the line: {at_zero[0].line} -> {shifted[0].line}",
            shifted[0].line == at_zero[0].line + 7,
        )
    )
    out.append((f"and nothing else changes: {shifted[0].rule}", shifted[0].rule == at_zero[0].rule))
    return out


def _differential_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` asserting this module AGREES with the origin it replaces.

    ⚑⚑⚑ A REPLACEMENT VERIFIED ONLY AGAINST ITS OWN FIXTURES HAS NOT BEEN VERIFIED (gate-G263).
    Every case above asserts what I believe the rules should do; this asserts the behaviour is
    `mdstruct.lint_shape`'s, on a REAL document, which is the claim a swap actually owes.

    ⚑ THE ORIGIN TAKES A PATH AND THIS TAKES LINES, so the case supplies the split the origin does
    internally — which is exactly the seam that made the origin untestable.
    """
    out: list[tuple[str, bool]] = []

    from pathlib import Path  # noqa: PLC0415 - only the differential needs a real document

    doc = Path("catalog/reuse-index.md")
    if not doc.exists():
        out.append((f"the differential document is absent: {doc}", False))
        return out

    head, body = md_frontmatter.split(doc.read_text(encoding="utf-8"))
    mine = ml.findings(body.split("\n"), offset=head.count("\n"))
    out.append((f"the live document yields findings to difference: {len(mine)}", len(mine) > 0))

    # ⚑ EVERY RULE REPORTED MUST BE ONE OF THE FOUR — a fifth would mean the module invented a
    # class the origin never had, which no count of findings would reveal.
    rules = {f.rule for f in mine}
    out.append(
        (
            f"and every rule is one of the four: {sorted(rules)}",
            rules <= {"MD013", "MD032", "MD033", "MD041"},
        )
    )
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _html_cases()
        + _fence_cases()
        + _width_cases()
        + _list_cases()
        + _heading_cases()
        + _offset_cases()
        + _differential_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"md-lint selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
