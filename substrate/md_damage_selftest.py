# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.md_damage` — four preservation checks, each in both directions.

⚑⚑⚑ EVERY CHECK NEEDS TWO ARMS AND THE SECOND IS THE HARD ONE. The damage arm proves the check
fires; the PRE-EXISTING arm proves it does not fire on notation the document always wrote. A check
that flagged an escape already present would report the corpus's own conventions as damage on every
run — the cries-wolf shape that teaches a reader to skim, which is exactly how the original damage
went unnoticed under two green gates.

⚑⚑ AND THE FIXTURES ARE THE MEASURED INCIDENT. A memory file converged to output that escaped
inline code, escaped its wikilinks, smart-quoted its prose and dropped its frontmatter — reported
as a clean fixpoint. Each fixture below is one of those four, so the suite pins the run that
motivated the module rather than a shape someone imagined.

⚑ THE COMPOSITE ARM IS SEPARATE BECAUSE THE CHECKS MUST NOT SHORT-CIRCUIT. That one write broke
four properties at once, and a reader given only the first has three unrepaired defects and no way
to know.
"""

from __future__ import annotations

import sys

from substrate import md_damage as md

#: A memory's frontmatter — its name, type and provenance.
FRONTMATTER = "---\nname: a-memory\ntype: project\n---\n"

#: ⚑ THE MEASURED CODE-ESCAPE, verbatim in shape: a PSI selector made wrong as written.
CODE_BEFORE = "read `cpu|memory|io` from the meter"
CODE_AFTER = "read `cpu\\|memory\\|io` from the meter"

#: ⚑ THE MEASURED WIKILINK ESCAPE — mesh edges turned into text.
LINK_BEFORE = "see [[first-memory]] and [[second-memory]]"
LINK_AFTER = "see \\[[first-memory]] and \\[[second-memory]]"

#: The typographic pair a prose writer substitutes, named so the fixture stays inside the width.
_OPEN = "\N{LEFT SINGLE QUOTATION MARK}"
_CLOSE = "\N{RIGHT SINGLE QUOTATION MARK}"

#: ⚑ THE MEASURED QUOTE SUBSTITUTION.
QUOTE_BEFORE = "the operator said 'do not do this'"
QUOTE_AFTER = f"the operator said {_OPEN}do not do this{_CLOSE}"


def _frontmatter_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the identity-dropping check."""
    out: list[tuple[str, bool]] = []

    dropped = md.frontmatter_dropped(FRONTMATTER + "body", "body")
    out.append(
        (
            f"dropped frontmatter is damage: {md.kinds(dropped)}",
            md.kinds(dropped) == ("frontmatter-dropped",),
        )
    )
    out.append(
        (f"and the detail names what was lost: {dropped[0].detail}", "name" in dropped[0].detail)
    )

    # ⚑ THE FALSE-POSITIVE ARM. A body-only document loses nothing by staying body-only.
    kept = md.frontmatter_dropped("body", "body")
    out.append((f"a document that never had it is not damaged: {kept}", kept == []))

    survived = md.frontmatter_dropped(FRONTMATTER + "body", FRONTMATTER + "reflowed body")
    out.append((f"and surviving frontmatter is not damage: {survived}", survived == []))

    # ⚑⚑ AN UNTERMINATED FENCE IS NOT FRONTMATTER, and this is why the question is
    # `md_frontmatter`'s: the origin's local predicate would call this a drop.
    unterminated = md.frontmatter_dropped("---\nnot closed\nbody", "body")
    out.append((f"an unterminated fence is not frontmatter: {unterminated}", unterminated == []))
    return out


