#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.tool_find_render` — where a renderer can report a method as a fact.

⚑⚑⚑ THREE ARMS HERE PIN DEFECTS THE MODULE RECORDS AS HAVING BEEN MEASURED, which is why a pure
renderer earns a suite at all: each failure produces a REPORT THAT READS FINE and says something
false about the substrate.

  · UNSEARCHED IS NOT EMPTY. A caller that did not pay for the docstring walk must read
    `(not searched)`, never `(none)` — the difference between "no tool does this" and "nothing
    looked". The second is a claim the search cannot support, and it is the one this repo keeps
    filing.
  · THE TRUNCATION NOTICE MUST NAME ITS OWN REMEDY. `--find _sql` once reported 54 hits and
    printed 20 with `… and 32 more` — a count that was exact beside a list that was not, honest
    and unactionable in the same breath. It sent one caller to a flag that did not exist and then
    to reading the file by hand.
  · A CITATION IS NOT DEBT. Folding cited mentions into the `NAMED but not declared` block made a
    correct cross-reference read as debt, and the paydown that follows DELETES the
    cross-discoverability the standing rule requires.

⚑⚑ THE FIXTURES ARE HAND-BUILT `Found` VALUES, NOT A LIVE SEARCH. The module's own docstring
states the reason it was split out — *"rendering is separate from finding so every arm is testable
without capturing stdout"* — and a live search would make every case a hostage to whatever the
tool corpus happens to hold this hour, which is the expiry shape this batch keeps recording.

⚑⚑ AND `witnessed` IS SET THROUGH `tool_decline.WITNESSED` / `INFERRED`, NOT BY A KEYWORD. It is a
DERIVED property over a `kind` field — a first draft passed it as a constructor argument and mypy
refused, which is the fixture being corrected by the type it was guessing at. Naming the constants
also means a renamed kind fails here rather than silently rendering the wrong half.

