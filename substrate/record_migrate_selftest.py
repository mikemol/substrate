#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `record_migrate` — the orchestrator that converted 58 files and had no suite.

⚑⚑⚑ THE PROSPECTIVE CHECK IS THE CONTRACT, SO IT IS WHAT THESE ARMS PIN. This tool exists because
a rewriter that writes and hopes turns N files into N chances to lose one — the per-file gate
REVERTS a file carrying any finding. Six such losses were measured by hand before the tool was
written, and the tool then caught four of its own transform's bugs, none of which reached disk. An
arm that only checked "the transform produces plausible output" would say nothing about that.

⚑⚑ THE VERDICT LATTICE IS THREE-VALUED AND THE THIRD IS THE ONE THAT ROTS. ruff and mypy exit 1
for "flagged something" and 2 for "could not run"; collapsing the second into CLEAN would write
files on the strength of a check that never ran, and collapsing it into FINDINGS would report a
broken invocation as a lint result. `census-green-is-a-fact-about-the-census` is the recurring
shape — so UNKNOWN gets its own arm, on `_verdict` AND on `Outcome.writable`.

⚑⚑ THE CHECKER IS INJECTED THROUGH `sys.modules`, WHICH IS THE MODULE'S OWN DOOR, NOT A HOLE PUNCHED
FOR THE TEST. `_check` reaches the checker via `gate_module.gate_module("pycheck_show.py")`, whose
first branch is *"an already-imported gate is returned as-is"* — so registering a stub under that
name is the sanctioned way to control the verdict. That lets these arms assert the STATE MACHINE
(which report yields which verdict, and which verdict is allowed to reach disk) deterministically,
without making a real ruff+mypy run a precondition of the suite.

⚑ WHAT IS THEREFORE NOT ASSERTED HERE: that ruff and mypy find the right things. That is their
suite, not this one. What is asserted is that whatever they say, this tool routes it correctly —
which is the property the four caught bugs turned on.

⚑⚑ THE FIXTURES LIVE INSIDE THE PROJECT, and that is load-bearing rather than incidental.
`consider` computes `path.relative_to(corpus.ROOT)`, so a fixture in a `/tmp` TemporaryDirectory
raises rather than being converted — the same path-keyed fact that makes the STAGING file live in
the tree. Arms that need a real file plant it under the root and remove it in a `finally`; the one
arm that never touches `corpus.ROOT` (`candidates`, which walks a caller-named root) uses a real
TemporaryDirectory.

⚑⚑⚑ AND THE VERDICT LATTICE IS NOT THE LOOP THAT ACTS ON IT. `only_clean_is_writable` pins the
PREDICATE; for a long time nothing pinned that `main`'s `--apply` loop CONSULTS it. A tool that
computed `writable` perfectly and then wrote the wrong set — or wrote on a non-CLEAN outcome —
would have passed every other arm in this file. The distinction is between a REPORT and a GATE,
and it is the one this tree has watched collapse repeatedly. The `--apply` arms below therefore
assert against THE FILES ON DISK, never by re-reading the predicate the loop consults: they plant
a directory of fixtures whose verdicts DIFFER, run the real loop over it, and read back which
bytes changed. They pin the PROPERTY (only-CLEAN-members, checked-bytes, dry-run-inert) rather
than any named victim file, because a case pinned to an instance expires when the tree moves.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
import types
from pathlib import Path
from typing import Self

from substrate import corpus, record_migrate

# A module holding one `NamedTuple` record — what a candidate file looks like.
_RECORD = '''"""Doc."""

from __future__ import annotations

from typing import NamedTuple


class Planted(NamedTuple):
    """A record planted for the orchestrator."""

    name: str
'''

# A module declaring no record at all — the UNCHANGED population.
_PLAIN = '"""Doc."""\n\nVALUE = 1\n'

# A checker report standing for "ruff flagged something".
_FINDING = "--- ruff ---\nsubstrate/x.py:1:1: F401 unused import\n"

# A checker report standing for "the checker itself did not run".
_BROKEN = f"--- mypy ---\n⚑ {record_migrate.COULD_NOT_RUN}: exit 2\n"

# How many records the two-record fixture declares, and how many files the candidate fixture holds.
_TWO = 2

# The directory the `--apply` loop arms plant their batch in — dot-prefixed and owned by this suite.
_TREE = ".record-migrate-tree"

# A record whose class name is the marker the discriminating stub keys its FINDINGS verdict on.
_MARKED = _RECORD.replace("Planted", "Marked")


