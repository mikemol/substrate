#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Apply the record transform across a tree — checking each prospective output BEFORE writing it.

⚑⚑⚑ THE CHECK ON THE PROSPECTIVE OUTPUT IS THIS TOOL'S CONTRACT, NOT A SAFEGUARD BOLTED ON. The
per-file gate refuses a file carrying any finding and REVERTS it, so a rewriter that writes and
hopes turns N files into N chances to lose one. Measured by hand first: six attempts across three
files were lost exactly that way, each costing a full re-derivation. So nothing is written until
it has passed the same ruff+mypy the gate runs, and a file that would land dirty is REPORTED.

⚑⚑ IT IS `split_lemmas`' CONSERVATION GUARD ONE LANGUAGE OVER. That splitter refuses to write
unless every non-blank body line lands in exactly one unit, and it has caught seven distinct
silent-deletion bugs. A mechanical rewriter's characteristic output is PLAUSIBLE AND WRONG, which
is precisely what a verification step before the write is for.

⚑⚑⚑ AND IT CAUGHT FOUR OF THE TRANSFORM'S OWN BUGS, EVERY ONE A CORRECT CONVERSION THAT COULD NOT
LAND: `NamedTuple` left in the `typing` import (`F401`), then three successive `I001` placements of
the added import. ⚑ The last three were one bug — the transform was reimplementing isort, badly,
while the real sorter ran in the next step — which is why `_autofix` now hands the staged file to
`ruff --fix` before checking it. None of the four ever reached disk.

⚑⚑ THE CHECKER MUST BE THE HOUSE ONE, INVOKED THE HOUSE WAY. `pycheck_show.run_checks` passes the
config EXPLICITLY and puts its target inside the project, because ruff and mypy DISCOVER
configuration by walking upward — a temp file in `/tmp` is checked under different rules than the
file it stands for, and a checker that finds its own config is *"a checker that agrees with you"*.
Re-deriving that argv here would inherit exactly the omissions `run_checks`' own docstring records
making. So it is CALLED, never reimplemented.

⚑⚑ THREE STATES, NOT TWO, AND THE THIRD MUST SURVIVE. ruff and mypy use exit 1 for "flagged
something" and exit 2 for "could not run"; `run_checks` renders the second as `⚑ COULD NOT RUN`.
This tool carries it as UNKNOWN, never as clean. ⚑ A CHECKER THAT WOULD NOT LOAD IS THE SAME
STATE: if `pycheck_show` cannot be imported then nothing was verified, and returning an empty
report would render that as CLEAN — writing 67 files on the strength of a check that never ran.

⚑ THE RESIDUE IS A WORK LIST, NOT A SILENT FIX. Two classes are flagged and never rewritten: a
keyless `sorted`/`min`/`max` (which under `NamedTuple` compared by FIELD POSITION) and an integer
subscript identifying something. Both need a human to say what the order or the position MEANS.
Every flag is a find — a place where meaning was carried by position.

    record_migrate.py --dry-run substrate/     # what would change, and what still needs a human
    record_migrate.py --apply substrate/       # write only the files that pass the gate clean
"""

from __future__ import annotations

import contextlib
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, cast

import libcst as cst
from libcst.codemod import CodemodContext

from substrate import corpus, gate_module, record_transform

# What a prospective file is called while it is being checked. ⚑ INSIDE THE PROJECT — see note.
#
# ⚑⚑ THIS IS A STEM, NOT THE PATH — `staging_path()` is. Two suites share this pipeline
# (`record_migrate_selftest`, `module_trim_selftest`) and `run_selftests` runs them in a pool, so
# with ONE fixed name each process's `unlink` landed between another's `write_text` and
# `read_text`: `module_trim_selftest` read UNREAD on `FileNotFoundError: .record-migrate-staging.py`
# while running clean on its own (gate-G387). The gate-F60 fixture-shares-a-path class, with a
# second PARTY rather than a second run. The PID makes the name per-process; the stem stays so a
# suite can still name what it expects to find nothing of afterward.
STAGING = ".record-migrate-staging.py"

# How long ruff's fix pass may take on one staged file.
FIX_TIMEOUT_S = 60

# The verdicts a prospective conversion can carry.
CLEAN = "CLEAN"
FINDINGS = "FINDINGS"
UNKNOWN = "UNKNOWN"
UNCHANGED = "UNCHANGED"

# What `run_checks` prints when the checker itself could not run.
COULD_NOT_RUN = "COULD NOT RUN"

# How many report lines to echo per file, so one bad file cannot bury the summary.
REPORT_LINES = 12


class Checker(Protocol):
    """The one function this tool needs of `pycheck_show`.

    ⚑ A PROTOCOL PLUS `cast`, WHICH IS THE HOUSE PATTERN for a module loaded by path
    (`tool_population.routed_names` does the same for the routing hook). A `ModuleType`'s
    attributes are `Any` by construction, so declaring the SURFACE is what stops the `Any`
    reaching every caller — and structural typing means `pycheck_show` declares nothing.

    ⚑⚑ THE DECLARED SURFACE MUST MOVE WITH THE REAL ONE. `run_checks` gained an optional
    `stands_for` so a prospective file is checked under the identity it stands for rather than its
    staging name (gate-G334); a Protocol still declaring the one-argument form would type-check
    green and refuse the second argument at the seam.
    """

    def run_checks(self, target: Path, stands_for: Path | None = None) -> str:
        """Return ruff's and mypy's findings for `target`, empty when clean."""
        ...


@dataclass(frozen=True, slots=True)
class Outcome:
    """One file's prospective conversion: what it would become, and whether it may be written."""

    relpath: str
    verdict: str
    records: tuple[str, ...]
    flags: tuple[str, ...]
    report: str
    source: str

    @property
    def writable(self) -> bool:
        """Report whether this conversion may be committed to disk.

        ⚑ ONLY `CLEAN` IS WRITABLE, AND `UNKNOWN` EXPLICITLY IS NOT. A checker that could not run
        has established nothing, and writing on the strength of that would bank an unmeasured
        claim — the same reason `tool_decline_run` fails on UNCHECKED rather than passing.
        """
        return self.verdict == CLEAN