⚑ THE PAGE BOUND IS READ FROM `tool_find.FUNCTION_PAGE`, never typed. One `Page` drives both the
slice and the notice precisely so they cannot disagree; a literal here would reintroduce the
second number whose divergence was the original defect.
"""

from __future__ import annotations

import sys

from substrate import tool_decline, tool_find, tool_find_render

# A scope where the function corpus WAS walked, and one where it was not.
_SEARCHED = tool_find_render.Scope(tools=3, modes=9, functions=40, searched=True)
_UNSEARCHED = tool_find_render.Scope(tools=3, modes=9, functions=0, searched=False)

# The width the elision cases bound a gloss to.
_WIDTH = 10

# Where the fixtures claim to live — names no real tool carries.
_TOOL = "scratch/one.py"
_OTHER = "scratch/two.py"
_DECLARER = "scratch/other.py"
_FUNCTION_HOME = "substrate/one.py"


def _mode(name: str = "--thing") -> tool_find.ModeHit:
    """Return one declared-mode hit."""
    return tool_find.ModeHit(
        mode=name, relpath=_TOOL, gloss="does the thing", sources=frozenset({"usage"})
    )


def _function(name: str) -> tool_find.FunctionHit:
    """Return one library-function hit."""
    return tool_find.FunctionHit(
        relpath=_FUNCTION_HOME, name=name, gloss="does the thing", why="name"
    )


def _mention(kind: str) -> tool_find.MentionHit:
    """Return one CITED mention of the given citation kind."""
    return tool_find.MentionHit(
        relpath=_TOOL,
        flag="--thing",
        citation=tool_decline.Citation(kind=kind, owners=(_DECLARER,)),
    )


def _found(
    *,
    by_mode: tuple[tool_find.ModeHit, ...] = (),
    lacking: tuple[str, ...] = (),
    cited: tuple[tool_find.MentionHit, ...] = (),
    dispatched: tuple[tuple[str, str], ...] = (),
    functions: tuple[tool_find.FunctionHit, ...] = (),
) -> tool_find.Found:
    """Return an empty search, with the named arms replaced.

    ⚑ EVERY ARM DEFAULTS TO EMPTY so a case supplies only the one it is about — which keeps each
    assertion about a single section rather than about a whole rendered page.
    """
    return tool_find.Found(
        needle="--thing",
        by_mode=by_mode,
        lacking=lacking,
        by_gloss=(),
        cited=cited,
        prose=(),
        dispatched=dispatched,
        functions=functions,
        tools=(),
    )


def the_unsearched_function_corpus_says_so(out: list[str]) -> int:
    """Check an unwalked corpus reads `not searched`, NEVER `(none)` — THE ARM.

    ⚑⚑⚑ A CALLER THAT DID NOT PAY FOR THE DOCSTRING WALK must not be told the capability is
    absent. `(none)` is a claim about the substrate; `(not searched)` is the truth about the
    method, and collapsing them is how a toolkit gap becomes "no tool covers this".
    """
    text = tool_find_render.render(_found(), _UNSEARCHED)
    section = text.partition("by FUNCTION")[2].partition("by TOOL")[0]
    if "not searched" not in section:
        out.append(f"selftest: an unsearched corpus does not say so: {section!r}")
        return 1
    if "(none)" in section:
        out.append(f"selftest: an unsearched corpus rendered as empty: {section!r}")
        return 1
    return 0


def a_searched_but_empty_function_corpus_reads_none(out: list[str]) -> int:
    """Check the OTHER half — a walked corpus with no hits says `(none)`.

    ⚑⚑ WITHOUT THIS, A RENDERER PRINTING `not searched` UNCONDITIONALLY passes the arm above.
    The two together are what make the distinction observable rather than asserted.
    """
    text = tool_find_render.render(_found(), _SEARCHED)
    section = text.partition("by FUNCTION")[2].partition("by TOOL")[0]
    if "(none)" not in section:
        out.append(f"selftest: a searched-and-empty corpus does not read none: {section!r}")
        return 1
    if "not searched" in section:
        out.append(f"selftest: a searched corpus claimed to be unsearched: {section!r}")
        return 1
    return 0


def the_function_arm_pages_and_names_its_remedy(out: list[str]) -> int:
    """Check a truncated listing says HOW to see the rest — THE MEASURED DEFECT.

    ⚑⚑⚑ `--find _sql` REPORTED 54 HITS AND PRINTED 20 with `… and 32 more`. The notice was
    honest and unactionable at once: it named what was missing without offering any way to see
    it, and sent a caller to a flag that did not exist. A census that can name its own omission
    but not remove it still reports the method as the substrate.
    """
    bound = tool_find.FUNCTION_PAGE
    found = _found(functions=tuple(_function(f"fn{n:03d}") for n in range(bound * 2)))
    text = tool_find_render.render(found, _SEARCHED)
    shown = [ln for ln in text.splitlines() if f" in {_FUNCTION_HOME}" in ln]
    if len(shown) != bound:
        out.append(
            f"selftest: {bound * 2} functions rendered {len(shown)} row(s), "
            f"expected the page of {bound}"
        )
        return 1
    notice = next((ln for ln in text.splitlines() if "more" in ln), "")
    if "--top 0" not in notice:
        out.append(f"selftest: the truncation notice names no remedy: {notice!r}")
        return 1
    if found.needle not in notice:
        out.append(f"selftest: the remedy does not carry the needle: {notice!r}")
        return 1
    return 0


def the_truncation_count_matches_what_was_withheld(out: list[str]) -> int:
    """Check the `N more` figure agrees with the rows actually shown.

    ⚑⚑ ONE `Page` DRIVES BOTH THE SLICE AND THE NOTICE precisely so they cannot disagree. Two
    independent literals is exactly how a truncation notice comes to contradict the list above
    it — which is the shape of the original defect, an exact count beside an inexact list.
    """
    total = tool_find.FUNCTION_PAGE + 7
    found = _found(functions=tuple(_function(f"fn{n:03d}") for n in range(total)))
    text = tool_find_render.render(found, _SEARCHED)
    shown = len([ln for ln in text.splitlines() if f" in {_FUNCTION_HOME}" in ln])
    notice = next((ln for ln in text.splitlines() if "more" in ln), "")
    if f"{total - shown} more" not in notice:
        out.append(f"selftest: {shown} shown of {total} but the notice reads {notice!r}")
        return 1
    return 0


def an_unbounded_listing_carries_no_truncation_notice(out: list[str]) -> int:
    """Check `--top 0` shows everything and drops the notice — the remedy actually works.

    ⚑ A REMEDY THE NOTICE NAMES MUST DO WHAT IT SAYS. Otherwise the fix for an unactionable
    notice is a second unactionable notice.
    """
    total = tool_find.FUNCTION_PAGE * 2
    found = _found(functions=tuple(_function(f"fn{n:03d}") for n in range(total)))
    text = tool_find_render.render(found, _SEARCHED, top=0)
    shown = len([ln for ln in text.splitlines() if f" in {_FUNCTION_HOME}" in ln])
    if shown != total:
        out.append(f"selftest: --top 0 showed {shown} of {total}")
        return 1
    if any("more —" in ln for ln in text.splitlines()):
        out.append("selftest: an unbounded listing still carries a truncation notice")
        return 1
    return 0


def a_citation_is_not_rendered_as_debt(out: list[str]) -> int:
    """Check cited mentions get their OWN section, marked not-a-gap — THE RECORDED DEFECT.

    ⚑⚑⚑ FOLDING CITATIONS INTO THE `NAMED but not declared` BLOCK made a correct cross-reference
    read as debt, and the paydown that follows DELETES the cross-discoverability the standing
    rule requires. The section heading saying `not a gap` is the whole repair.
    """
    found = _found(cited=(_mention(tool_decline.WITNESSED),))
    text = tool_find_render.render(found, _SEARCHED)
    if "CITED" not in text:
        out.append("selftest: a citation got no section of its own")
        return 1
    block = text.partition("CITED")[2].partition("NAMED but not declared")[0]
    if "not a gap" not in block:
        out.append(f"selftest: the citation section does not disclaim debt: {block!r}")
        return 1
    if _DECLARER not in block:
        out.append(f"selftest: the citation does not name its declarer: {block!r}")
        return 1
    return 0


def an_unwitnessed_citation_is_flagged(out: list[str]) -> int:
    """Check a citation whose owner is not named on the line says so.

    ⚑ WITNESSED AND INFERRED CITATIONS ARE DIFFERENT FACTS. Rendering both identically would
    make an inferred cross-reference read as a confirmed one.
    """
    blocks = []
    for kind in (tool_decline.WITNESSED, tool_decline.INFERRED):
        whole = tool_find_render.render(_found(cited=(_mention(kind),)), _SEARCHED).partition(
            "CITED"
        )[2]
        blocks.append(whole.partition("NAMED but not declared")[0])
    if blocks[0] == blocks[1]:
        out.append("selftest: a witnessed and an inferred citation render identically")
        return 1
    if "owner not named" not in blocks[1]:
        out.append(f"selftest: an inferred citation is not flagged: {blocks[1]!r}")
        return 1
    return 0


def no_citations_means_no_cited_section(out: list[str]) -> int:
    """Check the section is omitted when empty, rather than printed as a hollow heading."""
    if "CITED" in tool_find_render.render(_found(), _SEARCHED):
        out.append("selftest: an empty citation arm still printed its section")
        return 1
    return 0


def the_mode_arm_names_the_tools_that_lack_it(out: list[str]) -> int:
    """Check the ACTIONABLE half is rendered — the mode is not on the tool you just typed.

    ⚑⚑ `--grep EXISTS` WAS NEVER THE QUESTION; *it is not on the tool I just typed* was, in five
    recorded misses. A hit list without the lacking set answers the question nobody asked.
    """
    text = tool_find_render.render(_found(by_mode=(_mode(),), lacking=(_OTHER,)), _SEARCHED)
    if f"NOT on: {_OTHER}" not in text:
        out.append("selftest: the lacking tools are not named")
        return 1
    return 0


def a_universal_mode_says_every_tool_has_it(out: list[str]) -> int:
    """Check an empty `lacking` beside real hits reads as universality, not as silence.

    ⚑ THE THREE STATES ARE DISTINCT: no hits, hits with gaps, hits everywhere. Printing nothing
    for the third would leave a reader unable to tell it from a renderer that dropped the line.
    """
    text = tool_find_render.render(_found(by_mode=(_mode(),)), _SEARCHED)
    if "every tool has it" not in text:
        out.append("selftest: a universally-declared mode renders no verdict")
        return 1
    return 0


def an_empty_mode_arm_reads_none_not_universal(out: list[str]) -> int:
    """Check no hits reads `(none)` rather than claiming every tool has the mode.

    ⚑⚑ THIS IS THE DISCRIMINATOR FOR THE ARM ABOVE. With no hits, `lacking` is also empty — so a
    renderer keying only on `lacking` would announce that every tool has a mode nothing declares.
    """
    section = tool_find_render.render(_found(), _SEARCHED).partition("by GLOSS")[0]
    if "(none)" not in section:
        out.append(f"selftest: an empty mode arm does not read none: {section!r}")
        return 1
    if "every tool has it" in section:
        out.append("selftest: a mode nothing declares was reported as universal")
        return 1
    return 0


def an_undocumented_dispatch_is_reported_as_such(out: list[str]) -> int:
    """Check a flag accepted but never declared is named — the third verdict."""
    text = tool_find_render.render(_found(dispatched=((_TOOL, "--thing"),)), _SEARCHED)
    if "UNDOCUMENTED" not in text:
        out.append("selftest: an undocumented dispatch is not marked")
        return 1
    if _TOOL not in text.partition("NAMED but not declared")[2]:
        out.append("selftest: the dispatching tool is not named")
        return 1
    return 0


def a_long_gloss_is_elided_on_one_line(out: list[str]) -> int:
    """Check `one_line` collapses and bounds — a multi-line gloss must not break the columns."""
    got = tool_find_render.one_line("a\n  b   c", 40)
    if got != "a b c":
        out.append(f"selftest: a wrapped gloss collapsed to {got!r}")
        return 1
    long = tool_find_render.one_line("x" * 100, _WIDTH)
    if len(long) != _WIDTH:
        out.append(f"selftest: an elided gloss is {len(long)} chars, not the width")
        return 1
    if not long.endswith("…"):
        out.append(f"selftest: an elided gloss is not marked: {long!r}")
        return 1
    return 0


def a_short_gloss_is_left_alone(out: list[str]) -> int:
    """Check elision is conditional — the other half, so a truncator is not a constant."""
    if tool_find_render.one_line("short", 40) != "short":
        out.append("selftest: a gloss inside the width was altered")
        return 1
    return 0


def the_footer_reports_the_denominators(out: list[str]) -> int:
    """Check the hit count arrives with the population it was measured over.

    ⚑⚑ A HIT COUNT WITH NO POPULATION IS A NUMBER A READER CANNOT WEIGH, and reporting `0 hits`
    without saying over what is the absence-as-fact shape this census exists to refuse.
    """
    found = _found(by_mode=(_mode(),))
    footer = tool_find_render.render(found, _SEARCHED).strip().splitlines()[-1]
    for figure in (
        f"{found.hits} hit(s)",
        f"{_SEARCHED.modes} declared mode",
        f"{_SEARCHED.functions} documented function",
        f"{_SEARCHED.tools} tool",
    ):
        if figure not in footer:
            out.append(f"selftest: the footer omits {figure!r}: {footer!r}")
            return 1
    return 0


def every_arm_has_a_section_in_the_render(out: list[str]) -> int:
    """Check all five headings appear, so no arm can be silently dropped.

    ⚑ AN ARM THAT RENDERS NOTHING reads exactly like an arm that found nothing. The headings
    are what let a reader see that each question was asked.
    """
    text = tool_find_render.render(_found(), _SEARCHED)
    for heading in ("by MODE NAME", "by GLOSS", "NAMED but not declared", "by FUNCTION", "by TOOL"):
        if heading not in text:
            out.append(f"selftest: the render omits the {heading!r} section")
            return 1
    return 0


def the_render_ends_with_a_newline(out: list[str]) -> int:
    """Check the text is terminated, so a caller writing it directly does not run lines on."""
    if not tool_find_render.render(_found(), _SEARCHED).endswith("\n"):
        out.append("selftest: the render does not end with a newline")
        return 1
    return 0


_ARMS = (
    the_unsearched_function_corpus_says_so,
    a_searched_but_empty_function_corpus_reads_none,
    the_function_arm_pages_and_names_its_remedy,
    the_truncation_count_matches_what_was_withheld,
    an_unbounded_listing_carries_no_truncation_notice,
    a_citation_is_not_rendered_as_debt,
    an_unwitnessed_citation_is_flagged,
    no_citations_means_no_cited_section,
    the_mode_arm_names_the_tools_that_lack_it,
    a_universal_mode_says_every_tool_has_it,
    an_empty_mode_arm_reads_none_not_universal,
    an_undocumented_dispatch_is_reported_as_such,
    a_long_gloss_is_elided_on_one_line,
    a_short_gloss_is_left_alone,
    the_footer_reports_the_denominators,
    every_arm_has_a_section_in_the_render,
    the_render_ends_with_a_newline,
)

_CASE_COUNT = 2 + 2 + 3 + 1 + 2 + 3 + 2 + 1 + 1 + 1 + 2 + 2 + 3 + 1 + 4 + 5 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"tool-find-render selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"tool-find-render selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