class _Stub:
    """A checker whose verdict is fixed by construction — the injected `pycheck_show`.

    ⚑ NAMED CLASS, NOT A LAMBDA OR A `types.SimpleNamespace`. An untyped stand-in makes every value
    it hands back `Any`, which is the untyped-boundary defect this tree has met repeatedly; and the
    module under test declares the surface it needs as a `Protocol`, so the stub should satisfy a
    declared shape rather than duck past it.
    """

    def __init__(self, report: str, flag_marker: str | None = None) -> None:
        """Record the report this checker returns, and the targets it was asked about.

        ⚑⚑ `flag_marker` MAKES ONE STUB DISCRIMINATE RATHER THAN ADDING A SECOND STUB CLASS. The
        `--apply` loop arms need a batch whose verdicts DIFFER per file, but the stub is handed the
        STAGING path, whose name is identical for every file — so the only thing it can key on is
        the staged TEXT. With `flag_marker` set, a staged file containing it reports the findings
        and every other file reports clean. Two stub classes would drift apart; one stub that can
        be asked a question does not.
        """
        self.report = report
        self.flag_marker = flag_marker
        self.seen: list[Path] = []
        # ⚑ THE IDENTITY EACH CHECK WAS TOLD TO STAND FOR, kept beside the staging paths it saw.
        # Both are the same length by construction, so an arm can pair them.
        self.stood_for: list[Path | None] = []

    def run_checks(self, target: Path, stands_for: Path | None = None) -> str:
        """Return this checker's report, remembering which file was checked.

        ⚑⚑⚑ `stands_for` IS ACCEPTED BECAUSE THE PROTOCOL DECLARES IT, AND OMITTING IT BROKE TWO
        SUITES. `record_migrate._check` grew the argument so a prospective file is checked under
        the identity it stands for rather than its staging name (gate-G334), and the `Checker`
        Protocol moved with it — its docstring says outright that a Protocol still declaring the
        one-argument form *"would type-check green and refuse the second argument at the seam"*.
        That is what happened, one layer over: the PROTOCOL moved, the STUB did not, and both
        `record_migrate_selftest` and `module_trim_selftest` died at a TypeError before asserting
        anything — reported UNREAD, which is not a test failure and so reads as coverage.

        ⚑ RECORDED RATHER THAN SWALLOWED. A stub that accepted the argument and dropped it would
        satisfy the signature while leaving the identity untestable, which is the
        accepts-anything shape the named class exists to avoid.
        """
        self.seen.append(target)
        self.stood_for.append(stands_for)
        if self.flag_marker is None:
            return self.report
        staged = target.read_text(encoding="utf-8") if target.exists() else ""
        return self.report if self.flag_marker in staged else ""


class _Installed:
    """Hold a stub checker in `sys.modules` for the body of one arm, then restore what was there."""

    def __init__(self, stub: object) -> None:
        """Record the stub to install under the checker's module name."""
        self.stub = stub
        self.previous: object | None = None
        self.had = False

    def __enter__(self) -> Self:
        """Install the stub, remembering any real module it displaces."""
        self.had = "pycheck_show" in sys.modules
        self.previous = sys.modules.get("pycheck_show")
        sys.modules["pycheck_show"] = self.stub  # type: ignore[assignment]
        return self

    def __exit__(self, *_exc: object) -> None:
        """Put back exactly what was there before — including nothing."""
        if self.had:
            sys.modules["pycheck_show"] = self.previous  # type: ignore[assignment]
        else:
            sys.modules.pop("pycheck_show", None)


class _Planted:
    """Write a fixture INSIDE the project for one arm, and remove it afterwards.

    ⚑⚑ INSIDE THE PROJECT BECAUSE `consider` TAKES `relative_to(corpus.ROOT)`. A fixture in a temp
    directory outside the tree does not merely check under different rules — it raises before any
    checking happens. The staging file has the same constraint for the same path-keyed reason.
    """

    def __init__(self, source: str, name: str, also: tuple[str, ...] = ()) -> None:
        """Record the text to plant, where to plant it, and what else the arm may create.

        ⚑⚑⚑ `also` EXISTS BECAUSE A TOOL UNDER TEST CAN WRITE MORE THAN THE FILE IT WAS GIVEN.
        `module_trim --apply` writes a SIBLING beside the module it trims, and unlinking only the
        planted path left that behind as an untracked file — so the FOLLOWING run's apply arms hit
        *"already exists — it would be overwritten"* and refused. MEASURED: the suite reported two
        failures, then THREE on an identical re-run, and the third vanished when the leftover was
        removed by hand.

        ⚑⚑ A FAILURE COUNT THAT GROWS BETWEEN IDENTICAL RUNS IS THE TELL, and it was the only one
        available: every individual verdict looked like an ordinary refusal, correctly reported by
        a tool doing its job. A leaking suite does not fail — it makes its SUCCESSOR fail.

        ⚑ THE CALLER NAMES THE EXTRA PATHS RATHER THAN THIS HELPER DERIVING THEM. What a trim
        writes is `module_trim`'s knowledge, and reaching for it here would make this suite import
        the other suite's subject — an inverted dependency — while spelling the sibling rule a
        second time would be the two-authorities shape. The arm that knows, says.
        """
        self.source = source
        self.path = corpus.ROOT / name
        self.also = tuple(corpus.ROOT / extra for extra in also)

    def __enter__(self) -> Path:
        """Write the fixture and return its path."""
        self.path.write_text(self.source, encoding="utf-8")
        return self.path

    def __exit__(self, *_exc: object) -> None:
        """Remove the fixture and anything the arm declared it might create, whatever happened."""
        self.path.unlink(missing_ok=True)
        for extra in self.also:
            extra.unlink(missing_ok=True)


class _PlantedTree:
    """Plant a whole DIRECTORY of fixtures inside the project, and remove all of it afterwards.

    ⚑⚑⚑ THE `--apply` LOOP CANNOT BE OBSERVED ON ONE FILE. What the loop can get wrong is WHICH
    members of a batch it writes, and a one-file batch has only one wrong answer available. So the
    loop arms need several files whose verdicts differ — which means a directory, because
    `candidates` walks one.

    ⚑⚑ AND IT LIVES UNDER `corpus.ROOT` FOR `_Planted`'S REASON, NOT A NEW ONE: `consider` computes
    `relative_to(corpus.ROOT)` and `main` writes back through `corpus.ROOT / relpath`, so a
    directory outside the tree raises rather than being converted. It is planted under a
    dot-prefixed directory of its own, so the walked population is created by the arm and destroyed
    with it — **no file any other agent owns is ever inside the root the loop is turned loose on.**
    That is what makes letting the real write loop run acceptable at all.

    ⚑ REMOVAL IS UNCONDITIONAL AND RECURSIVE, because a file the loop WRITES is one this class did
    not create and must still take away. `shutil.rmtree` covers the planted members and anything
    the tool added beside them.
    """

    def __init__(self, members: dict[str, str], name: str = _TREE) -> None:
        """Record the `filename -> source` fixtures and the directory to plant them in."""
        self.members = members
        self.root = corpus.ROOT / name

    def __enter__(self) -> Path:
        """Create the directory, write every member, and return the directory."""
        shutil.rmtree(self.root, ignore_errors=True)
        self.root.mkdir(parents=True)
        for filename, source in self.members.items():
            (self.root / filename).write_text(source, encoding="utf-8")
        return self.root

    def __exit__(self, *_exc: object) -> None:
        """Remove the directory and everything in it, including anything the tool wrote."""
        shutil.rmtree(self.root, ignore_errors=True)