def _unique(flags: list[str]) -> tuple[str, ...]:
    """Return `flags` with duplicates dropped, first occurrence kept."""
    seen: list[str] = []
    for flag in flags:
        if flag not in seen:
            seen.append(flag)
    return tuple(seen)


def _transformed(source: str) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    """Return `(new_source, converted_records, flags)` for one file's text."""
    command = record_transform.SlottedRecords(CodemodContext())
    updated = cst.parse_module(source).visit(command)
    return (updated.code, tuple(command.converted), _unique(command.flags))


def _autofix(target: Path) -> None:
    """Apply ruff's own safe fixes to the staged file before it is checked.

    ⚑⚑⚑ THE SORTER DECIDES WHERE THE IMPORT GOES, NOT THE TRANSFORM. `record_transform` used to
    insert the dataclass import at a computed position, and three successive `I001` failures each
    provoked one more placement clause — an isort reimplementation growing inside a codemod, while
    the real sorter ran in the very next step. Handing the file to `ruff --fix` first removes the
    whole bug class instead of its next instance.

    ⚑⚑ ONLY THE SAFE FIXES. `--fix` without `--unsafe-fixes` applies transformations ruff
    guarantees preserve behaviour, so a formatting repair cannot quietly become a semantic one —
    which matters because whatever this produces is what gets written to the tree.

    ⚑ A FAILURE HERE IS DELIBERATELY SILENT, AND ONLY BECAUSE THE CHECK STILL RUNS AFTERWARDS. If
    ruff cannot fix the file, `run_checks` reports whatever remains and the verdict is FINDINGS or
    UNKNOWN — never CLEAN. This is an OPTIMISATION of the transform's output, not a step whose
    success anything is inferred from.
    """
    argv = [
        str(corpus.ROOT / ".venv" / "bin" / "python3"),
        "-m",
        "ruff",
        "check",
        "--config",
        str(corpus.ROOT / "pyproject.toml"),
        "--no-cache",
        "--fix",
        "--quiet",
        str(target),
    ]
    with contextlib.suppress(OSError, subprocess.SubprocessError):
        subprocess.run(
            argv,
            capture_output=True,
            check=False,  # noqa: S603 — argv is built here
            timeout=FIX_TIMEOUT_S,
        )


def _check(source: str, stands_for: Path | None = None) -> str:
    """Return the house checker's report for prospective `source`, empty when clean.

    ⚑ THE STAGING FILE LIVES INSIDE THE PROJECT. ruff and mypy walk upward to find configuration,
    so a file checked outside the tree is checked under different rules than the one it stands for
    — which would make this verification agree with itself rather than with the gate.

    ⚑⚑⚑ AND `stands_for` CARRIES THE OTHER HALF OF THAT, WHICH THE STAGING NAME LOST. Config
    DISCOVERY is satisfied anywhere in the tree; a `per-file-ignores` entry is keyed on the EXACT
    path, and `.record-migrate-staging.py` matches none of them. Measured: `substrate/type_scope.py`
    is CLEAN on disk because `pyproject` exempts `S603` for that path, and its staged form reported
    `S603` — a finding the real file cannot carry (gate-G334). Naming the path the bytes stand for
    is what closes it; `run_checks` routes it to ruff's `--stdin-filename` and mypy's
    `--shadow-file`.

    ⚑⚑ AND A CHECKER THAT WOULD NOT LOAD RETURNS `COULD NOT RUN`, NOT `""`. An unimportable
    verifier means nothing was verified, and an empty report renders as CLEAN.
    """
    module, why = gate_module.gate_module("pycheck_show.py")
    if module is None or not hasattr(module, "run_checks"):
        return f"--- pycheck_show ---\n⚑ {COULD_NOT_RUN}: {why or 'no run_checks'}"
    checker = cast("Checker", module)
    staging = staging_path()
    staging.write_text(source, encoding="utf-8")
    try:
        _autofix(staging)
        return checker.run_checks(staging, stands_for)
    finally:
        staging.unlink(missing_ok=True)