def _code_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for escapes introduced inside inline code."""
    out: list[tuple[str, bool]] = []

    hurt = md.escaped_code(CODE_BEFORE, CODE_AFTER)
    out.append(
        (
            f"an escape added inside code is damage: {md.kinds(hurt)}",
            md.kinds(hurt) == ("escape-in-code",),
        )
    )
    out.append((f"and the detail carries the span: {hurt[0].detail}", "cpu" in hurt[0].detail))

    # ⚑⚑ THE FALSE-POSITIVE ARM, AND IT IS THE SUBTLE ONE. A document that ALWAYS wrote the
    # backslash is unchanged by a transform that preserves it.
    already = md.escaped_code(CODE_AFTER, CODE_AFTER)
    out.append((f"an escape already present is not damage: {already}", already == []))

    # ⚑ AND AN UNRELATED CODE SPAN APPEARING IS NOT AN ESCAPE. Unescaping it recovers nothing the
    # input held, which is the test that separates the two.
    added = md.escaped_code("`plain`", "`plain` and `other\\|thing`")
    out.append((f"an unrelated new span is not an escape: {added}", added == []))
    return out


def _wikilink_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for mesh edges turned into text."""
    out: list[tuple[str, bool]] = []

    hurt = md.escaped_wikilinks(LINK_BEFORE, LINK_AFTER)
    out.append(
        (f"escaped links are damage: {md.kinds(hurt)}", md.kinds(hurt) == ("wikilink-escaped",))
    )
    out.append((f"and the detail counts both: {hurt[0].detail}", "2 of 2" in hurt[0].detail))

    survived = md.escaped_wikilinks(LINK_BEFORE, LINK_BEFORE)
    out.append((f"surviving links are not damage: {survived}", survived == []))
    out.append(
        (
            f"a document with no links is not damaged: {md.escaped_wikilinks('a', 'b')}",
            md.escaped_wikilinks("a", "b") == [],
        )
    )

    # ⚑ GAINING A LINK IS NOT DAMAGE — only a DROP is, which is what makes this a delta check.
    gained = md.escaped_wikilinks(LINK_BEFORE, LINK_BEFORE + " and [[third]]")
    out.append((f"gaining a link is not damage: {gained}", gained == []))
    return out


def _quote_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for typographic substitution."""
    out: list[tuple[str, bool]] = []

    hurt = md.smart_quotes(QUOTE_BEFORE, QUOTE_AFTER)
    out.append(
        (
            f"straight quotes becoming typographic is damage: {md.kinds(hurt)}",
            md.kinds(hurt) == ("smart-quotes",),
        )
    )

    # ⚑⚑ THE FALSE-POSITIVE ARM. A corpus that already writes typographic quotes made that choice
    # deliberately, and flagging it would make the check fire forever.
    already = md.smart_quotes(QUOTE_AFTER, QUOTE_AFTER)
    out.append((f"a document already using them is not damaged: {already}", already == []))

    none = md.smart_quotes("no quotes here", "no quotes here")
    out.append((f"a document with no quotes is not damaged: {none}", none == []))
    return out


def _composite_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` proving all four checks run rather than short-circuiting.

    ⚑⚑⚑ THE MEASURED WRITE BROKE FOUR PROPERTIES AT ONCE. A reader handed only the first would
    repair one and ship three, and each has a different remedy — so this asserts the whole set.
    """
    out: list[tuple[str, bool]] = []
    before = FRONTMATTER + CODE_BEFORE + "\n" + LINK_BEFORE + "\n" + QUOTE_BEFORE
    after = CODE_AFTER + "\n" + LINK_AFTER + "\n" + QUOTE_AFTER

    rows = md.damage(before, after)
    out.append(
        (
            f"all four are reported: {md.kinds(rows)}",
            set(md.kinds(rows))
            == {"frontmatter-dropped", "escape-in-code", "wikilink-escaped", "smart-quotes"},
        )
    )

    # ⚑ AN UNDAMAGED TRANSFORM REPORTS NOTHING — the arm that would fail if any check fired on
    # the corpus's own notation.
    clean = md.damage(before, before)
    out.append((f"an identity transform is clean: {clean}", clean == []))

    reflowed = md.damage(before, before.replace("\n", "\n\n"))
    out.append((f"and a pure reflow is clean: {md.kinds(reflowed)}", reflowed == []))
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _frontmatter_cases()
        + _code_cases()
        + _wikilink_cases()
        + _quote_cases()
        + _composite_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"md-damage selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