def a_findings_report_is_not_clean(out: list[str]) -> int:
    """Check `_verdict` calls a non-empty lint report FINDINGS.

    ⚑ THE MIDDLE OF THE LATTICE. If this collapsed to CLEAN the whole tool would be a pass-through.
    """
    verdict = record_migrate._verdict(_FINDING)  # noqa: SLF001 — the unit under test
    if verdict != record_migrate.FINDINGS:
        out.append(f"selftest: a lint report read as {verdict!r}, not FINDINGS")
        return 1
    return 0


def an_empty_report_is_clean(out: list[str]) -> int:
    """Check `_verdict` calls an empty report CLEAN — the arm that keeps the tool useful.

    ⚑ WITHOUT THIS, A `_verdict` THAT RETURNED FINDINGS UNCONDITIONALLY WOULD PASS the arm above.
    A predicate asserted only on its positive side is indistinguishable from a constant one.
    """
    if record_migrate._verdict("") != record_migrate.CLEAN:  # noqa: SLF001 — the unit under test
        out.append("selftest: an empty report did not read as CLEAN")
        return 1
    if record_migrate._verdict("   \n\n") != record_migrate.CLEAN:  # noqa: SLF001 — under test
        out.append("selftest: a whitespace-only report did not read as CLEAN")
        return 1
    return 0


def a_checker_that_could_not_run_is_unknown_not_clean(out: list[str]) -> int:
    """Check `COULD NOT RUN` yields UNKNOWN — the third state, and the one that rots.

    ⚑⚑ BOTH COLLAPSES ARE ASSERTED AGAINST. Reading it as CLEAN is the false green this tool exists
    to refuse; reading it as FINDINGS understates it, because a broken invocation is not a lint
    result and the two are paid down by different work.
    """
    verdict = record_migrate._verdict(_BROKEN)  # noqa: SLF001 — the unit under test
    if verdict == record_migrate.CLEAN:
        out.append("selftest: a checker that could not run read as CLEAN — the false green")
        return 1
    if verdict != record_migrate.UNKNOWN:
        out.append(f"selftest: a checker that could not run read as {verdict!r}, not UNKNOWN")
        return 1
    return 0


def only_clean_is_writable(out: list[str]) -> int:
    """Check `Outcome.writable` admits CLEAN and refuses every other verdict — THE CONTRACT ARM.

    ⚑⚑⚑ IF ONLY ONE ARM EXISTED IT WOULD BE THIS ONE. A file carrying any finding must not be
    written, because the per-file gate reverts it and the conversion is lost. UNKNOWN is refused on
    the same footing as FINDINGS: a checker that established nothing cannot authorise a write.

    ⚑⚑ AND IT PINS THE PREDICATE ONLY. That `main`'s write loop CONSULTS it is a separate fact,
    asserted against the files on disk by `only_the_clean_members_of_a_batch_are_written`.
    """
    for verdict in (record_migrate.FINDINGS, record_migrate.UNKNOWN, record_migrate.UNCHANGED):
        outcome = record_migrate.Outcome(
            relpath="x.py", verdict=verdict, records=("R",), flags=(), report="", source=""
        )
        if outcome.writable:
            out.append(f"selftest: a {verdict} outcome reported itself writable")
            return 1
    clean = record_migrate.Outcome(
        relpath="x.py", verdict=record_migrate.CLEAN, records=("R",), flags=(), report="", source=""
    )
    if not clean.writable:
        out.append("selftest: a CLEAN outcome refused to be written — nothing would ever land")
        return 1
    return 0


def a_file_with_findings_is_not_written(out: list[str]) -> int:
    """Check `consider` on a real file returns FINDINGS and leaves the file untouched.

    ⚑⚑ THE END-TO-END FORM OF THE CONTRACT. The arm above pins the predicate; this one pins that
    `consider` reaches it — that a file whose prospective conversion the checker flags comes back
    non-writable, with the original bytes still on disk because nothing writes but `main`.
    """
    with _Installed(_Stub(_FINDING)), _Planted(_RECORD, ".record-migrate-case.py") as path:
        outcome = record_migrate.consider(path)
        if outcome.verdict != record_migrate.FINDINGS:
            out.append(f"selftest: a flagged conversion read as {outcome.verdict!r}")
            return 1
        if outcome.writable:
            out.append("selftest: a flagged conversion reported itself writable")
            return 1
        if path.read_text(encoding="utf-8") != _RECORD:
            out.append("selftest: `consider` altered the file it was only asked to consider")
            return 1
    return 0


def a_checker_that_could_not_run_blocks_the_write(out: list[str]) -> int:
    """Check `consider` carries UNKNOWN through to a non-writable outcome.

    ⚑ THE STATE MUST SURVIVE THE WHOLE PATH, not just `_verdict`. The recorded failure mode is 67
    files written on the strength of a check that never ran, and that requires the collapse to
    happen anywhere between the report and `writable`.
    """
    with _Installed(_Stub(_BROKEN)), _Planted(_RECORD, ".record-migrate-case.py") as path:
        outcome = record_migrate.consider(path)
        if outcome.verdict != record_migrate.UNKNOWN:
            out.append(f"selftest: an unrunnable checker yielded {outcome.verdict!r}")
            return 1
        if outcome.writable:
            out.append("selftest: an UNKNOWN outcome would have been written")
            return 1
    return 0