def staging_path() -> Path:
    """Return THIS process's staging file — inside the project, and no other process's.

    ⚑ THE PID IS THE DISCRIMINATOR, not a random suffix: a suite asserting that nothing survives
    a run can compute the same name and look for it, where a random name would leave it guessing.
    """
    import os  # noqa: PLC0415 — one function needs it, nothing else in this module does

    stem, dot, ext = STAGING.rpartition(".")
    return corpus.ROOT / f"{stem}-{os.getpid()}{dot}{ext}"


def _fixed(source: str) -> str:
    """Return `source` as ruff's fixer leaves it — what the verdict was actually about.

    ⚑⚑ THE WRITTEN TEXT MUST BE THE CHECKED TEXT. `_check` fixes a staged copy and then verifies
    it; writing the UNFIXED transform output instead would commit a file no checker ever saw, and
    a CLEAN verdict would be about a different document. So the fixed text is read back from
    staging rather than reconstructed.
    """
    staging = staging_path()
    staging.write_text(source, encoding="utf-8")
    try:
        _autofix(staging)
        return staging.read_text(encoding="utf-8")
    finally:
        staging.unlink(missing_ok=True)


def _verdict(report: str) -> str:
    """Return CLEAN, FINDINGS or UNKNOWN for a checker report.

    ⚑ `COULD NOT RUN` IS ITS OWN VERDICT. Collapsing it into FINDINGS would understate it — a
    broken invocation is not a lint result — and collapsing it into CLEAN would be the false green
    this tool exists to avoid.
    """
    if COULD_NOT_RUN in report:
        return UNKNOWN
    return FINDINGS if report.strip() else CLEAN


def consider(path: Path) -> Outcome:
    """Return what converting `path` would produce, without writing anything."""
    relpath = str(path.relative_to(corpus.ROOT))
    source = path.read_text(encoding="utf-8")
    new_source, records, flags = _transformed(source)
    if not records or new_source == source:
        return Outcome(
            relpath=relpath,
            verdict=UNCHANGED,
            records=records,
            flags=flags,
            report="",
            source=source,
        )
    report = _check(new_source)
    verdict = _verdict(report)
    written = _fixed(new_source) if verdict == CLEAN else new_source
    return Outcome(
        relpath=relpath,
        verdict=verdict,
        records=records,
        flags=flags,
        report=report,
        source=written,
    )


def candidates(root: Path) -> tuple[Path, ...]:
    """Return every file at or under `root` that declares a `NamedTuple` record.

    ⚑⚑ A FILE ARGUMENT IS A FILE, NOT AN EMPTY DIRECTORY. `rglob` on a path that is not a
    directory yields NOTHING, so naming one file reported `0 clean · 0 with findings` — a silent
    zero that reads exactly like "nothing to convert". MEASURED on this tool's first run, against
    a file that demonstrably holds a `NamedTuple`: **the orchestrator built to refuse false greens
    produced one.** A caller cannot distinguish an unsupported argument SHAPE from an empty
    population, so the shape is handled rather than assumed.
    """
    found = [root] if root.is_file() else sorted(root.rglob("*.py"))
    return tuple(
        path
        for path in found
        if path.suffix == ".py" and "NamedTuple" in path.read_text(encoding="utf-8")
    )


def _kind(flag: str) -> str:
    """Return which CLASS of residue a flag belongs to.

    ⚑ THE CENSUS IS BY KIND, NOT BY SITE. Sixty-odd flags listed individually is the 29.6 KB dump
    this mode exists to replace; `N keyless comparisons across M files` is the number a reader
    weighs a batch by, and the sites remain available per file.
    """
    return "keyless comparison" if flag.startswith("keyless") else "numeric subscript"


def _summarised(outcome: Outcome) -> str:
    """Return one file's outcome as a single line."""
    return (
        f"{outcome.verdict:<9} {outcome.relpath:<44} "
        f"{len(outcome.records)} record(s), {len(outcome.flags)} flag(s)"
    )


