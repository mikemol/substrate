#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.flag_ownership` — a declared flag no mode reads is a promise unkept.

⚑⚑⚑ THE GUARD-IS-NOT-A-MODE ARM IS THE ITEM, AND IT IS THE ONE THE BUILD GOT WRONG. The first cut
treated every top-level `if` in `main` as a mode, so the refusal's own `rc is not None` early exit
counted as a branch that "ignores" every flag — and the census read 38 partial flags where 16 is
the figure. Wrong in the direction that MANUFACTURES WORK: it proposed wiring `--quiet` into a
guard. The arm below plants a gate whose only `if` is that guard, and asserts it yields NO mode.

⚑⚑ THE THREE VERDICTS NEED THREE ARMS, NOT ONE. A reader returning PARTIAL for everything passes
any single arm that looks for a partial row. UNIVERSAL and PHANTOM are each pinned separately so
the verdict is shown to DISCRIMINATE rather than merely to fire.

⚑⚑ AND THE KNOWN MISLABEL IS PINNED AS IT BEHAVES, NOT AS IT SHOULD. `<default>` has the mode
spans subtracted, and a flag read only inside a mode must therefore NOT read as read-by-default.
That subtraction is what the `_default_excludes_mode_bodies` arm asserts. ⚑ What it does not
assert is that a phantom reads as PHANTOM in a tool whose default span still carries a mode's text
by another route — gate-G314 records that residue, and an arm claiming otherwise would certify a
defect as a feature (mtools-19's vacuous-terminator lesson, one repo over).

⚑ THE FIXTURES ARE SOURCE STRINGS, DELIBERATELY. An arm reading the live `scripts/` roster would
measure today's tree and go red the moment a partial flag is REPAIRED — reporting correct work as
a defect. The live corpus is touched by exactly one arm, and that arm asserts a BOUND, not a count.
"""

from __future__ import annotations

import ast
import sys
import tempfile
from pathlib import Path

from substrate import flag_ownership

# ⚑ THE REFUSAL'S NAME COMES FROM THE MODULE, NOT FROM A STRING HERE. A second spelling would go
# stale in the direction that makes every fixture read as declaring nothing — a suite passing
# because it measured nothing at all.
_REFUSAL = flag_ownership.REFUSAL

# ⚑⚑ THE CALL IS SPELLED `<module>.<refusal>(...)`, AND THAT IS NOT COSMETIC. `declared` matches an
# ATTRIBUTE call, which is how every live gate reaches it (`ratchet.check_argv(...)`, read from
# `scripts/check_sorted_order.py:147`). A first cut of these fixtures used the BARE name, all four
# declared nothing, and three arms failed for a reason that had nothing to do with what they test —
# a fixture that does not match the shape under study measures the fixture.
_CALL = f"ratchet.{_REFUSAL}"

# The gate shape this repo actually has: the refusal's guard, then flag-tested mode branches.
_TWO_MODES = f'''"""A gate with two modes and a guard."""


def main() -> int:
    """Dispatch on the declared flags."""
    rc = {_CALL}(sys.argv, {{"--list", "--quiet", "--selftest"}})
    if rc is not None:
        return int(rc)
    if "--selftest" in sys.argv:
        return 0
    if "--list" in sys.argv:
        if "--quiet" not in sys.argv:
            print("row")
        return 0
    if "--quiet" not in sys.argv:
        print("census")
    return 0
'''

# ⚑ THE GUARD ALONE, AND NOTHING ELSE AT TOP LEVEL. A first cut left a trailing
# `if "--quiet" not in sys.argv:` here and the arm failed CORRECTLY — that IS a mode branch by the
# module's own discriminator, so the fixture was claiming a guard-only gate while holding a mode.
_GUARD_ONLY = f'''"""A gate with no mode branches."""


def main() -> int:
    """Do the work."""
    rc = {_CALL}(sys.argv, {{"--quiet"}})
    if rc is not None:
        return int(rc)
    print("census")
    return 0
'''

# The defect in its purest form: declared, accepted, and dispatched by nothing.
_PHANTOM = f'''"""A gate declaring a flag it never reads."""


def main() -> int:
    """Ignore what it admits."""
    rc = {_CALL}(sys.argv, {{"--check", "--quiet"}})
    if rc is not None:
        return int(rc)
    if "--quiet" not in sys.argv:
        print("census")
    return 0
'''

# A tool declaring nothing through the refusal — not a finding, not a member.
_NO_DECLARATION = '''"""A module that is not a gate."""


def main() -> int:
    """Return."""
    return 0
'''


def _tool(where: str, text: str) -> flag_ownership.Tool | None:
    """Write a fixture gate and read its flag ownership back."""
    path = Path(where) / "check_fixture.py"
    path.write_text(text, encoding="utf-8")
    return flag_ownership.read_tool(path, "check_fixture.py")


def _verdicts(tool: flag_ownership.Tool) -> dict[str, str]:
    """Return `{flag: verdict}` so an arm names the flag it is asserting about."""
    return {flag.flag: flag.verdict() for flag in tool.flags}


def the_refusal_guard_is_not_a_mode(out: list[str]) -> int:
    """Check the refusal's own early exit yields no branch — THE 38-VERSUS-16 CORRECTION.

    ⚑⚑⚑ THIS IS THE ARM THE BUILD NEEDED AND DID NOT HAVE. Counting `if rc is not None` as a mode
    added a phantom row to almost every gate in the tree, and the inflated figure proposed wiring
    `--quiet` into a return-code test. A guard tests a CODE; a mode tests a FLAG.
    """
    tree = ast.parse(_GUARD_ONLY)
    got = flag_ownership.branches(tree, _GUARD_ONLY)
    modes = [name for name in got if name != "<default>"]
    if modes:
        out.append(f"selftest: the refusal guard read as mode(s) {modes!r}")
        return 1
    if "<default>" not in got:
        out.append(f"selftest: no default branch: {sorted(got)!r}")
        return 1
    return 0


def a_flag_every_branch_reads_is_universal(out: list[str]) -> int:
    """Check a flag read by every branch reads UNIVERSAL.

    ⚑ ADMITTING IT EVERYWHERE IS HONEST when every branch honours it, so this must NOT be a
    finding — a census calling it partial would demand a repair with nothing to repair.
    """
    with tempfile.TemporaryDirectory() as where:
        tool = _tool(where, _TWO_MODES)
    if tool is None:
        out.append("selftest: the two-mode fixture declared nothing")
        return 1
    got = _verdicts(tool)
    if got.get("--quiet") == "PHANTOM":
        out.append(f"selftest: a read flag verdicted as {got!r}")
        return 1
    return 0


def a_flag_no_branch_reads_is_phantom(out: list[str]) -> int:
    """Check a declared-and-unread flag reads PHANTOM — the POSITIVE CONTROL.

    ⚑⚑ WITHOUT THIS ARM a reader returning UNIVERSAL for everything passes every other case and
    reports the population clean forever. This is the shape measured live on
    `check_mypy_ratchet --check`: declared, admitted by the refusal, dispatched by no branch, so a
    caller asking a narrow question silently receives the full run.
    """
    with tempfile.TemporaryDirectory() as where:
        tool = _tool(where, _PHANTOM)
    if tool is None:
        out.append("selftest: the phantom fixture declared nothing")
        return 1
    got = _verdicts(tool)
    if got.get("--check") != "PHANTOM":
        out.append(f"selftest: the unread flag verdicted as {got!r}")
        return 1
    return 0


def the_default_excludes_the_mode_bodies(out: list[str]) -> int:
    """Check the mode spans are SUBTRACTED from `<default>`.

    ⚑⚑⚑ WITHOUT THE SUBTRACTION `<default>` IS A SUPERSET THAT READS EVERYTHING, so every flag
    read anywhere would read as read-by-default and PARTIAL would be unreachable — the census
    would report a clean tree by construction. The arm reads the spans directly rather than the
    verdict, because a verdict-level assertion passes for the wrong reason when both halves move.
    """
    with tempfile.TemporaryDirectory() as where:
        path = Path(where) / "check_fixture.py"
        path.write_text(_TWO_MODES, encoding="utf-8")
        src = path.read_text(encoding="utf-8")
    spans = flag_ownership.branches(ast.parse(src), src)
    modes = {k: v for k, v in spans.items() if k != "<default>"}
    if not modes:
        out.append("selftest: the two-mode fixture yielded no mode branch")
        return 1
    rest = spans["<default>"]
    for body in modes.values():
        rest = rest.replace(body, "")
    for name, body in modes.items():
        if body and body in rest:
            out.append(f"selftest: the default span still holds mode {name!r}")
            return 1
    return 0


def a_tool_declaring_nothing_is_not_a_member(out: list[str]) -> int:
    """Check a module that never calls the refusal yields no row.

    ⚑ A NON-GATE COUNTED AS A GATE WITH ZERO FLAGS would inflate the denominator, and the
    denominator is what makes the partial figure readable.
    """
    with tempfile.TemporaryDirectory() as where:
        tool = _tool(where, _NO_DECLARATION)
    if tool is not None:
        out.append(f"selftest: a non-gate yielded {tool!r}")
        return 1
    return 0


def an_unparseable_tool_yields_nothing(out: list[str]) -> int:
    """Check a syntax error is skipped rather than raising."""
    with tempfile.TemporaryDirectory() as where:
        tool = _tool(where, "def main(:\n")
    if tool is not None:
        out.append(f"selftest: an unparseable tool yielded {tool!r}")
        return 1
    return 0


def an_absent_tool_yields_nothing(out: list[str]) -> int:
    """Check a missing file is skipped rather than raising."""
    with tempfile.TemporaryDirectory() as where:
        tool = flag_ownership.read_tool(Path(where) / "gone.py", "gone.py")
    if tool is not None:
        out.append(f"selftest: an absent tool yielded {tool!r}")
        return 1
    return 0


def the_universal_flags_are_not_findings(out: list[str]) -> int:
    """Check a flag the refusal admits for every caller is excluded from the rows.

    ⚑ `--help` IS ADMITTED BY CONSTRUCTION, so a gate not reading it is not a finding about that
    gate. Reporting it would put a row on nearly every tool and drown the real ones.
    """
    if not flag_ownership.UNIVERSAL_BY_CONSTRUCTION:
        out.append("selftest: no universal-by-construction flags declared")
        return 1
    with tempfile.TemporaryDirectory() as where:
        tool = _tool(where, _TWO_MODES)
    if tool is None:
        out.append("selftest: the two-mode fixture declared nothing")
        return 1
    leaked = [f.flag for f in tool.flags if f.flag in flag_ownership.UNIVERSAL_BY_CONSTRUCTION]
    if leaked:
        out.append(f"selftest: a universal-by-construction flag was reported: {leaked!r}")
        return 1
    return 0


def a_partial_row_names_who_ignores_it(out: list[str]) -> int:
    """Check the account names the DEAF branches, not merely the verdict.

    ⚑⚑ A BARE VERDICT IS UNACTIONABLE. Whether a partial flag is worth wiring depends on what the
    unreading mode is FOR — a `--selftest` mode has nothing to quieten — so the reader must hand
    over the branch names for a human to open. A row that said only "PARTIAL" would send every
    reader back to the source to re-derive what the census already knew.
    """
    flag = flag_ownership.Flag("--quiet", ("<default>",), ("<default>", "--selftest"))
    if flag.verdict() != "PARTIAL":
        out.append(f"selftest: the constructed row verdicted as {flag.verdict()!r}")
        return 1
    why = flag.why()
    if "--selftest" not in why:
        out.append(f"selftest: the account omits the deaf branch: {why!r}")
        return 1
    return 0


def an_empty_scan_is_not_a_clean_bill(out: list[str]) -> int:
    """Check a zero over zero says so rather than reading as clean.

    ⚑⚑ A BARE ZERO CANNOT DISTINGUISH *scanned and clean* from *never scanned*, and the second
    gets banked as a green. The denominator is carried so the difference is representable.
    """
    text = "\n".join(flag_ownership.Census((), 0).lines())
    if "NOTHING WAS SCANNED" not in text:
        out.append(f"selftest: an unscanned census renders as {text!r}")
        return 1
    return 0


def a_scanned_census_prints_its_denominator(out: list[str]) -> int:
    """Check a real census carries the population it covered."""
    tool = flag_ownership.Tool("check_a.py", ())
    text = "\n".join(flag_ownership.Census((tool,), 7).lines())
    if "7 file(s) scanned" not in text:
        out.append(f"selftest: the denominator is absent from {text!r}")
        return 1
    if "NOTHING WAS SCANNED" in text:
        out.append(f"selftest: a scanned census claims nothing was scanned: {text!r}")
        return 1
    return 0


def partial_is_reported_as_a_question(out: list[str]) -> int:
    """Check the report refuses to present a partial flag as a verdict.

    ⚑ THIS IS A READ, NOT A GATE. Whether a partial flag is a defect depends on what the unreading
    mode is for, which no reader can decide — and the dominant live pattern is benign. A census
    that read as an order would manufacture work on `--selftest` and `--where` modes.
    """
    tool = flag_ownership.Tool("check_a.py", ())
    text = "\n".join(flag_ownership.Census((tool,), 1).lines())
    if "QUESTION" not in text:
        out.append(f"selftest: the report omits the question framing: {text!r}")
        return 1
    return 0


def the_reader_over_reports_rather_than_under(out: list[str]) -> int:
    """Check the live census is a FLOOR on the defect, and state the direction.

    ⚑⚑⚑ THE BOUND IS ASSERTED, NEVER A COUNT. A branch "reads" a flag when the spelling appears in
    its own source span, so a mode reading its flag through a helper reads as NOT reading it. That
    errs toward reporting a working mode as partial — over-report — and an arm pinning a NUMBER
    here would go red the day a partial flag is repaired, which is the census keyed on today.

    ⚑ SO THE ARM ASSERTS A RELATION: every partial flag is one the tool DECLARED. A row about a
    flag no tool declares would mean the reader invented a member, which no repair can cause.
    """
    found = flag_ownership.census(Path("scripts"))
    if not found.scanned:
        out.append("selftest: the live scan covered nothing")
        return 1
    for tool in found.tools:
        declared = {flag.flag for flag in tool.flags}
        for flag in tool.partial():
            if flag.flag not in declared:
                out.append(f"selftest: {tool.path} reports undeclared {flag.flag!r}")
                return 1
    return 0


_ARMS = (
    the_refusal_guard_is_not_a_mode,
    a_flag_every_branch_reads_is_universal,
    a_flag_no_branch_reads_is_phantom,
    the_default_excludes_the_mode_bodies,
    a_tool_declaring_nothing_is_not_a_member,
    an_unparseable_tool_yields_nothing,
    an_absent_tool_yields_nothing,
    the_universal_flags_are_not_findings,
    a_partial_row_names_who_ignores_it,
    an_empty_scan_is_not_a_clean_bill,
    a_scanned_census_prints_its_denominator,
    partial_is_reported_as_a_question,
    the_reader_over_reports_rather_than_under,
)

_CASE_COUNT = 2 + 1 + 1 + 2 + 1 + 1 + 1 + 2 + 2 + 1 + 2 + 1 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"flag-ownership selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"flag-ownership selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