def an_unimportable_checker_reads_as_unknown(out: list[str]) -> int:
    """Check a module without `run_checks` is reported COULD NOT RUN, not silently clean.

    ⚑⚑ AN EMPTY REPORT FROM A MISSING CHECKER RENDERS AS CLEAN, which is why `_check` synthesises
    the `COULD NOT RUN` text rather than returning `""`. This arm installs a module that loads fine
    and simply has no `run_checks` — the exact shape `_check` guards with `hasattr`.
    """
    with _Installed(types.ModuleType("pycheck_show")):
        report = record_migrate._check(_PLAIN)  # noqa: SLF001 — the unit under test
        if record_migrate.COULD_NOT_RUN not in report:
            out.append(f"selftest: a checker with no run_checks reported {report!r}")
            return 1
        if record_migrate._verdict(report) != record_migrate.UNKNOWN:  # noqa: SLF001 — under test
            out.append("selftest: the synthesised report did not read as UNKNOWN")
            return 1
    return 0


def the_staged_file_is_checked_inside_the_project(out: list[str]) -> int:
    """Check the target handed to the checker sits under `corpus.ROOT` — THE PATH-KEYED ARM.

    ⚑⚑⚑ RUFF AND MYPY DISCOVER CONFIGURATION BY WALKING UPWARD. A staged file outside the tree is
    checked under different rules than the file it stands for, so a CLEAN verdict there would be
    *a checker that agrees with you* rather than the gate's answer. The stub records what it was
    asked about, so this asserts the actual argument rather than re-reading the constant.
    """
    stub = _Stub("")
    with _Installed(stub):
        record_migrate._check(_PLAIN)  # noqa: SLF001 — the unit under test
    if not stub.seen:
        out.append("selftest: the checker was never called")
        return 1
    target = stub.seen[0]
    if target.parent != corpus.ROOT:
        out.append(
            f"selftest: the staged file was checked at {target} — outside the project, "
            f"where tool configuration resolves differently"
        )
        return 1
    # ⚑ THE NAME IS PER-PROCESS NOW, so it is asked of `staging_path()` rather than compared to
    # the stem — a suite that pinned the bare stem would go red the moment the PID was added,
    # which is the tracker-outlives-its-transition shape.
    if target != record_migrate.staging_path():
        out.append(f"selftest: the staged file was named {target.name!r}")
        return 1
    return 0


def the_staging_file_does_not_survive_the_check(out: list[str]) -> int:
    """Check the staged file is removed once the verdict is in.

    ⚑ A STAGING FILE LEFT IN THE TREE IS A CANDIDATE FOR THE NEXT WALK and an untracked file for
    the gate. `_check` removes it in a `finally`, so it goes even when the checker raises.
    """
    with _Installed(_Stub("")):
        record_migrate._check(_PLAIN)  # noqa: SLF001 — the unit under test
    # ⚑ ASKED OF `staging_path()`, NOT THE STEM. Checking `ROOT / STAGING` would pass VACUOUSLY
    # now that nothing writes there — an arm green for the wrong reason.
    if record_migrate.staging_path().exists():
        out.append("selftest: the staging file outlived the check")
        return 1
    return 0


def the_written_text_is_the_checked_text(out: list[str]) -> int:
    """Check a CLEAN outcome carries the FIXED source, not the raw transform output.

    ⚑⚑⚑ THE VERDICT WOULD OTHERWISE BE ABOUT A DIFFERENT DOCUMENT. `_check` hands the staged copy
    to `ruff --fix` and verifies the RESULT; writing the unfixed transform output would commit a
    file no checker ever saw. `_fixed` re-reads the staged file rather than reconstructing it,
    which is what makes the bytes that passed the bytes that land.

    ⚑⚑ ASSERTED AS AN IDENTITY AGAINST `_fixed`, NOT AS A GUESS AT WHAT RUFF DOES. This arm does
    not claim to know which fixes apply — it claims the outcome's source is exactly what the fixer
    leaves, which is the property that fails if a re-serialization creeps between check and write.
    """
    with _Installed(_Stub("")), _Planted(_RECORD, ".record-migrate-case.py") as path:
        outcome = record_migrate.consider(path)
        if outcome.verdict != record_migrate.CLEAN:
            out.append(f"selftest: the fixture did not reach CLEAN ({outcome.verdict})")
            return 1
        raw, _records, _flags = record_migrate._transformed(_RECORD)  # noqa: SLF001 — under test
        if outcome.source != record_migrate._fixed(raw):  # noqa: SLF001 — the unit under test
            out.append(
                "selftest: a CLEAN outcome's source is not what the fixer left — "
                "the checked text and the written text have diverged"
            )
            return 1
    return 0


def a_rejected_outcome_keeps_the_unfixed_source(out: list[str]) -> int:
    """Check a non-CLEAN outcome does not pay for a second fix pass it will never use.

    ⚑ `consider` CALLS `_fixed` ONLY ON THE CLEAN BRANCH. The source of a rejected outcome is the
    raw transform output — it is never written, and reporting is all it is for.
    """
    with _Installed(_Stub(_FINDING)), _Planted(_RECORD, ".record-migrate-case.py") as path:
        outcome = record_migrate.consider(path)
        raw, _records, _flags = record_migrate._transformed(_RECORD)  # noqa: SLF001 — under test
        if outcome.source != raw:
            out.append("selftest: a rejected outcome did not carry the raw transform output")
            return 1
    return 0


