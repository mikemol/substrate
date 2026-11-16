#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.module_replace` — the additive transform, and what it refuses.

⚑⚑⚑ THIS MODULE WRITES TO THE TREE, WHICH IS WHY ITS REFUSALS ARE THE ITEM. A replacement that
silently wrote a file in which nothing was replaced would report CLEAN, and a caller reads CLEAN as
*the change landed* — the plausible-and-wrong output the whole stage-check-write pipeline exists to
refuse. So the arms pin the REFUSALS first and the happy path second.

⚑⚑ THE OUTSIDE-SPAN GUARD IS WHAT SURVIVED OF THE CONSERVATION GUARD, AND BOTH DIRECTIONS ARE
LOAD-BEARING. `module_trim` can assert every original line lands in one of two partitions; a
replacement cannot, because introducing and dropping lines INSIDE the named span is the operation.
What stays checkable is everything else — a transform that dropped a neighbouring def (absent) or
rewrote one in place (gained). An arm for only one direction certifies half a guard.

⚑ AND AN IMPORT MOVES EITHER WAY WITHOUT ACCUSATION. `ruff --fix` legitimately re-sorts and
re-narrows the block, so treating its output as invented content makes the pipeline accuse itself
(gate-G333) — cased here so the exemption cannot be quietly dropped.

⚑⚑ `module_trim` IS IMPORTED DIRECTLY, NEVER REACHED THROUGH `module_replace`. A module attribute
borrowed from another module is the same object at runtime and an unexported name to the checker —
the re-export defect (gate-G325), refused here before it could be written.

