#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `module_trim` — the mode that makes a trim a write instead of a retype.

⚑⚑⚑ A NEW WRITE PATH WITH NO CASES IS THE VACUOUS-VERIFICATION SHAPE. This module writes source
files, and the per-file gate REVERTS a file carrying any finding — so an unguarded trim costs a
whole re-derivation, which is exactly the cost this mode exists to close. The arms therefore pin
the two properties the mode is FOR, not that libcst can delete a node.

⚑⚑ THE CONSERVATION GUARD IS THE FIRST PROPERTY, AND IT IS ASSERTED IN BOTH DIRECTIONS. A trim
that dropped the wrong `def` is perfectly lintable — a CLEAN checker report says nothing about
whether content survived. `split_lemmas`' Agda-side form of this comparison caught seven distinct
silent-deletion bugs; the arms here plant a LOSS and an INVENTION and require the guard to refuse
each, plus a correct trim it must NOT refuse (a guard that refused everything would pass the first
two and be useless).

⚑⚑ THE SECOND PROPERTY IS THAT THE WRITTEN TEXT IS THE CHECKED TEXT. `consider` guards and reports
against what `ruff --fix` LEAVES, read back from staging rather than reconstructed. Asserted as an
identity against `record_migrate._fixed`, not as a guess at which fixes ruff applies.

⚑⚑⚑ THE THIRD IS THE DISPATCH BLOCK, AND IT IS THE ONE WITH TWO SIDES THAT MUST BOTH BE PINNED. An
`if __name__ == "__main__":` guard reaching only trimmed names is TAIL and must come out; one that
also reaches a survivor is a CLI that outlives its cases and must be REFUSED. An arm asserting only
the first would pass a mode that took every guard it saw — which would silently delete entry
points, the worst shape this tool has. So both directions are planted, and the classifier is
additionally shown to reject an `if __name__ != "__main__"` and a plain `if`.

⚑⚑ THE CHECKER IS INJECTED THROUGH `sys.modules`, WHICH IS THE MODULE'S OWN DOOR. `record_migrate`
reaches its checker via `gate_module.gate_module("pycheck_show.py")`, whose first branch returns an
already-imported gate as-is — so registering a stub there fixes the verdict deterministically,
without making a real ruff+mypy run a precondition of this suite. The helpers are imported from
`record_migrate_selftest` rather than re-declared: two copies of a stub drift.

⚑⚑ AND THE FIXTURES LIVE INSIDE THE PROJECT. `consider` computes `path.relative_to(corpus.ROOT)`,
so a fixture in a `/tmp` TemporaryDirectory raises before any trimming happens — the same
path-keyed fact that makes the staging file live in the tree.
"""

from __future__ import annotations

import sys
from pathlib import Path

import libcst as cst

from substrate import module_trim, record_migrate
from substrate.record_migrate_selftest import _Installed, _Planted, _Stub

# A module with an inline tail: a public def, a helper used only by the tail, and the tail itself.
# ⚑ THE SHAPE THE SIX HAND-DONE SPLITS HAD. `Path` is used ONLY by `selftest`, so trimming the tail
# strands the import — the F401/F821 dilemma this mode dissolves.
_TAILED = '''"""Doc."""

from __future__ import annotations

from pathlib import Path


def public(value: int) -> int:
    """Return the value unchanged."""
    return value


def _only_for_the_tail(root: Path) -> str:
    """Return the root's name."""
    return root.name


def selftest() -> int:
    """Run the arm."""
    return 0 if _only_for_the_tail(Path(".")) else 1
'''

# The names the tail is made of.
_TAIL_NAMES = ("selftest", "_only_for_the_tail")

# A module whose CLASS carries a method sharing the tail's name — the top-level-only arm.
_METHOD = '''"""Doc."""

from __future__ import annotations


class Holder:
    """A class with a method named like a module-level tail."""

    def selftest(self) -> int:
        """Return zero."""
        return 0
'''

# A module whose tail is reached by an `if __name__ == "__main__":` block — THE MEASURED WALL.
# ⚑ `selftest` is referenced ONLY by the dispatch block, so trimming the def and leaving the block
# strands the call: the trim came back FINDINGS (`F821 Undefined name selftest`) and wrote nothing.
_DISPATCHED = '''"""Doc."""

from __future__ import annotations

import sys


def public(value: int) -> int:
    """Return the value unchanged."""
    return value


def selftest() -> int:
    """Run the arm."""
    return 0


if __name__ == "__main__":
    sys.exit(selftest())
'''

# A module whose dispatch block reaches BOTH the tail and a `main` that SURVIVES the trim.
# ⚑ THE REFUSAL FIXTURE. This module's command line outlives its cases, so the block is NOT tail
# and taking it would silently delete the entry point.
_CLI = '''"""Doc."""

from __future__ import annotations