def a_recordless_file_is_unchanged_and_never_checked(out: list[str]) -> int:
    """Check a module with no record short-circuits before the checker is invoked.

    ⚑⚑ UNCHANGED IS A FOURTH VERDICT, and it must not be spelled CLEAN — CLEAN authorises a write.
    The checker not being called is the observable that separates the two: a file needing nothing
    should cost nothing.
    """
    stub = _Stub("")
    with _Installed(stub), _Planted(_PLAIN, ".record-migrate-case.py") as path:
        outcome = record_migrate.consider(path)
        if outcome.verdict != record_migrate.UNCHANGED:
            out.append(f"selftest: a recordless file read as {outcome.verdict!r}")
            return 1
        if outcome.writable:
            out.append("selftest: an UNCHANGED outcome reported itself writable")
            return 1
        if stub.seen:
            out.append("selftest: the checker ran on a file needing no conversion")
            return 1
    return 0


def a_file_argument_is_a_file_not_an_empty_directory(out: list[str]) -> int:
    """Check `candidates` on a single file returns it — THE MEASURED FALSE GREEN.

    ⚑⚑⚑ `rglob` ON A NON-DIRECTORY YIELDS NOTHING, so naming one file reported `0 clean · 0 with
    findings` against a file that demonstrably holds a `NamedTuple` — **the orchestrator built to
    refuse false greens produced one.** A caller cannot distinguish an unsupported argument SHAPE
    from an empty population, so the shape is handled rather than assumed.
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "holds_a_record.py"
        path.write_text(_RECORD, encoding="utf-8")
        found = record_migrate.candidates(path)
        if found != (path,):
            out.append(f"selftest: naming one file yielded {found!r} — the silent zero")
            return 1
    return 0


def a_directory_yields_only_the_files_holding_a_record(out: list[str]) -> int:
    """Check `candidates` walks a directory and discriminates by content.

    ⚑ THE F ARM FOR THE WALK. A `candidates` returning every `.py` file would pass the arm above,
    and would put the whole tree through the checker.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "holds_a_record.py").write_text(_RECORD, encoding="utf-8")
        (root / "holds_none.py").write_text(_PLAIN, encoding="utf-8")
        (root / "not_python.txt").write_text(_RECORD, encoding="utf-8")
        found = record_migrate.candidates(root)
        if found != (root / "holds_a_record.py",):
            out.append(f"selftest: the walk selected {[p.name for p in found]}")
            return 1
    return 0


def the_residue_flags_are_carried_not_fixed(out: list[str]) -> int:
    """Check a flagged site is reported on the outcome rather than silently rewritten.

    ⚑ THE RESIDUE IS A WORK LIST. A keyless comparison compared by FIELD POSITION under
    `NamedTuple`; only a human can say what the order MEANT, so the tool flags and never repairs.
    """
    keyless = _RECORD + "\nROWS = sorted(items)\n"
    with _Installed(_Stub("")), _Planted(keyless, ".record-migrate-case.py") as path:
        outcome = record_migrate.consider(path)
        if not any("keyless" in flag for flag in outcome.flags):
            out.append(f"selftest: the keyless comparison was not flagged: {outcome.flags!r}")
            return 1
        if "sorted(items)" not in outcome.source:
            out.append("selftest: the flagged site was rewritten rather than reported")
            return 1
    return 0


def duplicate_flags_are_reported_once(out: list[str]) -> int:
    """Check `_unique` drops repeats and keeps first-occurrence order."""
    got = record_migrate._unique(["b", "a", "b", "c", "a"])  # noqa: SLF001 — the unit under test
    if got != ("b", "a", "c"):
        out.append(f"selftest: `_unique` returned {got!r}")
        return 1
    return 0


def the_residue_census_is_grouped_by_kind(out: list[str]) -> int:
    """Check `_kind` separates the two classes, and the census groups by them.

    ⚑ BY KIND, NOT BY SITE. Sixty-odd flags listed individually is the 29.6 KB dump `--summary`
    exists to replace; `N sites across M files` is what a reader weighs a batch by.
    """
    if record_migrate._kind("keyless sorted() at x") != "keyless comparison":  # noqa: SLF001
        out.append("selftest: a keyless flag was not classed as a comparison")
        return 1
    if record_migrate._kind("pair[0] identifies") != "numeric subscript":  # noqa: SLF001
        out.append("selftest: a subscript flag was not classed as a subscript")
        return 1
    outcomes = (
        record_migrate.Outcome(
            relpath="a.py",
            verdict=record_migrate.CLEAN,
            records=("R",),
            flags=("keyless sorted() at a", "pair[0] at a"),
            report="",
            source="",
        ),
        record_migrate.Outcome(
            relpath="b.py",
            verdict=record_migrate.CLEAN,
            records=("R",),
            flags=("keyless min() at b",),
            report="",
            source="",
        ),
    )
    lines = "\n".join(record_migrate._census(outcomes))  # noqa: SLF001 — the unit under test
    if "keyless comparison" not in lines or "numeric subscript" not in lines:
        out.append(f"selftest: the census omits a kind: {lines!r}")
        return 1
    if "2 site(s) across 2 file(s)" not in lines:
        out.append(f"selftest: the comparison kind was not counted across both files: {lines!r}")
        return 1
    return 0