def _census(outcomes: tuple[Outcome, ...]) -> list[str]:
    """Return the residue grouped by KIND, with the files each kind touches."""
    by_kind: dict[str, list[str]] = {}
    for outcome in outcomes:
        for flag in outcome.flags:
            by_kind.setdefault(_kind(flag), []).append(outcome.relpath)
    if not by_kind:
        return []
    out = ["\n── RESIDUE, by kind (every one is a place meaning was carried by POSITION)"]
    for kind in sorted(by_kind):
        files = sorted(set(by_kind[kind]))
        out.append(f"   {kind:<20} {len(by_kind[kind])} site(s) across {len(files)} file(s)")
        out.extend(f"      {relpath}" for relpath in files)
    return out


def _report(outcomes: tuple[Outcome, ...], *, brief: bool) -> list[str]:
    """Return the per-file report, one line each when brief and in full otherwise.

    ⚑ `--summary` IS A READING MODE, NOT A SHORTER ONE. The full form prints every file's checker
    report, which over 67 files is 29.6 KB — unreadable without the shell composition the
    structural hook correctly refuses, so a tool with only the full form CANNOT REPORT ITS OWN
    CENSUS. One line per file plus the residue grouped by KIND is what a reader weighs a batch by
    before authorising it.
    """
    if not brief:
        return [line for outcome in outcomes for line in _render(outcome)]
    changed = tuple(o for o in outcomes if o.verdict != UNCHANGED)
    return [*[_summarised(o) for o in changed], *_census(changed)]


def _render(outcome: Outcome) -> list[str]:
    """Render one file's outcome, with its flags and any findings."""
    if outcome.verdict == UNCHANGED:
        return []
    header = (
        f"\n{outcome.verdict:<9} {outcome.relpath}  "
        f"({len(outcome.records)} record(s): {', '.join(outcome.records)})"
    )
    out = [header]
    out.extend(f"   ⚑ {flag}" for flag in outcome.flags)
    if outcome.report.strip():
        out.extend(f"     {line}" for line in outcome.report.splitlines()[:REPORT_LINES])
    return out


def _summary(outcomes: tuple[Outcome, ...], *, applied: int | None) -> list[str]:
    """Render the totals, keeping each verdict distinct."""
    counted = {
        verdict: sum(1 for o in outcomes if o.verdict == verdict)
        for verdict in (CLEAN, FINDINGS, UNKNOWN)
    }
    flags = sum(len(o.flags) for o in outcomes if o.verdict != UNCHANGED)
    totals = (
        f"\n{counted[CLEAN]} clean · {counted[FINDINGS]} with findings · "
        f"{counted[UNKNOWN]} UNKNOWN · {flags} site(s) needing a human"
    )
    out = [totals]
    if counted[UNKNOWN]:
        out.append(
            "   ⚑ UNKNOWN means the CHECKER could not run — a fact about this "
            "environment, never a clean bill."
        )
    if flags:
        out.append("   ⚑ EVERY FLAG IS A FIND: a place where meaning was carried by POSITION.")
    if applied is None:
        out.append("   (--dry-run: nothing written)")
    else:
        out.append(f"   ✓ WROTE {applied} file(s) — only the clean ones.")
    return out


def main(argv: list[str]) -> int:
    """Consider every candidate, and write only what passes the gate clean."""
    apply = "--apply" in argv
    if not apply and "--dry-run" not in argv:
        # ⚑ INTENT IS STATED, NEVER DEFAULTED — the house contract for a mutating tool. A
        # default-dry silently does nothing when you meant to write; a default-apply writes when
        # you meant to look.
        sys.stderr.write(__doc__ or "")
        return 2

    # ⚑ RESOLVED AT INTAKE, because `corpus.ROOT` is absolute and `relative_to` refuses a
    # relative path against it — a caller typing the natural `substrate/x.py` would otherwise get
    # a traceback from deep inside the walk rather than an answer.
    roots = [Path(a).resolve() for a in argv if not a.startswith("-")]
    if not roots:
        sys.stderr.write("record_migrate: name a directory to convert\n")
        return 2

    outcomes = tuple(consider(path) for root in roots for path in candidates(root))
    for line in _report(outcomes, brief="--summary" in argv):
        sys.stdout.write(line + "\n")

    written = 0
    if apply:
        for outcome in outcomes:
            if outcome.writable:
                (corpus.ROOT / outcome.relpath).write_text(outcome.source, encoding="utf-8")
                written += 1

    for line in _summary(outcomes, applied=written if apply else None):
        sys.stdout.write(line + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