import sys


def main() -> int:
    """Run the tool."""
    return 0


def selftest() -> int:
    """Run the arm."""
    return 0


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
'''

# Where a fixture is planted. ⚑ Inside the project — `consider` takes `relative_to(corpus.ROOT)`.
_FIXTURE = ".module-trim-case.py"

# What an `--apply` arm ALSO creates, so `_Planted` can take it away again.
# ⚑⚑ THE SIBLING IS A SECOND ARTEFACT AND IT LEAKED. `module_trim --apply` writes the trimmed
# module AND this file beside it; `_Planted` unlinked only the planted path, so the leftover
# survived as an untracked file and the NEXT run's apply arms refused with *"already exists"*.
# MEASURED: two failures, then three on an identical re-run, back to two once it was removed.
# ⚑ SPELLED HERE RATHER THAN DERIVED IN THE HELPER, because what a trim writes is `module_trim`'s
# knowledge — deriving it there would invert the dependency, and re-implementing the naming rule
# would be a second authority for it.
_SIBLING = module_trim.sibling_of(_FIXTURE)

# What an unstated or empty request must exit with.
_TWO = 2


def _guard_of(source: str) -> cst.BaseStatement:
    """Return the last top-level statement of a fixture — its dispatch block."""
    return cst.parse_module(source).body[-1]


def a_tail_and_its_private_helper_come_out_together(out: list[str]) -> int:
    """Check both requested definitions leave the module and land in the extracted text.

    ⚑ THE PARTITION IS THE POINT: each name lands in EXACTLY ONE place. A trim that removed the
    definitions without carrying their text would satisfy "gone from the module" and lose the code.
    """
    trimmed, extracted, taken, _why = module_trim._excised(_TAILED, _TAIL_NAMES)  # noqa: SLF001
    if sorted(taken) != sorted(_TAIL_NAMES):
        out.append(f"selftest: the trim took {taken!r}, not both tail definitions")
        return 1
    for name in _TAIL_NAMES:
        if f"def {name}" in trimmed:
            out.append(f"selftest: {name} survived the trim")
            return 1
        if f"def {name}" not in extracted:
            out.append(f"selftest: {name} was deleted rather than extracted")
            return 1
    if "def public" not in trimmed or "def public" in extracted:
        out.append("selftest: an unrequested definition was moved")
        return 1
    return 0


def a_method_sharing_the_name_is_not_trimmed(out: list[str]) -> int:
    """Check a method named `selftest` is left alone — TOP LEVEL IS A FACT, NOT A DEPTH GUESS.

    ⚑⚑ A METHOD THAT SHARES A SPELLING IS A DIFFERENT DEFINITION. Removing it because the
    module-level one was asked for is the silent-deletion shape, and the resulting class still
    parses — so nothing downstream of the trim would notice.
    """
    trimmed, extracted, taken, _why = module_trim._excised(_METHOD, ("selftest",))  # noqa: SLF001
    if taken:
        out.append(f"selftest: a method was trimmed as a top-level definition: {taken!r}")
        return 1
    if "def selftest" not in trimmed or extracted.strip():
        out.append("selftest: the method was excised from its class")
        return 1
    return 0


def a_name_that_is_not_there_is_a_refusal_not_a_no_op(out: list[str]) -> int:
    """Check an unmatched name is reported UNSAFE rather than silently skipped.

    ⚑⚑⚑ TRIMMING FOUR OF FIVE REQUESTED NAMES IS PLAUSIBLE AND WRONG. The caller is about to delete
    the sibling they moved these into; a silent partial trim loses the fifth for good. Same shape as
    the `rglob` on a non-directory that reported a silent zero — an unsupported REQUEST rendered as
    an empty result.
    """
    if module_trim.missing(("a", "b"), ("a",)) != ("b",):
        out.append("selftest: an unmatched name was not reported missing")
        return 1
    if module_trim.missing(("a",), ("a",)):
        out.append("selftest: a matched name was reported missing")
        return 1
    with _Installed(_Stub("")), _Planted(_TAILED, _FIXTURE) as path:
        trim = module_trim.consider(path, ("selftest", "no_such_definition"))
        if trim.verdict != module_trim.UNSAFE or trim.writable:
            out.append(f"selftest: an absent name yielded a writable {trim.verdict!r}")
            return 1
        if "no_such_definition" not in trim.report:
            out.append(f"selftest: the refusal does not name the absent def: {trim.report!r}")
            return 1
    return 0


def a_correct_trim_conserves_every_code_line(out: list[str]) -> int:
    """Check the guard passes a trim that loses nothing — THE ARM THAT KEEPS THE GUARD USEFUL.

    ⚑⚑ WITHOUT THIS, A GUARD THAT REFUSED UNCONDITIONALLY WOULD PASS EVERY OTHER GUARD ARM. A
    predicate asserted only on its negative side is indistinguishable from a constant one.
    """
    trimmed, extracted, _taken, _why = module_trim._excised(_TAILED, _TAIL_NAMES)  # noqa: SLF001
    reasons = module_trim.conserved(_TAILED, trimmed, extracted)
    if reasons:
        out.append(f"selftest: a correct trim was refused: {reasons!r}")
        return 1
    return 0


def a_lost_line_is_caught_by_the_guard(out: list[str]) -> int:
    """Check the guard refuses a partition that DROPPED a body line.

    ⚑⚑⚑ THE SEVEN-BUG DIRECTION. `split_lemmas` caught seven distinct silent deletions with exactly
    this comparison; a mechanical extractor's characteristic output is a file that reads perfectly
    and is missing a definition.
    """
    trimmed, extracted, _taken, _why = module_trim._excised(_TAILED, _TAIL_NAMES)  # noqa: SLF001
    lost = trimmed.replace("    return value\n", "")
    reasons = module_trim.conserved(_TAILED, lost, extracted)
    if not reasons:
        out.append("selftest: a dropped body line passed the conservation guard")
        return 1
    if not any("vanished" in reason for reason in reasons):
        out.append(f"selftest: the loss was not named as a loss: {reasons!r}")
        return 1
    return 0


def an_invented_line_is_caught_by_the_guard(out: list[str]) -> int:
    """Check the guard refuses a partition holding a line the original never had.

    ⚑⚑ THE OTHER DIRECTION, AND A LINE COUNT CANNOT SEE IT. A transformer that REWROTE a line while
    moving it loses nothing and conserves the count; only comparing the lines themselves catches it.
    """
    trimmed, extracted, _taken, _why = module_trim._excised(_TAILED, _TAIL_NAMES)  # noqa: SLF001
    invented = trimmed + "\nSNEAKED = 1\n"
    reasons = module_trim.conserved(_TAILED, invented, extracted)
    if not reasons:
        out.append("selftest: an invented line passed the conservation guard")
        return 1
    if not any("from nowhere" in reason for reason in reasons):
        out.append(f"selftest: the invention was not named as one: {reasons!r}")
        return 1
    return 0


def a_duplicated_line_is_caught_even_though_nothing_was_lost(out: list[str]) -> int:
    """Check the guard is a MULTISET comparison, not a set one.

    ⚑⚑ A SET COMPARISON WOULD PASS AN EXCISION THAT RAN TWICE — every line still present somewhere,
    one of them twice. That is how a duplicated definition reaches disk looking correct.
    """
    trimmed, extracted, _taken, _why = module_trim._excised(_TAILED, _TAIL_NAMES)  # noqa: SLF001
    reasons = module_trim.conserved(_TAILED, trimmed, extracted + extracted)
    if not reasons:
        out.append("selftest: a doubled extraction passed a guard that must be a multiset check")
        return 1
    return 0


def a_stranded_import_may_vanish_but_a_body_line_may_not(out: list[str]) -> int:
    """Check the import exemption covers BOTH directions and the body exemption NEITHER.

    ⚑⚑⚑ `ruff --fix` REMOVING THE NOW-UNUSED IMPORT IS THE WHOLE POINT OF THIS MODE, so the guard
    must tolerate an import disappearing. ⚑ AND APPEARING: the guard's own record (W5, gate-G368)
    is that the one-way form REFUSED A CORRECT TRIM — ruff NARROWS `from substrate import a, b, c`
    to `from substrate import a, b`, which vanishes AND appears as one edit. This arm asserted the
    abandoned one-directional rule for a day after the guard moved, reporting the guard's design as
    a defect; the discriminating question (*does an invented BODY line still refuse?*) is answered
    below, in both directions, because that is the property the seven silent-deletion bugs were
    caught by and the only one the import exemption must never reach.
    """
    trimmed, extracted, _taken, _why = module_trim._excised(_TAILED, _TAIL_NAMES)  # noqa: SLF001
    without_import = trimmed.replace("from pathlib import Path\n", "")
    if module_trim.conserved(_TAILED, without_import, extracted):
        out.append("selftest: a stranded import vanishing was refused — the fixer's own work")
        return 1
    with_import = trimmed + "\nimport os\n"
    if module_trim.conserved(_TAILED, with_import, extracted):
        out.append("selftest: a rewritten import was refused — the narrowing the fixer produces")
        return 1
    with_body = trimmed + "\ninvented = 1\n"
    if not module_trim.conserved(_TAILED, with_body, extracted):
        out.append("selftest: an INVENTED body line passed — the import exemption reached the body")
        return 1
    without_body = extracted.replace("    return root.name\n", "", 1)
    if without_body == extracted:
        out.append("selftest: the fixture's body line was not found — the arm measured nothing")
        return 1
    if not module_trim.conserved(_TAILED, trimmed, without_body):
        out.append("selftest: a VANISHED body line passed — the silent-deletion check is gone")
        return 1
    return 0


def only_a_real_main_guard_is_recognised(out: list[str]) -> int:
    """Check the classifier reads the comparison's STRUCTURE — THE DISCRIMINATOR FOR THIS ARM.

    ⚑⚑⚑ A PREDICATE THAT ALWAYS SAID YES WOULD PASS EVERY OTHER DISPATCH ARM HERE. So the negatives
    are planted explicitly: an `if __name__ != "__main__"` is the OPPOSITE block and matching it
    would take the branch that runs on import; a plain `if` and a def are not guards at all. A
    substring test for `__main__` would accept the first of these and a docstring mentioning it.
    """
    if not module_trim.is_dispatch_guard(_guard_of(_DISPATCHED)):
        out.append("selftest: a real `__main__` guard was not recognised — the mode is dead")
        return 1
    negatives = (
        'if __name__ != "__main__":\n    pass\n',
        'if __name__ == "__other__":\n    pass\n',
        "if True:\n    pass\n",
        "def selftest() -> int:\n    return 0\n",
    )
    for negative in negatives:
        if module_trim.is_dispatch_guard(_guard_of(negative)):
            out.append(f"selftest: a non-guard was classified as a dispatch block: {negative!r}")
            return 1
    return 0


def an_attribute_base_is_read_but_its_leaf_is_not(out: list[str]) -> int:
    """Check `names_used` collects `sys` from `sys.exit`, and never `exit`.

    ⚑⚑ COLLECTING THE LEAF WOULD REFUSE CORRECT TRIMS. A guard calling `sys.exit(selftest())` would
    appear to reference a definition named `exit`; if the module happened to define one, the block
    would be read as a surviving CLI and the trim refused for a name that is not a reference at all.
    """
    used = module_trim.names_used(_guard_of(_DISPATCHED))
    if "sys" not in used:
        out.append(f"selftest: an attribute's base was not read as a name: {sorted(used)!r}")
        return 1
    if "exit" in used:
        out.append("selftest: an attribute's LEAF was read as a name — a false survivor")
        return 1
    if "selftest" not in used:
        out.append("selftest: the guard's call to the tail was not seen")
        return 1
    return 0


def a_guard_reaching_only_trimmed_names_comes_out_as_tail(out: list[str]) -> int:
    """Check the dispatch block leaves with the definitions it references — THE CLOSED BOUND.

    ⚑⚑⚑ THIS IS THE LIMIT THE ARM EXISTS TO RECORD AS CLOSED. Trimming `selftest` out of a module
    like `_DISPATCHED` used to come back FINDINGS with `F821 Undefined name selftest`, because the
    block is not a named definition the trim could take. It is now partitioned out WITH the tail.
    """
    trimmed, extracted, taken, why = module_trim._excised(_DISPATCHED, ("selftest",))  # noqa: SLF001
    if why:
        out.append(f"selftest: a tail-only dispatch block was refused: {why!r}")
        return 1
    if taken != ("selftest",):
        out.append(f"selftest: the trim took {taken!r}")
        return 1
    if "__main__" in trimmed:
        out.append("selftest: the dispatch block survived the trim — the F821 would land")
        return 1
    if "__main__" not in extracted:
        out.append("selftest: the dispatch block was DELETED rather than extracted")
        return 1
    if "def public" not in trimmed:
        out.append("selftest: a surviving definition was taken with the block")
        return 1
    return 0


def a_guard_that_outlives_the_trim_is_refused_by_name(out: list[str]) -> int:
    """Check a block reaching a SURVIVOR is refused, and the survivor is named.

    ⚑⚑⚑ THE CONSERVATIVE HALF, AND THE ARM THAT KEEPS THE ONE ABOVE HONEST. A mode that took every
    guard it saw would pass `a_guard_reaching_only_trimmed_names_comes_out_as_tail` and silently
    delete this module's entry point — the worst output this tool could produce, since the file
    still imports, still lints, and simply stops being runnable.
    """
    trimmed, _extracted, _taken, why = module_trim._excised(_CLI, ("selftest",))  # noqa: SLF001
    if not why:
        out.append("selftest: a dispatch block calling a SURVIVING `main` was taken as tail")
        return 1
    if "main" not in why:
        out.append(f"selftest: the refusal does not name the survivor: {why!r}")
        return 1
    if "__main__" not in trimmed:
        out.append("selftest: the refused block was removed anyway")
        return 1
    return 0


def a_refused_dispatch_block_is_unsafe_and_unwritable(out: list[str]) -> int:
    """Check the refusal reaches `consider` as UNSAFE, never as a lint FINDINGS.

    ⚑⚑ THE VERDICT IS THE READER'S REPAIR INSTRUCTION. Letting the stranded reference fall through
    to the checker would report `F821` — the SYMPTOM — and send the reader hunting a lint fix when
    what they need is to rewrite their entry point. UNSAFE says the excision as asked is wrong.
    """
    with _Installed(_Stub("")), _Planted(_CLI, _FIXTURE) as path:
        trim = module_trim.consider(path, ("selftest",))
        if trim.verdict != module_trim.UNSAFE or trim.writable:
            out.append(f"selftest: a CLI-outliving trim yielded a writable {trim.verdict!r}")
            return 1
        if "main" not in trim.report:
            out.append(f"selftest: the refusal does not name the survivor: {trim.report!r}")
            return 1
        if path.read_text(encoding="utf-8") != _CLI:
            out.append("selftest: a refused trim altered the file")
            return 1
    return 0


def the_taken_dispatch_block_is_conserved_not_exempted(out: list[str]) -> int:
    """Check the block's lines are weighed by the conservation guard like any other content.

    ⚑⚑⚑ AN EXEMPTION HERE WOULD RE-OPEN THE HOLE THE BOTH-BASELINES RULE CLOSED. A block excused
    from the partition could vanish from BOTH sides and be accused by neither — which is exactly the
    silent deletion the guard exists to make impossible. So the arm plants a partition that DROPS
    the block and requires the guard to catch it.
    """
    trimmed, extracted, _taken, _why = module_trim._excised(_DISPATCHED, ("selftest",))  # noqa: SLF001
    if module_trim.conserved(_DISPATCHED, trimmed, extracted):
        out.append("selftest: a correct dispatch-block trim was refused by the conservation guard")
        return 1
    if not module_trim.conserved(_DISPATCHED, trimmed, ""):
        out.append(
            "selftest: a DROPPED dispatch block passed the guard — it is exempted, not "
            "partitioned, and could vanish silently"
        )
        return 1
    return 0


def the_dispatch_wall_now_reaches_clean_end_to_end(out: list[str]) -> int:
    """Check the whole pipeline lands the trim the wall used to refuse.

    ⚑⚑ ASSERTED ON THE BYTES, NOT THE VERDICT. `--apply` is run and the fixture re-read: the tail
    gone, the block gone, the keeper kept. A `consider` that reported CLEAN while `main` wrote
    something else would pass a verdict-only arm.
    """
    with _Installed(_Stub("")), _Planted(_DISPATCHED, _FIXTURE, (_SIBLING,)) as path:
        if module_trim.main(["--apply", str(path), "selftest"]):
            out.append("selftest: the dispatch-block trim did not exit 0")
            return 1
        landed = path.read_text(encoding="utf-8")
        if "def selftest" in landed:
            out.append("selftest: --apply left the tail in the module")
            return 1
        if "__main__" in landed:
            out.append("selftest: --apply left the dispatch block — the F821 landed")
            return 1
        if "def public" not in landed:
            out.append("selftest: --apply removed a definition it was not asked for")
            return 1
    return 0


def only_clean_is_writable(out: list[str]) -> int:
    """Check `Trim.writable` admits CLEAN and refuses UNSAFE, FINDINGS and UNKNOWN alike.

    ⚑⚑⚑ IF ONLY ONE ARM EXISTED IT WOULD BE THIS ONE. UNSAFE is refused on the same footing as the
    checker's verdicts: a guard that refused has established that content would be LOST, which is
    strictly worse than a lint finding and must never reach disk either.
    """
    for verdict in (module_trim.UNSAFE, record_migrate.FINDINGS, record_migrate.UNKNOWN):
        trim = module_trim.Trim(
            relpath="x.py", verdict=verdict, names=("selftest",), removed="", report="", source=""
        )
        if trim.writable:
            out.append(f"selftest: a {verdict} trim reported itself writable")
            return 1
    clean = module_trim.Trim(
        relpath="x.py",
        verdict=record_migrate.CLEAN,
        names=("selftest",),
        removed="",
        report="",
        source="",
    )
    if not clean.writable:
        out.append("selftest: a CLEAN trim refused to be written — nothing would ever land")
        return 1
    return 0


def a_flagged_trim_is_not_written_and_the_file_is_untouched(out: list[str]) -> int:
    """Check `consider` reaches the checker's verdict and writes nothing on the way.

    ⚑⚑ THE END-TO-END FORM OF THE CONTRACT. `consider` is a pure question; only `main` writes. A
    considering step that touched the file would have already spent the gate's revert.
    """
    with _Installed(_Stub("--- ruff ---\nx.py:1:1: F401\n")), _Planted(_TAILED, _FIXTURE) as path:
        trim = module_trim.consider(path, _TAIL_NAMES)
        if trim.verdict != record_migrate.FINDINGS or trim.writable:
            out.append(f"selftest: a flagged trim read as a writable {trim.verdict!r}")
            return 1
        if path.read_text(encoding="utf-8") != _TAILED:
            out.append("selftest: `consider` altered the file it was only asked to consider")
            return 1
    return 0


def a_checker_that_could_not_run_blocks_the_trim(out: list[str]) -> int:
    """Check UNKNOWN survives the whole path to a non-writable trim.

    ⚑ THE THIRD STATE IS THE ONE THAT ROTS. Collapsing it into CLEAN writes a file on the strength
    of a check that never ran; this mode inherits the lattice rather than re-deriving it, so the arm
    asserts the inheritance actually happened.
    """
    broken = f"--- mypy ---\n⚑ {record_migrate.COULD_NOT_RUN}: exit 2\n"
    with _Installed(_Stub(broken)), _Planted(_TAILED, _FIXTURE) as path:
        trim = module_trim.consider(path, _TAIL_NAMES)
        if trim.verdict != record_migrate.UNKNOWN:
            out.append(f"selftest: an unrunnable checker yielded {trim.verdict!r}")
            return 1
        if trim.writable:
            out.append("selftest: an UNKNOWN trim would have been written")
            return 1
    return 0


def the_written_text_is_the_checked_text(out: list[str]) -> int:
    """Check a CLEAN trim carries the FIXED source, not the raw excision.

    ⚑⚑⚑ THE VERDICT WOULD OTHERWISE BE ABOUT A DIFFERENT DOCUMENT. `ruff --fix` is what removes the
    stranded import, so the raw excision still holds it — writing that would commit the very F401
    the mode exists to dissolve. Asserted as an identity against `_fixed`, which re-reads the staged
    file rather than reconstructing it; a re-serialization between check and write voids this.
    """
    with _Installed(_Stub("")), _Planted(_TAILED, _FIXTURE) as path:
        trim = module_trim.consider(path, _TAIL_NAMES)
        if trim.verdict != record_migrate.CLEAN:
            out.append(f"selftest: the fixture did not reach CLEAN ({trim.verdict}): {trim.report}")
            return 1
        raw, _extracted, _taken, _why = module_trim._excised(_TAILED, _TAIL_NAMES)  # noqa: SLF001
        if trim.source != record_migrate._fixed(raw):  # noqa: SLF001 — the shared fixer
            out.append(
                "selftest: a CLEAN trim's source is not what the fixer left — "
                "the checked text and the written text have diverged"
            )
            return 1
    return 0


def the_stranded_import_is_gone_from_what_would_land(out: list[str]) -> int:
    """Check the F401/F821 dilemma is actually dissolved — THE MEASURED WALL.

    ⚑⚑⚑ THIS IS THE WHOLE MODE IN ONE ASSERTION. `Path` is used only by the trimmed tail, so the
    raw excision strands its import; the text that would land must not. Every hand-done trim hit
    exactly this and had to retype the file. The arm reads the SOURCE THAT WOULD BE WRITTEN, not the
    transform output — checking the latter would assert nothing about what lands.
    """
    with _Installed(_Stub("")), _Planted(_TAILED, _FIXTURE) as path:
        trim = module_trim.consider(path, _TAIL_NAMES)
        raw, _extracted, _taken, _why = module_trim._excised(_TAILED, _TAIL_NAMES)  # noqa: SLF001
        if "from pathlib import Path" not in raw:
            out.append(
                "selftest: the raw excision did not strand the import — the fixture no "
                "longer reproduces the wall this mode exists for"
            )
            return 1
        if "from pathlib import Path" in trim.source:
            out.append(
                "selftest: the stranded import survived into what would be written — "
                "the F401 the mode dissolves would land"
            )
            return 1
        if "def public" not in trim.source:
            out.append("selftest: the surviving definition is not in what would be written")
            return 1
    return 0


def intent_is_stated_never_defaulted(out: list[str]) -> int:
    """Check `main` refuses to act without `--apply` or `--dry-run`, and refuses an empty request.

    ⚑⚑ NEITHER DEFAULT IS SAFE, and a trim with no names is a third refusal: it would report a
    clean no-op, which reads exactly like a successful trim.
    """
    if module_trim.main([_FIXTURE, "selftest"]) != _TWO:
        out.append("selftest: an unstated intent did not refuse with exit 2")
        return 1
    if module_trim.main(["--dry-run"]) != _TWO:
        out.append("selftest: a stated intent with no module did not refuse with exit 2")
        return 1
    if module_trim.main(["--dry-run", _FIXTURE]) != _TWO:
        out.append("selftest: a trim naming no definitions did not refuse with exit 2")
        return 1
    return 0


def a_dry_run_writes_nothing(out: list[str]) -> int:
    """Check `--dry-run` leaves the module byte-identical even when the trim is CLEAN.

    ⚑ THE HALF OF THE INTENT CONTRACT THAT IS EASY TO GET WRONG SILENTLY. A dry run that wrote
    would look exactly like a successful apply, and the caller asked to LOOK.
    """
    with _Installed(_Stub("")), _Planted(_TAILED, _FIXTURE) as path:
        if module_trim.main(["--dry-run", str(path), *_TAIL_NAMES]):
            out.append("selftest: a clean dry run did not exit 0")
            return 1
        if path.read_text(encoding="utf-8") != _TAILED:
            out.append("selftest: a --dry-run wrote to the module")
            return 1
    return 0


def an_apply_lands_the_fixed_text(out: list[str]) -> int:
    """Check `--apply` writes the trimmed module — THE ONLY ARM THAT LETS A WRITE HAPPEN.

    ⚑⚑ ASSERTED AGAINST THE FILE, NOT THE RETURN CODE. A `main` that reported success and wrote
    nothing would pass every other arm here, so the fixture is re-read from disk and the three
    properties are checked on the bytes: the tail gone, the stranded import gone, the keeper kept.
    """
    with _Installed(_Stub("")), _Planted(_TAILED, _FIXTURE, (_SIBLING,)) as path:
        if module_trim.main(["--apply", str(path), *_TAIL_NAMES]):
            out.append("selftest: a clean apply did not exit 0")
            return 1
        landed = path.read_text(encoding="utf-8")
        if "def selftest" in landed:
            out.append("selftest: --apply left the tail in the module")
            return 1
        if "from pathlib import Path" in landed:
            out.append("selftest: --apply landed the stranded import")
            return 1
        if "def public" not in landed:
            out.append("selftest: --apply removed a definition it was not asked for")
            return 1
    return 0


def an_unsafe_trim_is_never_written_by_main(out: list[str]) -> int:
    """Check `--apply` on a refused trim leaves the module byte-identical and exits non-zero.

    ⚑⚑⚑ THE GUARD MUST BIND AT THE WRITE, NOT ONLY IN THE REPORT. A refusal that printed UNSAFE and
    then wrote anyway would be the false green in its worst place — and the arms above assert the
    predicate, which is not the same as asserting that `main` consults it.
    """
    with _Installed(_Stub("")), _Planted(_TAILED, _FIXTURE) as path:
        code = module_trim.main(["--apply", str(path), "selftest", "no_such_definition"])
        if not code:
            out.append("selftest: an UNSAFE apply exited 0")
            return 1
        if path.read_text(encoding="utf-8") != _TAILED:
            out.append("selftest: an UNSAFE trim was written to disk")
            return 1
    return 0


def a_trim_is_frozen_and_slotted(out: list[str]) -> int:
    """Check `Trim` is the immutable record this tree converted toward.

    ⚑ A MUTABLE TRIM WOULD LET A VERDICT BE EDITED BETWEEN THE GUARD AND THE WRITE, which is the one
    window this mode closes.
    """
    trim = module_trim.Trim(
        relpath="a.py", verdict=module_trim.UNSAFE, names=(), removed="", report="", source=""
    )
    try:
        trim.verdict = record_migrate.CLEAN  # type: ignore[misc]
    except (AttributeError, TypeError):
        pass
    else:
        out.append("selftest: a verdict could be reassigned after the guard")
        return 1
    if hasattr(trim, "__dict__"):
        out.append("selftest: `Trim` carries a __dict__ — it is not slotted")
        return 1
    return 0


def the_three_refusals_are_never_collapsed(out: list[str]) -> int:
    """Check the summary names UNSAFE and UNKNOWN for what they are.

    ⚑⚑ THEY ARE PAID DOWN BY DIFFERENT WORK. FINDINGS is fixed by editing the module; UNSAFE means
    the excision itself was wrong; UNKNOWN means nothing was measured. A reader who reads only
    "refused" would try the wrong repair.
    """
    unsafe = module_trim.Trim(
        relpath="a.py", verdict=module_trim.UNSAFE, names=(), removed="", report="", source=""
    )
    lines = "\n".join(module_trim.summary(unsafe, applied=False))
    if "CONSERVATION GUARD" not in lines or "nothing written" not in lines:
        out.append(f"selftest: an UNSAFE summary does not say what it means: {lines!r}")
        return 1
    unknown = module_trim.Trim(
        relpath="a.py", verdict=record_migrate.UNKNOWN, names=(), removed="", report="", source=""
    )
    if "never a clean bill" not in "\n".join(module_trim.summary(unknown, applied=False)):
        out.append("selftest: an UNKNOWN summary did not say the checker had not run")
        return 1
    clean = module_trim.Trim(
        relpath="a.py", verdict=record_migrate.CLEAN, names=(), removed="", report="", source=""
    )
    if "WROTE" not in "\n".join(module_trim.summary(clean, applied=True)):
        out.append("selftest: a written trim was not reported as written")
        return 1
    return 0


def one_bad_report_cannot_bury_the_verdict(out: list[str]) -> int:
    """Check a long checker report is truncated in the render.

    ⚑ THE CAP IS INHERITED FROM `record_migrate`, not restated — a second number would drift.
    """
    long_report = "\n".join(f"line {n}" for n in range(200))
    trim = module_trim.Trim(
        relpath="a.py",
        verdict=record_migrate.FINDINGS,
        names=("selftest",),
        removed="",
        report=long_report,
        source="",
    )
    rendered = module_trim.render(trim)
    if len(rendered) > record_migrate.REPORT_LINES + 1:
        out.append(
            f"selftest: {len(rendered)} line(s) rendered — the cap is {record_migrate.REPORT_LINES}"
        )
        return 1
    return 0


def the_staging_file_does_not_survive_a_trim(out: list[str]) -> int:
    """Check no staging artefact is left in the tree after a trim is considered.

    ⚑ A STAGING FILE LEFT BEHIND IS AN UNTRACKED FILE FOR THE GATE and a candidate for the next
    walk. `consider` calls `_fixed` and `_check`, each of which removes it in a `finally`.
    """
    with _Installed(_Stub("")), _Planted(_TAILED, _FIXTURE) as path:
        module_trim.consider(path, _TAIL_NAMES)
    # ⚑ THIS PROCESS'S staging file, by its PID-suffixed name (gate-G390). The bare `STAGING`
    # stem this arm checked before was a file no process writes any more, so the arm passed
    # VACUOUSLY — asserting the absence of something that could not have been present (W6).
    if record_migrate.staging_path().exists():
        out.append("selftest: the staging file outlived the trim")
        return 1
    return 0


def a_fixture_path_is_resolved_inside_the_project(out: list[str]) -> int:
    """Check `consider` reports a project-relative path — the path-keyed constraint.

    ⚑⚑ `relative_to(corpus.ROOT)` IS WHY FIXTURES ARE PLANTED IN THE TREE. A module outside the
    project does not merely check under different rules; it raises before any trimming happens.
    """
    with _Installed(_Stub("")), _Planted(_TAILED, _FIXTURE) as path:
        trim = module_trim.consider(path, _TAIL_NAMES)
        if trim.relpath != _FIXTURE:
            out.append(f"selftest: the trim reported {trim.relpath!r}, not the relative path")
            return 1
        if Path(trim.relpath).is_absolute():
            out.append("selftest: the reported path is absolute")
            return 1
    return 0


_ARMS = (
    a_tail_and_its_private_helper_come_out_together,
    a_method_sharing_the_name_is_not_trimmed,
    a_name_that_is_not_there_is_a_refusal_not_a_no_op,
    a_correct_trim_conserves_every_code_line,
    a_lost_line_is_caught_by_the_guard,
    an_invented_line_is_caught_by_the_guard,
    a_duplicated_line_is_caught_even_though_nothing_was_lost,
    a_stranded_import_may_vanish_but_a_body_line_may_not,
    only_a_real_main_guard_is_recognised,
    an_attribute_base_is_read_but_its_leaf_is_not,
    a_guard_reaching_only_trimmed_names_comes_out_as_tail,
    a_guard_that_outlives_the_trim_is_refused_by_name,
    a_refused_dispatch_block_is_unsafe_and_unwritable,
    the_taken_dispatch_block_is_conserved_not_exempted,
    the_dispatch_wall_now_reaches_clean_end_to_end,
    only_clean_is_writable,
    a_flagged_trim_is_not_written_and_the_file_is_untouched,
    a_checker_that_could_not_run_blocks_the_trim,
    the_written_text_is_the_checked_text,
    the_stranded_import_is_gone_from_what_would_land,
    intent_is_stated_never_defaulted,
    a_dry_run_writes_nothing,
    an_apply_lands_the_fixed_text,
    an_unsafe_trim_is_never_written_by_main,
    a_trim_is_frozen_and_slotted,
    the_three_refusals_are_never_collapsed,
    one_bad_report_cannot_bury_the_verdict,
    the_staging_file_does_not_survive_a_trim,
    a_fixture_path_is_resolved_inside_the_project,
)

# ⚑ COUNTED PER ARM, because a hardcoded total once hid an added case elsewhere in this tree.
_CASE_COUNT = (
    5
    + 2
    + 4
    + 1
    + 2
    + 2
    + 1
    + 2
    + 5
    + 3
    + 5
    + 3
    + 3
    + 2
    + 4
    + 4
    + 2
    + 2
    + 2
    + 3
    + 3
    + 2
    + 4
    + 2
    + 2
    + 4
    + 1
    + 1
    + 2
)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"module-trim selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"module-trim selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