def an_unknown_is_never_folded_into_the_totals(out: list[str]) -> int:
    """Check `_summary` keeps each verdict distinct and names what UNKNOWN means.

    ⚑⚑ THE SUMMARY IS WHERE A COLLAPSE WOULD LAND LAST AND READ WORST. A reader authorising a
    batch reads this line; `1 clean` covering an UNKNOWN would be the false green at the point of
    decision, so the counts are separate and the caveat is spelled out.
    """
    outcomes = (
        record_migrate.Outcome(
            relpath="a.py",
            verdict=record_migrate.CLEAN,
            records=("R",),
            flags=(),
            report="",
            source="",
        ),
        record_migrate.Outcome(
            relpath="b.py",
            verdict=record_migrate.UNKNOWN,
            records=("R",),
            flags=(),
            report="",
            source="",
        ),
        record_migrate.Outcome(
            relpath="c.py",
            verdict=record_migrate.FINDINGS,
            records=("R",),
            flags=(),
            report="",
            source="",
        ),
    )
    lines = "\n".join(record_migrate._summary(outcomes, applied=None))  # noqa: SLF001 — under test
    if "1 clean" not in lines or "1 with findings" not in lines or "1 UNKNOWN" not in lines:
        out.append(f"selftest: the totals collapsed a verdict: {lines!r}")
        return 1
    if "never a clean bill" not in lines:
        out.append("selftest: an UNKNOWN was counted without saying what it means")
        return 1
    if "nothing written" not in lines:
        out.append("selftest: a dry run did not say nothing was written")
        return 1
    return 0


def intent_is_stated_never_defaulted(out: list[str]) -> int:
    """Check `main` refuses to act without `--apply` or `--dry-run` — the house contract.

    ⚑⚑ NEITHER DEFAULT IS SAFE. A default-dry silently does nothing when you meant to write; a
    default-apply writes when you meant to look. So an unstated intent is exit 2, not a guess.
    """
    if record_migrate.main(["substrate/"]) != _TWO:
        out.append("selftest: an unstated intent did not refuse with exit 2")
        return 1
    if record_migrate.main(["--dry-run"]) != _TWO:
        out.append("selftest: a stated intent with no root did not refuse with exit 2")
        return 1
    return 0


def only_the_clean_members_of_a_batch_are_written(out: list[str]) -> int:
    """Check `--apply` writes exactly the CLEAN files of a mixed batch — THE LOOP ARM.

    ⚑⚑⚑ THE PREDICATE IS NOT THE GATE. `only_clean_is_writable` pins that `Outcome.writable` is
    true of CLEAN alone; nothing pinned that `main`'s write loop CONSULTS it. A loop that computed
    the verdicts correctly and then wrote every outcome — or wrote the wrong subset — would pass
    every other arm in this file. That is the report-versus-gate collapse, and it is why this arm
    exists.

    ⚑⚑ OBSERVED ON THE FILES, NEVER ON THE PREDICATE. Re-reading `outcome.writable` here would
    assert the loop's own input back at itself and could not fail. So the batch is planted, the
    real loop is turned loose on it, and the BYTES are read back: the clean member must have
    changed and the flagged member must be byte-identical to what was planted.

    ⚑ THE POPULATION IS THE ARM'S OWN. Both members live in a dot-prefixed directory this arm
    creates and destroys, so the write loop cannot reach a file anything else owns.
    """
    members = {"clean_member.py": _RECORD, "flagged_member.py": _MARKED}
    with _Installed(_Stub(_FINDING, flag_marker="Marked")), _PlantedTree(members) as root:
        if record_migrate.main(["--apply", str(root)]):
            out.append("selftest: a mixed apply did not exit 0")
            return 1
        clean_landed = (root / "clean_member.py").read_text(encoding="utf-8")
        flagged_landed = (root / "flagged_member.py").read_text(encoding="utf-8")
        if clean_landed == _RECORD:
            out.append(
                "selftest: --apply left the CLEAN member unwritten — the loop wrote "
                "nothing, which every predicate arm would have reported as fine"
            )
            return 1
        if "NamedTuple" in clean_landed:
            out.append("selftest: the CLEAN member was rewritten but still declares a NamedTuple")
            return 1
        if flagged_landed != _MARKED:
            out.append(
                "selftest: --apply wrote a member the checker FLAGGED — the per-file gate "
                "reverts that file and the conversion is lost"
            )
            return 1
    return 0


def a_recordless_member_of_a_batch_is_left_alone(out: list[str]) -> int:
    """Check the loop writes no UNCHANGED member — the fourth verdict, at the write.

    ⚑⚑ UNCHANGED IS NOT CLEAN, AND THE DIFFERENCE ONLY SHOWS AT THE WRITE. A loop keyed on
    `verdict != FINDINGS` rather than `verdict == CLEAN` would rewrite every recordless file in the
    tree with its own unchanged text — invisible in the report, and a diff on every one of them.

    ⚑ A RECORDLESS FILE IS NOT EVEN A CANDIDATE, so this also pins that the walk's filter and the
    loop's filter agree. Asserted on bytes: the plain member must be byte-identical.
    """
    members = {"has_record.py": _RECORD, "no_record.py": _PLAIN}
    with _Installed(_Stub("")), _PlantedTree(members) as root:
        if record_migrate.main(["--apply", str(root)]):
            out.append("selftest: an apply over a mixed batch did not exit 0")
            return 1
        if (root / "no_record.py").read_text(encoding="utf-8") != _PLAIN:
            out.append("selftest: --apply rewrote a file holding no record at all")
            return 1
        if (root / "has_record.py").read_text(encoding="utf-8") == _RECORD:
            out.append("selftest: --apply skipped the one member it was supposed to convert")
            return 1
    return 0


def an_unknown_member_of_a_batch_is_never_written(out: list[str]) -> int:
    """Check the loop refuses UNKNOWN at the write, not merely in the report.

    ⚑⚑⚑ THE RECORDED FAILURE IS 67 FILES WRITTEN ON A CHECK THAT NEVER RAN. `_verdict` and
    `writable` both refuse UNKNOWN, and this arm pins that the refusal SURVIVES INTO THE LOOP:
    every member of a batch checked by a broken checker must come back byte-identical.

    ⚑ AND THE SUMMARY MUST SAY SO. A run that wrote nothing while reporting `WROTE 2` would leave
    the operator believing a batch landed, so the reported count is pinned at zero too.
    """
    members = {"one.py": _RECORD, "two.py": _MARKED}
    with _Installed(_Stub(_BROKEN)), _PlantedTree(members) as root:
        if record_migrate.main(["--apply", str(root)]):
            out.append("selftest: an UNKNOWN apply did not exit 0")
            return 1
        for filename, planted in members.items():
            if (root / filename).read_text(encoding="utf-8") != planted:
                out.append(f"selftest: --apply wrote {filename} on a check that never ran")
                return 1
    return 0