⚑ THE CASES ARE SOURCE STRINGS, NOT TREE WRITES. `consider` needs a real path under `corpus.ROOT`
and shells out to the house checker; driving it per case would make this suite slow and would
assert facts about the TREE rather than about this transform. One arm touches the live corpus, and
it asserts a RELATION rather than a verdict.
"""

from __future__ import annotations

import sys

import libcst as cst

from substrate import corpus, module_replace, module_trim, record_migrate

# A module with two top-level defs, so a transform that takes the wrong one is visible.
_MODULE = '''"""A fixture module."""


def keep() -> int:
    """Stay put."""
    return 1


def swap() -> int:
    """Be replaced."""
    return 2
'''

# ⚑ THE SAME NAME AS A METHOD, WHICH IS A DIFFERENT DEFINITION. The partition must not take it.
_NESTED = '''"""A fixture whose CLASS has a method sharing the replaced name."""


class Holder:
    """Hold a method named like the target."""

    def swap(self) -> int:
        """Not the top-level definition."""
        return 9


def swap() -> int:
    """The real target."""
    return 2
'''

# The replacement text every arm swaps in, so a difference in output is the transform's.
_NEW = 'def swap() -> int:\n    """New."""\n    return 3\n'

# ⚑ AN IMPORT BLOCK RUFF WOULD LEGITIMATELY NARROW — the exemption's subject, built as two
# fixtures rather than inline so neither line runs past the bar.
_IMPORTS_BEFORE = "import sys\nfrom os import path, sep\n\n\n" + _NEW
_IMPORTS_AFTER = "from os import path\n\n\n" + _NEW


def _replaced(source: str, name: str, new_text: str) -> str:
    """Return `source` with `name`'s top-level definition swapped for `new_text`.

    ⚑ THE PARTITION IS THE SHIPPED ONE, never a copy of it. A suite that reimplements the rule it
    tests passes while the shipped rule rots.
    """
    module = cst.parse_module(source)
    body: list[cst.BaseStatement] = []
    for statement in module.body:
        if module_trim._defined_name(statement) == name:  # noqa: SLF001 — the shared partition
            body.extend(cst.parse_module(new_text).body)
        else:
            body.append(statement)
    return module.with_changes(body=body).code


def _span_of(source: str, name: str) -> str:
    """Return the source text of one top-level definition, for the identity arm."""
    module = cst.parse_module(source)
    for statement in module.body:
        if module_trim._defined_name(statement) == name:  # noqa: SLF001 — the shared partition
            return module.code_for_node(statement)
    return ""


def _without(source: str, name: str) -> str:
    """Return `source` with the named top-level definition removed — structurally.

    ⚑⚑⚑ A FIXTURE THAT DAMAGES ITS INPUT BY STRING MATCH TESTS THE MATCH, NOT THE GUARD. The first
    cut of the dropped-neighbour arm spliced the def out with `str.replace` on an exact three-line
    string including its trailing blank run — and libcst's round-trip does not guarantee that
    spelling, so the replace found nothing, the text was UNCHANGED, and the guard correctly
    reported nothing. The arm read as *the guard missed a deletion* when the deletion never
    happened. Removing the statement through the same partition the guard uses makes the damage a
    fact rather than a hope, and the arm now asserts the fixture bit before asserting the verdict.
    """
    module = cst.parse_module(source)
    kept = [s for s in module.body if module_trim._defined_name(s) != name]  # noqa: SLF001 — the shared partition
    return module.with_changes(body=kept).code


def _fail(out: list[str], why: str) -> int:
    """Record one failure and return its contribution to the exit code."""
    out.append(f"selftest: {why}")
    return 1


def an_untouched_neighbour_passes(out: list[str]) -> int:
    """Check a clean replacement reports no outside-span reason."""
    got = _replaced(_MODULE, "swap", _NEW)
    reasons = module_replace.outside_span(_MODULE, got, "swap")
    if reasons:
        return _fail(out, f"a clean replacement was accused: {reasons!r}")
    return 0


def a_dropped_neighbour_is_caught(out: list[str]) -> int:
    """Check a line vanishing OUTSIDE the span is reported — the deletion direction.

    ⚑⚑ THIS IS WHAT THE GUARD IS FOR. A mechanical transform's characteristic failure is taking
    the definition BELOW the one named, and the replaced span itself cannot witness that because
    changing it is the operation.
    """
    got = _replaced(_MODULE, "swap", _NEW)
    lost = _without(got, "keep")
    if lost == got:
        return _fail(out, "the fixture did not drop the neighbouring def")
    if not module_replace.outside_span(_MODULE, lost, "swap"):
        return _fail(out, "a dropped neighbouring def was not reported")
    return 0


def a_rewritten_neighbour_is_caught(out: list[str]) -> int:
    """Check a line APPEARING outside the span is reported — the rewrite direction.

    ⚑⚑ THE MIRROR ARM, AND WITHOUT IT HALF THE GUARD IS UNPINNED — but only a PURE ADDITION pins
    it. A first cut rewrote `return 1` to `return 99`, which is a loss AND a gain, so the LOST
    loop caught it and the arm passed with the gained direction inverted: a passing arm certifying
    a direction it never exercised. Verified by planting that inversion and watching this stay
    green. Inserting a statement removes nothing, so only the gained loop can see it.
    """
    got = _replaced(_MODULE, "swap", _NEW)
    added = got.replace('    """Stay put."""\n', '    """Stay put."""\n    _ = 7\n')
    if added == got:
        return _fail(out, "the fixture did not add a line outside the span")
    if not module_replace.outside_span(_MODULE, added, "swap"):
        return _fail(out, "an added neighbouring line was not reported")
    return 0


def an_import_may_move_either_way(out: list[str]) -> int:
    """Check an import is exempt in BOTH directions — `ruff --fix` re-sorts and re-narrows.

    ⚑ TREATING THE FIXER'S OUTPUT AS INVENTED CONTENT MAKES THE PIPELINE ACCUSE ITSELF. The
    one-directional form refused a correct trim when ruff narrowed a shared import line, which
    both vanishes and appears as one edit (gate-G333).
    """
    if module_replace.outside_span(_IMPORTS_BEFORE, _IMPORTS_AFTER, "swap"):
        return _fail(out, "an import that moved was reported as content")
    return 0


def a_method_sharing_the_name_is_not_the_target(out: list[str]) -> int:
    """Check the partition reads TOP-LEVEL definitions only.

    ⚑⚑ A VISITOR MATCHING ON THE NAME ALONE WOULD TAKE THE METHOD, which is the silent-deletion
    shape: the output parses, reads plausibly, and removed the wrong thing.
    """
    got = _replaced(_NESTED, "swap", _NEW)
    if "Not the top-level definition" not in got:
        return _fail(out, "the class method was taken instead of the top-level def")
    if "return 3" not in got:
        return _fail(out, "the top-level def was not replaced")
    return 0


def an_absent_name_is_a_refusal(out: list[str]) -> int:
    """Check a name that is not there REFUSES rather than writing an unchanged file.

    ⚑⚑⚑ SILENTLY WRITING A FILE IN WHICH NOTHING WAS REPLACED IS THE WORST OUTPUT AVAILABLE. The
    caller reads CLEAN as *the change landed* and moves on; the refusal is what makes a green
    verdict mean something.

    ⚑ THE FIXTURE LIVES UNDER `corpus.ROOT` because `consider` takes a path relative to it — one
    in a temp directory would raise, making this an arm about `Path.relative_to` instead.
    """
    path = corpus.ROOT / "substrate" / "_module_replace_fixture.py"
    path.write_text(_MODULE, encoding="utf-8")
    try:
        found = module_replace.consider(path, "nosuchname", _NEW)
    finally:
        path.unlink(missing_ok=True)
    if found.verdict != module_replace.UNSAFE:
        return _fail(out, f"an absent name verdicted as {found.verdict!r}")
    if module_replace.NOT_FOUND not in found.report:
        return _fail(out, f"the refusal does not name the cause: {found.report!r}")
    if found.writable:
        return _fail(out, "an absent-name refusal read as writable")
    return 0


def only_clean_is_writable(out: list[str]) -> int:
    """Check UNSAFE and UNKNOWN are refused on the same footing as FINDINGS.

    ⚑ A GUARD THAT REFUSED AND A CHECKER THAT COULD NOT RUN HAVE BOTH ESTABLISHED NOTHING, so
    neither may write. Constructed rather than provoked — the verdict lattice is the claim.
    """
    for verdict in (module_replace.UNSAFE, record_migrate.UNKNOWN, record_migrate.FINDINGS):
        row = module_replace.Replacement("a.py", verdict, "swap", "", "")
        if row.writable:
            return _fail(out, f"{verdict} read as writable")
    clean = module_replace.Replacement("a.py", record_migrate.CLEAN, "swap", "", "")
    if not clean.writable:
        return _fail(out, "CLEAN did not read as writable")
    return 0


def the_render_names_both_the_verdict_and_the_file(out: list[str]) -> int:
    """Check a refusal says WHICH file and WHICH definition, so a reader can open it."""
    row = module_replace.Replacement("a.py", module_replace.UNSAFE, "swap", "why", "")
    text = "\n".join(module_replace.render(row, applied=False))
    for want in ("a.py", "swap", "nothing written"):
        if want not in text:
            return _fail(out, f"the render omits {want!r}: {text!r}")
    return 0


def an_unsafe_render_says_nothing_about_the_checker(out: list[str]) -> int:
    """Check UNSAFE is reported as a GUARD refusal, never as a checker verdict.

    ⚑ THE THREE REFUSALS ARE PAID DOWN BY DIFFERENT WORK. FINDINGS is a lint result, UNSAFE is a
    claim about CONTENT, UNKNOWN is a fact about the environment — collapsing them sends a reader
    to the wrong repair.
    """
    row = module_replace.Replacement("a.py", module_replace.UNSAFE, "swap", "why", "")
    if "GUARD" not in "\n".join(module_replace.render(row, applied=False)):
        return _fail(out, "UNSAFE does not name the guard")
    unknown = module_replace.Replacement("a.py", record_migrate.UNKNOWN, "swap", "", "")
    if "CHECKER could not run" not in "\n".join(module_replace.render(unknown, applied=False)):
        return _fail(out, "UNKNOWN does not name the checker")
    return 0


def the_lattice_is_record_migrates(out: list[str]) -> int:
    """Check the verdict vocabulary is imported, not restated.

    ⚑ A SECOND SPELLING OF CLEAN WOULD DRIFT the first time either module moved, and this module's
    `writable` defers to `record_migrate.CLEAN` precisely so it cannot.
    """
    if module_replace.UNSAFE != module_trim.UNSAFE:
        return _fail(out, "UNSAFE is a second spelling rather than the shared one")
    return 0


def a_real_module_replaces_and_stays_clean(out: list[str]) -> int:
    """Check the whole transform on a live file — a RELATION, never a pinned verdict.

    ⚑⚑⚑ A COUNT OR A FIXED VERDICT HERE WOULD GO RED WHEN THE TREE MOVES, reporting correct work
    as a defect. What holds across every tree state is that replacing a definition with ITSELF
    changes no CODE — the transform's identity element, which a transform that corrupted the file
    would fail.

    ⚑⚑ AND THE INVARIANT IS CODE LINES, NOT BYTES, WHICH IS A REAL LIMIT RATHER THAN A WEAKENING.
    A first cut asserted byte-identity and failed: `code_for_node` returns a statement WITHOUT the
    blank run libcst holds as the next statement's leading whitespace, so re-parsing that text and
    splicing it back cannot reproduce the original spacing. The arm was asserting a promise the
    module never made. `module_trim._body` is the unit the guard itself compares, for the reason
    its own docstring gives — blank runs are necessarily disturbed and demanding they match is how
    a guard gets switched off.
    """
    target = corpus.ROOT / "substrate" / "module_replace.py"
    source = target.read_text(encoding="utf-8")
    span = _span_of(source, "outside_span")
    if not span:
        return _fail(out, "the live module no longer defines outside_span")
    same = _replaced(source, "outside_span", span)
    if module_trim._body(same) != module_trim._body(source):  # noqa: SLF001 — the shared unit
        return _fail(out, "replacing a definition with itself changed a code line")
    if module_replace.outside_span(source, same, "outside_span"):
        return _fail(out, "an identity replacement was accused by the guard")
    return 0


_ARMS = (
    an_untouched_neighbour_passes,
    a_dropped_neighbour_is_caught,
    a_rewritten_neighbour_is_caught,
    an_import_may_move_either_way,
    a_method_sharing_the_name_is_not_the_target,
    an_absent_name_is_a_refusal,
    only_clean_is_writable,
    the_render_names_both_the_verdict_and_the_file,
    an_unsafe_render_says_nothing_about_the_checker,
    the_lattice_is_record_migrates,
    a_real_module_replaces_and_stays_clean,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 2 + 3 + 4 + 3 + 2 + 1 + 3


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"module-replace selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"module-replace selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