def a_dry_run_writes_nothing_at_all(out: list[str]) -> int:
    """Check `--dry-run` leaves every member byte-identical even when the batch is CLEAN.

    ⚑⚑⚑ DISTINCT FROM "WRITES THE EMPTY SET", AND THAT DISTINCTION IS THE ARM. A dry run over a
    batch whose verdicts are all FINDINGS writes nothing for a reason that has nothing to do with
    `--dry-run`, so it cannot witness the flag. The population here is entirely CLEAN — every
    member is one the apply loop WOULD write — and the assertion is that the original bytes
    survive. That is the only form in which the flag is observable.

    ⚑ THE ORIGINAL BYTES, NOT A COUNT. `--dry-run: nothing written` in the report is the tool's own
    claim about itself; the files are the fact.
    """
    members = {"first.py": _RECORD, "second.py": _MARKED}
    with _Installed(_Stub("")), _PlantedTree(members) as root:
        if record_migrate.main(["--dry-run", str(root)]):
            out.append("selftest: a clean dry run did not exit 0")
            return 1
        for filename, planted in members.items():
            if (root / filename).read_text(encoding="utf-8") != planted:
                out.append(f"selftest: --dry-run wrote to {filename} — the caller asked to LOOK")
                return 1
    return 0


def the_bytes_the_loop_writes_are_the_bytes_that_were_checked(out: list[str]) -> int:
    """Check the file the loop lands is exactly the outcome's checked source.

    ⚑⚑⚑ THE WRITE IS THE LAST PLACE THE TWO CAN DIVERGE. `the_written_text_is_the_checked_text`
    pins that a CLEAN `Outcome` CARRIES the fixed source; this pins that the loop puts THAT on
    disk. A loop that re-ran the transform, re-serialised, or wrote `outcome.report` instead would
    satisfy both the predicate arm and the carrier arm and still land a document no checker saw.

    ⚑⚑ THE COMPARISON IS AGAINST `consider`'S OWN ANSWER, RE-DERIVED HERE — not against a guess at
    what ruff does. This arm never claims to know which fixes apply; it claims the landed bytes and
    the checked bytes are the same string.
    """
    with _Installed(_Stub("")), _PlantedTree({"only.py": _RECORD}) as root:
        expected = record_migrate.consider(root / "only.py").source
        if record_migrate.main(["--apply", str(root)]):
            out.append("selftest: a clean apply did not exit 0")
            return 1
        landed = (root / "only.py").read_text(encoding="utf-8")
        if landed != expected:
            out.append(
                "selftest: the bytes on disk are not the bytes that were checked — "
                "the write re-derived the conversion instead of committing it"
            )
            return 1
    return 0


def a_batch_reports_what_it_wrote_and_what_it_refused(out: list[str]) -> int:
    """Check the run's OUTCOME is legible, since a batch exit code cannot carry it.

    ⚑⚑⚑ `main` RETURNS 0 FOR ANY COMPLETED BATCH, AND THAT IS THE HONEST CONTRACT HERE — not an
    omission to paper over with a vacuous assertion. A refused file among sixty is not a failed
    run; the sibling `module_trim` returns 1 on refusal because it converts exactly ONE module, so
    its exit code CAN name that module's verdict. Over a batch it cannot: `1` would be
    indistinguishable between one refusal and all of them, and would make a normal
    partly-clean sweep look like a crash.

    ⚑⚑ SO WHAT IS PINNED IS THAT THE INFORMATION IS SOMEWHERE. The refused count must be legible in
    the SUMMARY, beside the written count, and the two must not be collapsed — `1 clean` covering a
    refusal is the false green at the point of decision. This is the property the exit code cannot
    carry, asserted where it actually lives.
    """
    outcomes = (
        record_migrate.Outcome(
            relpath="a.py",
            verdict=record_migrate.CLEAN,
            records=("R",),
            flags=(),
            report="",
            source="",
        ),
        record_migrate.Outcome(
            relpath="b.py",
            verdict=record_migrate.FINDINGS,
            records=("R",),
            flags=(),
            report="",
            source="",
        ),
    )
    lines = "\n".join(record_migrate._summary(outcomes, applied=1))  # noqa: SLF001 — under test
    if "WROTE 1 file(s)" not in lines:
        out.append(f"selftest: an apply did not report how many files it wrote: {lines!r}")
        return 1
    if "only the clean ones" not in lines:
        out.append("selftest: the write count did not say which files it covered")
        return 1
    if "1 with findings" not in lines:
        out.append(f"selftest: the refused file vanished from the summary: {lines!r}")
        return 1
    return 0


def the_loop_leaves_no_staging_file_behind(out: list[str]) -> int:
    """Check a full `--apply` sweep leaves no artefact of its own in the tree.

    ⚑⚑ THE STAGING FILE IS WRITTEN ONCE PER CANDIDATE, AND `_fixed` WRITES IT A SECOND TIME on the
    CLEAN branch. `the_staging_file_does_not_survive_the_check` pins one `_check`; this pins the
    whole loop, across a batch that exercises both branches. A survivor is a candidate for the next
    walk and an untracked file for the commit gate.
    """
    members = {"a.py": _RECORD, "b.py": _MARKED}
    with _Installed(_Stub(_FINDING, flag_marker="Marked")), _PlantedTree(members) as root:
        record_migrate.main(["--apply", str(root)])
    if record_migrate.staging_path().exists():
        out.append("selftest: the staging file outlived a full apply sweep")
        return 1
    return 0


def a_summary_line_is_produced_per_changed_file(out: list[str]) -> int:
    """Check `--summary` renders one line per changed file and drops the unchanged.

    ⚑ `--summary` IS A READING MODE, NOT A SHORTER ONE. The full form over 67 files is 29.6 KB —
    a tool with only the full form cannot report its own census.
    """
    outcomes = (
        record_migrate.Outcome(
            relpath="a.py",
            verdict=record_migrate.CLEAN,
            records=("R",),
            flags=(),
            report="",
            source="",
        ),
        record_migrate.Outcome(
            relpath="b.py",
            verdict=record_migrate.UNCHANGED,
            records=(),
            flags=(),
            report="",
            source="",
        ),
    )
    brief = record_migrate._report(outcomes, brief=True)  # noqa: SLF001 — the unit under test
    if len(brief) != 1:
        out.append(f"selftest: the brief report emitted {len(brief)} line(s) for one changed file")
        return 1
    if "a.py" not in brief[0] or "b.py" in brief[0]:
        out.append(f"selftest: the brief line names the wrong file: {brief[0]!r}")
        return 1
    if record_migrate._render(outcomes[1]):  # noqa: SLF001 — the unit under test
        out.append("selftest: an UNCHANGED file was rendered in the full report")
        return 1
    return 0


def one_bad_file_cannot_bury_the_summary(out: list[str]) -> int:
    """Check a long checker report is truncated in the full render.

    ⚑ THE CAP EXISTS SO THE TOTALS STAY REACHABLE. A file whose report runs hundreds of lines would
    otherwise push the summary past anything a reader scrolls to.
    """
    long_report = "\n".join(f"line {n}" for n in range(200))
    outcome = record_migrate.Outcome(
        relpath="a.py",
        verdict=record_migrate.FINDINGS,
        records=("R",),
        flags=(),
        report=long_report,
        source="",
    )
    rendered = record_migrate._render(outcome)  # noqa: SLF001 — the unit under test
    if len(rendered) > record_migrate.REPORT_LINES + 1:
        out.append(
            f"selftest: {len(rendered)} line(s) rendered for one file — the cap is "
            f"{record_migrate.REPORT_LINES}"
        )
        return 1
    return 0


def every_record_in_a_file_reaches_the_outcome(out: list[str]) -> int:
    """Check `_transformed` reports each converted record, not one per file."""
    two = _RECORD + '\n\nclass Second(NamedTuple):\n    """Another."""\n\n    other: int\n'
    _code, records, _flags = record_migrate._transformed(two)  # noqa: SLF001 — under test
    if len(records) != _TWO:
        out.append(f"selftest: `_transformed` reported {records!r}")
        return 1
    return 0


def an_outcome_is_frozen_and_slotted(out: list[str]) -> int:
    """Check `Outcome` is the immutable record this tree converted toward.

    ⚑ THE ORCHESTRATOR'S OWN RECORD MUST HOLD THE SHAPE IT IMPOSES. A mutable outcome would let a
    verdict be edited between the check and the write, which is the one window this tool closes.
    """
    outcome = record_migrate.Outcome(
        relpath="a.py", verdict=record_migrate.FINDINGS, records=(), flags=(), report="", source=""
    )
    try:
        outcome.verdict = record_migrate.CLEAN  # type: ignore[misc]
    except (AttributeError, TypeError):
        pass
    else:
        out.append("selftest: a verdict could be reassigned after the check")
        return 1
    if hasattr(outcome, "__dict__"):
        out.append("selftest: `Outcome` carries a __dict__ — it is not slotted")
        return 1
    return 0


_ARMS = (
    a_findings_report_is_not_clean,
    an_empty_report_is_clean,
    a_checker_that_could_not_run_is_unknown_not_clean,
    only_clean_is_writable,
    a_file_with_findings_is_not_written,
    a_checker_that_could_not_run_blocks_the_write,
    an_unimportable_checker_reads_as_unknown,
    the_staged_file_is_checked_inside_the_project,
    the_staging_file_does_not_survive_the_check,
    the_written_text_is_the_checked_text,
    a_rejected_outcome_keeps_the_unfixed_source,
    a_recordless_file_is_unchanged_and_never_checked,
    a_file_argument_is_a_file_not_an_empty_directory,
    a_directory_yields_only_the_files_holding_a_record,
    the_residue_flags_are_carried_not_fixed,
    duplicate_flags_are_reported_once,
    the_residue_census_is_grouped_by_kind,
    an_unknown_is_never_folded_into_the_totals,
    intent_is_stated_never_defaulted,
    only_the_clean_members_of_a_batch_are_written,
    a_recordless_member_of_a_batch_is_left_alone,
    an_unknown_member_of_a_batch_is_never_written,
    a_dry_run_writes_nothing_at_all,
    the_bytes_the_loop_writes_are_the_bytes_that_were_checked,
    a_batch_reports_what_it_wrote_and_what_it_refused,
    the_loop_leaves_no_staging_file_behind,
    a_summary_line_is_produced_per_changed_file,
    one_bad_file_cannot_bury_the_summary,
    every_record_in_a_file_reaches_the_outcome,
    an_outcome_is_frozen_and_slotted,
)

_CASE_COUNT = (
    1
    + 2
    + 2
    + 4
    + 3
    + 2
    + 2
    + 3
    + 1
    + 2
    + 1
    + 3
    + 1
    + 1
    + 2
    + 1
    + 4
    + 4
    + 2
    + 4
    + 3
    + 3
    + 2
    + 2
    + 3
    + 1
    + 3
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
        sys.stderr.write(f"record-migrate selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"record-migrate selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
