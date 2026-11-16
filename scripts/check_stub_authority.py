#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""⟡stub-authority: every `.pyi` in `stubs/` must still match the module it describes.

⚑⚑ A STUB IS A CLAIM, AND AN UNVERIFIED CLAIM ABOUT TYPES IS WORTH LESS THAN NO CLAIM —
because it TYPE-CHECKS. `stubs/` exists so a promoted module can import an authority that is
not yet a package (`mypy_path` finds the `.pyi`, so the import is typed even though the module
is not). That mechanism buys real safety and opens a real hole: nothing otherwise notices when
the module moves and the stub does not.

⚑⚑⚑ THE HOLE IS NOT HYPOTHETICAL — THE FIRST STUB WRITTEN IN THIS TREE WAS WRONG, and
`stubtest` caught it on its first run. It declared `main(argv: list[str]) -> int`, invented
from the shape of OTHER gates rather than read from this one, which takes no parameters; and
it omitted `scan_file` entirely. A caller's argument list would then have been "checked"
against a fiction. **The defect the stub exists to prevent, committed inside the prevention,
caught only because this gate was written immediately after.**

⚑ WHAT IT VERIFIES AND WHAT IT CANNOT. `stubtest` imports the runtime module and compares
NAMES, ARITY and declared types against the stub. It cannot verify a type the source never
states: `scan_file(path)` is unannotated at source, so `path: str` in the stub stays a
READING. That half is closed by annotating the module, not by this gate — stated so a green
run is not read as more than it is.

⚑ NOT A RATCHET — A BIJECTION. There is no baseline and no paydown ledger, because a stub
either matches its module or it does not; there is no meaningful "existing debt" in a
correspondence. A stub that drifts is repaired or deleted.

⚑ AND IT DISCOVERS ITS POPULATION. The stubs are whatever is in `stubs/`; a frozen roster
here would be the third instance of the class this repo keeps recording (`run_selftests.DIRS`
twice, `_pycodemod_core`'s corpus roots once) — a list that can only ever be as current as
its last edit.

⚑⚑⚑ THE ELEVEN FAILURES THE WIDENED DISCOVERY EXPOSED WERE NOT ONE POPULATION, AND REPORTING
THEM AS ONE WAS THE REAL DEFECT. Sorting them (2026-09-02) found FOUR kinds, of which exactly
one was drift:

  * DRIFT — the stub contradicts the module. ONE instance: `panflute.load` declared its
    parameter `source` where the runtime spells it `input_stream`, so any keyword call would
    raise `TypeError` while type-checking clean. Repaired against the module.
  * DECLARED PARTIALITY — the stub declines a surface on purpose and says so. A stub over a
    third-party package SHADOWS it, so `stubtest`'s default reports every undeclared name as
    missing; `stubs/networkx` alone produces thousands of findings saying one thing its own
    docstring already says. See `substrate/stub_declines.py` for the two markers.
  * UNVERIFIABLE — `stubtest` could not run at all, because the runtime import failed for a
    reason outside the stub (`paperkit.bib` needs `bibparse`, absent from this machine).
  * A DISCOVERY ARTEFACT — `paperkit` was reported TWICE, as the package and as
    `paperkit.bib`, for one root cause.

⚑⚑ SO THE VERDICT IS MULTI-VALUED, BECAUSE COLLAPSING THE KINDS WAS THE BUG. `not verified` is
not `verified broken`: an absent third-party dependency is a fact about THIS MACHINE, and
rendering it identically to a contradicted signature is the same error as reading *no consumer
found* as *no consumer exists*.

⚑⚑⚑ BUT "UNVERIFIABLE" WAS ITSELF TWO KINDS COLLAPSED INTO ONE, AND THE PASSING HALF WAS
HIDING THE ONE CASE THAT MUST FAIL (⟡wire-the-stub-gate, 2026-09-02). Both arrive as the same
`ModuleNotFoundError`, and until this was split they were byte-identical to the reader:

  * ABSENT-DEP — the stub's own module is present and importable in principle; a THIRD-PARTY
    package it imports is not installed here. `paperkit.bib` needs `bibparse`. The stub is not
    implicated, the machine is, and a gate that failed on this would fail a clean checkout for
    a reason its author cannot fix — the Ⓝ95 ⟡the-tracking-gaps shape. **PASSES, reported.**
  * ORPHANED — the module the stub DESCRIBES is itself gone. `ModuleNotFoundError` names the
    stub's own module. This is not a fact about the machine at all: it is the exact defect this
    gate exists to catch, arriving in the one costume that used to walk past it. A stub for a
    deleted module is a claim about nothing, and it still SHADOWS that import name for every
    consumer — so mypy keeps type-checking callers against a module that no longer exists.
    **FAILS.**

⚑⚑ THE DISCRIMINATOR IS WHICH MODULE THE IMPORT ERROR NAMES, and it is mechanical rather than
a judgement: if the missing name is the stub's own module (or a submodule of it), the stub is
orphaned; if it is anything else, a dependency is absent. MEASURED, not reasoned — a stub for a
nonexistent `_ghostmod` was dropped into `stubs/` and the pre-split gate reported it beside
`paperkit` as NOT VERIFIED and exited 0. **A permanent free pass, in the gate whose subject is
stub authority.** See `classify`.

⚑ RELIEF IS ENUMERABLE AND LIVES IN THE STUB. A partial stub declares `⟡declines:` (a surface
it never claimed) and/or `⟡declines-signature:` (named findings on a signature it does claim)
in its own docstring, and the gate PRINTS the declaration beside its verdict — so the relief is
reviewed in the same breath as the result, and no allowlist lives here. Neither marker can
silence a CONTRADICTION on its own: a signature exemption must NAME the finding. That is what
let `panflute` decline every element constructor and still be caught renaming `load`'s
parameter.

⚑⚑⚑ AND A `.pyi` THAT WILL NOT PARSE IS A FAILURE OF ITS OWN, BECAUSE THE SILENT VERSION WAS
MEASURED HERE. A deliberately broken `_probe_broken.pyi` was dropped into `stubs/psycopg` and
this gate said NOTHING about it — not in `--list`, not in the verdict. The declarations reader
returned "declines nothing" for a file it could not parse, which is indistinguishable from a
file that genuinely declines nothing, so a typo inside a marker's own file would silently
WITHDRAW every exemption in it; the resulting findings would then be reported as drift in the
MODULE, sending the reader to repair source that was never wrong. `unreadable` is now its own
state, it names the file and the parse error, and it FAILS the gate — a stub nobody can read is
not a stub that agrees.

Blocking gate (pre-commit Phase A). Exit 0 = every stub matches, 1 = drift, an orphaned stub or
an unreadable one, 2 = cannot run.
Usage: check_stub_authority.py [--quiet] [--list] [--selftest]
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from substrate import stub_declines

# ⚑ THE `sys.path` INSERT THAT USED TO SIT HERE IS GONE, AND WITH IT A COMMENT EXPLAINING WHY
# IT SPELLED `absolute()` RATHER THAN `resolve()` (symlinks: this tooling is symlinked into
# other checkouts). The reasoning was sound and is no longer LOAD-BEARING HERE — measured,
# `attr_reads.py Path.absolute` finds no other read of it in this file — because the editable
# install resolves `substrate` with no path mutation at all. ⚑ The symlink hazard itself is
# NOT retired; it simply stops being this file's problem the moment the file stops computing
# its own repo root.
ROOT = Path(__file__).absolute().parent.parent
STUBS = ROOT / "stubs"

# Where the runtime modules the stubs describe actually live.
#
# ⚑ A STUB TYPES AN IMPORT; IT DOES NOT MAKE THE MODULE IMPORTABLE — and `stubtest` must
# IMPORT the runtime to compare against it. That is the same reachability gap that made a
# freshly-typed import fail at runtime with `ModuleNotFoundError` in `promote_agree`: the
# checker was satisfied and the interpreter was not.
_RUNTIME_PATHS = ("scripts", "scratch", "jea/metalanguage")

# A stubtest run over one small module is seconds; this bounds a hang, not the work.
_TIMEOUT_S = 300

_FLAGS = frozenset({"--quiet", "--list", "--selftest"})

# How many lines of one failure to show. A drift report longer than this is a rewritten
# module, not a discrepancy.
_DETAIL_LINES = 12

# ⚑ THE MARKER `stubtest` PRINTS WHEN THE RUNTIME WOULD NOT IMPORT. This is the seam between
# "the stub is wrong" and "this machine cannot answer", and it is the library's own wording.
_UNIMPORTABLE = "failed to import"

# ⚑ THE NAME THE IMPORT ERROR COULD NOT FIND, which is the whole discriminator between an
# ORPHANED stub and an ABSENT DEPENDENCY. It is CPython's own wording, stable across versions
# and quoted verbatim by stubtest.
_MISSING_RE = re.compile(r"No module named '([^']+)'")

# ⚑ THE FLAGS THAT GRANT RELIEF, so the selftest can ask which ones a command line carries
# without spelling them twice. `--ignore-positional-only` is NOT emitted and never will be: see
# `stubtest_argv`. It is listed so the selftest can assert its ABSENCE.
_RELIEF_FLAGS = ("--allowlist", "--ignore-missing-stub", "--ignore-positional-only")

# The states a stub can end in. `ok` and `absent-dep` pass; the rest fail.
OK = "ok"
DRIFT = "drift"
ORPHANED = "orphaned"
ABSENT_DEP = "absent-dep"

# ⚑ FAILING IS DECLARED AS A SET, NOT RE-DERIVED AT EACH READER. Three call sites ask "did this
# fail" and a fourth asks "which passed"; spelling the predicate once is what keeps a new state
# from being silently admitted as passing by whichever reader nobody updated.
_FAILING = frozenset({DRIFT, ORPHANED})


@dataclass(frozen=True, slots=True)
class Verdict:
    """One stub's result: what was checked, how it came out, and what it declined."""

    module: str
    state: str  # OK | DRIFT | ORPHANED | ABSENT_DEP
    detail: str
    declined: str | None

    @property
    def failed(self) -> bool:
        """True when this verdict must abort the commit."""
        return self.state in _FAILING


@dataclass(frozen=True, slots=True)
class Unreadable:
    """One `.pyi` that would not parse, and the error that says why.

    ⚑ THE FILE IS NAMED, NOT JUST THE UNIT. The whole point of collecting declarations across a
    package is that a declaration lives beside the code it excuses; a failure to read one must
    point at the same place, or the reader is sent to the package root to look for a typo that
    is three files away.
    """

    module: str
    path: Path
    reason: str


def stubs() -> list[str]:
    """Return the module names `stubs/` declares, discovered rather than listed.

    ⚑⚑⚑ A PACKAGE STUB IS A DIRECTORY, AND THE GLOB COULD NOT SEE ONE. Until 2026-09-02 this
    was `STUBS.glob("*.pyi")` — top-level FILES only — so it reported `clean (5 stub(s) match)`
    while `stubs/` held SEVENTEEN `.pyi` across five more packages. The verdict was true and was
    a fact about the GLOB: `census-green-is-a-fact-about-the-census`, in the gate whose subject
    is stub authority.

    ⚑⚑ AND THE UNSEEN HALF IS EXACTLY WHERE THE ONE REAL DRIFT WAS. `panflute.load`'s renamed
    parameter — a live latent break — sat in a stub this function could not reach, while all
    five it did reach were honest full-surface additions. Unverifiable is where drift
    accumulates, because nothing contradicts it.

    ⚑⚑⚑ A PACKAGE IS ONE UNIT, AND ENUMERATING ITS SUBMODULES CHECKED IT TWICE. `stubtest` on
    a package ALREADY RECURSES — running it on `paperkit` reports *"checked 3 modules"* — so
    naming `paperkit.bib` as well re-ran the same work and reported the same single root cause
    as two failures. The population is therefore the TOP-LEVEL stub: a directory's name, or a
    bare `.pyi`'s stem. That is also what makes the count meaningful, and why the gate now says
    which number it is quoting: files and stubs are different denominators.
    """
    if not STUBS.is_dir():
        return []
    names = {p.name for p in STUBS.iterdir() if p.is_dir() and any(p.rglob("*.pyi"))}
    names |= {p.stem for p in STUBS.glob("*.pyi")}
    return sorted(names)


def stub_sources(module: str) -> list[Path]:
    """Return every `.pyi` belonging to one stub unit.

    ⚑⚑ A PACKAGE'S DECLARATIONS ARE SPREAD ACROSS ITS SUBMODULES, AND READING ONLY THE ROOT
    LOST THEM. `psycopg`'s positional-only residue is documented in `rows.pyi`, beside the three
    protocols it is about — which is where it belongs, and where a first cut of this gate could
    not see it. Forcing every declaration up into `__init__.pyi` would separate each exemption
    from the code it excuses, which is how a declaration rots.
    """
    pkg = STUBS / module
    if pkg.is_dir():
        return sorted(pkg.rglob("*.pyi"))
    return [STUBS / f"{module}.pyi"]


def declared_surface(module: str) -> str | None:
    """Return the surface prose a stub unit declines, joining what its files each say."""
    parts = [d for p in stub_sources(module) if (d := stub_declines.declines(p)) is not None]
    return " ".join(parts) if parts else None


def declared_signatures(module: str) -> tuple[str, ...]:
    """Return every named allowlist entry a stub unit declares, across its files."""
    seen: list[str] = []
    for p in stub_sources(module):
        seen += [e for e in stub_declines.declines_signature(p) if e not in seen]
    return tuple(seen)


def unreadable(module: str) -> list[Unreadable]:
    """Return every `.pyi` in one stub unit that would not parse.

    ⚑ ASKED PER UNIT AND ANSWERED PER FILE. A package with one broken submodule is not wholly
    unreadable, and saying so would overstate the finding; naming the file is what makes it
    actionable.
    """
    out: list[Unreadable] = []
    for p in stub_sources(module):
        d = stub_declines.read(p)
        if d.state == stub_declines.UNREADABLE:
            out.append(Unreadable(module, p, d.reason))
    return out


def _env() -> dict[str, str]:
    """Build the environment `stubtest` needs to reach both the stub and the runtime."""
    env = dict(os.environ)
    env["MYPYPATH"] = str(STUBS)
    runtime = os.pathsep.join(str(ROOT / p) for p in _RUNTIME_PATHS)
    prior = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f"{runtime}{os.pathsep}{prior}" if prior else runtime
    return env


def missing_module(detail: str) -> str | None:
    """Return the module name an import error could not find, or None."""
    m = _MISSING_RE.search(detail)
    return m.group(1) if m is not None else None


def classify(module: str, detail: str) -> str:
    """Return the state a failed `stubtest` run represents for `module`.

    ⚑⚑⚑ THE THREE-WAY SPLIT THAT THIS FUNCTION MAKES IS THE GATE'S WHOLE MEANING, and two of
    its three arms were ONE arm until ⟡wire-the-stub-gate. An unimportable runtime is not
    self-evidently the machine's fault: it is the machine's fault only when the module that
    could not be found is a THIRD PARTY. When the missing name is the stub's OWN module, the
    stub describes something that is not there — the defect this gate exists to catch, wearing
    the costume that used to walk past it.

    ⚑⚑ AND `startswith` IS ON A DOTTED PREFIX, NOT A BARE ONE. `paperkit.bib` failing to find
    `bibparse` must not match, and a package stub failing to find its own `paperkit.grade`
    must. Comparing `f"{missing}."` against `f"{module}."` gets both: it is true for the module
    itself and for any submodule, and false for a sibling whose name merely shares a prefix
    (`paperkit_extras` is not `paperkit`). A bare `startswith(module)` would call that sibling
    orphaned and send the reader to delete a stub that is fine.

    ⚑ A NON-IMPORT FAILURE IS DRIFT BY CONSTRUCTION. stubtest ran, compared, and disagreed;
    there is no machine-fact arm to fall into.
    """
    if _UNIMPORTABLE not in detail:
        return DRIFT
    missing = missing_module(detail)
    if missing is not None and f"{missing}.".startswith(f"{module}."):
        return ORPHANED
    return ABSENT_DEP


def stubtest_argv(module: str, allowlist: Path | None) -> list[str]:
    """Build the `stubtest` command line for one module, given its declared relief.

    ⚑ A DECLINED SURFACE BECOMES `--ignore-missing-stub`, which is scoped by construction: it
    can only silence *absent*, never *contradicted*. A declined SIGNATURE becomes an allowlist
    of NAMED entries.

    ⚑⚑ THE BLANKET FLAG IS REFUSED ON PURPOSE. `--ignore-positional-only` turns `stubs/psycopg`
    green in one word — measured — and would silence that finding class across all 83 modules of
    the package, including a contradiction nobody has looked at yet. An allowlist entry names
    the one finding, so relief is as reviewable as the verdict.

    ⚑ AND `--ignore-unused-allowlist` IS DELIBERATELY NOT PASSED: an entry matching nothing
    becomes a finding of its own, so a declared exemption cannot outlive what it excused. If
    psycopg adopts PEP 570, its three entries stop matching and the gate says so.
    """
    argv = [
        sys.executable,
        "-m",
        "mypy.stubtest",
        module,
        "--mypy-config-file",
        str(ROOT / "pyproject.toml"),
    ]
    if declared_surface(module) is not None:
        argv.append("--ignore-missing-stub")
    if allowlist is not None:
        argv += ["--allowlist", str(allowlist)]
    return argv


def relief_in(argv: list[str]) -> list[str]:
    """Return the relief flags a command line carries, sorted."""
    return sorted(f for f in _RELIEF_FLAGS if f in argv)


def check(module: str) -> Verdict:
    """Run `stubtest` for one module and classify what came back."""
    declined = declared_surface(module)
    entries = declared_signatures(module)
    tmp = tempfile.mkdtemp(prefix="stub-authority-")
    try:
        allowlist: Path | None = None
        if entries:
            allowlist = Path(tmp) / "allowlist.txt"
            allowlist.write_text("".join(f"{e}\n" for e in entries), encoding="utf-8")
        try:
            p = subprocess.run(
                stubtest_argv(module, allowlist),
                cwd=str(ROOT),
                env=_env(),
                capture_output=True,
                text=True,
                timeout=_TIMEOUT_S,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as e:
            return Verdict(module, ABSENT_DEP, f"could not run stubtest: {e}", declined)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if p.returncode == 0:
        return Verdict(module, OK, "", declined)
    detail = (p.stdout or p.stderr or "").strip()
    return Verdict(module, classify(module, detail), detail, declined)


def _first_line(detail: str) -> str:
    """Return the first non-blank line of a stubtest report."""
    return next((ln for ln in detail.splitlines() if ln.strip()), "")


def _render_unreadable(broken: list[Unreadable]) -> None:
    """Print the `.pyi` files that would not parse, each with its own error."""
    sys.stdout.write(
        f"stub-authority: BROKEN — {len(broken)} stub file(s) do not parse. A `.pyi` IS a\n"
        f"  Python file, and one that cannot be read declares NOTHING — which is\n"
        f"  indistinguishable from declining nothing, so every exemption in it is silently\n"
        f"  withdrawn and its findings resurface as drift in the MODULE:\n"
    )
    for b in broken:
        sys.stdout.write(f"    ✗ {b.path.relative_to(STUBS)} ({b.module}): {b.reason}\n")
    sys.stdout.write(
        "  NEXT: open the file named above and fix the syntax error, then re-run\n"
        "  `python3 scripts/check_stub_authority.py`.\n"
    )


def _render_absent(unverified: list[Verdict]) -> None:
    """Print the stubs a missing third-party dependency kept this machine from verifying."""
    if not unverified:
        return
    sys.stdout.write(
        f"  ⚑ {len(unverified)} stub(s) NOT VERIFIED — a THIRD-PARTY package the runtime "
        f"imports is not installed here. That is a fact about THIS MACHINE, not about the "
        f"stub, and does not fail the gate:\n"
    )
    for v in unverified:
        sys.stdout.write(f"    ? {v.module}: {_first_line(v.detail)}\n")


def _render(verdicts: list[Verdict]) -> None:
    """Print the sorted population: drift, then orphans, then what could not be verified."""
    drift = [v for v in verdicts if v.state == DRIFT]
    orphaned = [v for v in verdicts if v.state == ORPHANED]
    sys.stdout.write(
        f"stub-authority: BROKEN — {len(drift) + len(orphaned)} of {len(verdicts)} stub(s) do "
        f"not match their module:\n"
    )
    for v in drift:
        sys.stdout.write(f"    ✗ {v.module} — DRIFT: the stub contradicts the module\n")
        sys.stdout.writelines(f"        {ln}\n" for ln in v.detail.splitlines()[:_DETAIL_LINES])
    for v in orphaned:
        sys.stdout.write(
            f"    ✗ {v.module} — ORPHANED: the module this stub describes is GONE\n"
            f"        {_first_line(v.detail)}\n"
        )
    if orphaned:
        sys.stdout.write(
            "  ⚑ An ORPHANED stub is not a fact about this machine: the name that could not\n"
            "  be imported is the stub's OWN module. It still SHADOWS that import for every\n"
            "  consumer, so mypy keeps checking callers against a module that no longer\n"
            "  exists. NEXT: delete the stub, or restore the module it describes.\n"
        )
    _render_absent([v for v in verdicts if v.state == ABSENT_DEP])
    if drift:
        sys.stdout.write(
            "  A stub that has drifted is WORSE than no stub: callers type-check against a\n"
            "  fiction. NEXT: repair it against the module, or delete it and let the import\n"
            "  be untyped honestly. A stub that declines a surface ON PURPOSE says so with\n"
            "  `⟡declines:` in its own docstring — see substrate/stub_declines.py.\n"
        )


def _render_clean(verdicts: list[Verdict], *, quiet: bool) -> None:
    """Print the passing verdict, naming what each stub declined."""
    absent = [v for v in verdicts if v.state == ABSENT_DEP]
    if quiet and not absent:
        return
    ok = [v for v in verdicts if v.state == OK]
    sys.stdout.write(f"stub-authority: clean ({len(ok)} of {len(verdicts)} stub(s) match).\n")
    for v in ok:
        if v.declined is not None:
            sys.stdout.write(f"    · {v.module} declines: {v.declined}\n")
        named = declared_signatures(v.module)
        if named:
            sys.stdout.write(f"      signature exemptions: {', '.join(named)}\n")
    for v in absent:
        sys.stdout.write(f"    ? {v.module} NOT VERIFIED: {_first_line(v.detail)}\n")


def main(argv: list[str]) -> int:
    """Check every stub; 1 on drift/orphan/unreadable, 2 when a flag is unknown."""
    unknown = [a for a in argv[1:] if a.startswith("-") and a not in _FLAGS]
    if unknown:
        sys.stdout.write(
            f"check_stub_authority.py: unknown flag(s) {' '.join(unknown)} — "
            f"known: {' '.join(sorted(_FLAGS))}\n"
            "  Refusing rather than running with a flag you did not mean.\n"
        )
        return 2

    found = stubs()
    if "--list" in argv:
        for m in found:
            declared = declared_surface(m)
            named = declared_signatures(m)
            suffix = f" — declines: {declared}" if declared is not None else ""
            if named:
                suffix += f" [signature: {', '.join(named)}]"
            sys.stdout.write(f"    {m}{suffix}\n")
            for b in unreadable(m):
                sys.stdout.write(f"      ✗ UNREADABLE {b.path.name}: {b.reason}\n")
        sys.stdout.write(f"stub-authority: {len(found)} stub(s) in stubs/\n")
        return 0

    # ⚑ AN EMPTY POPULATION IS REPORTED, NEVER PASSED SILENTLY. Zero stubs is a legitimate
    # state (nothing has needed one yet) and it is also what a moved directory looks like. A
    # gate that says nothing in both cases certifies its own blind spot.
    if not found:
        if "--quiet" not in argv:
            sys.stdout.write(
                "stub-authority: no stubs in stubs/ — nothing to verify (a fact about the "
                "POPULATION, not a pass)\n"
            )
        return 0

    # ⚑⚑ THE PARSE CHECK RUNS FIRST AND SHORT-CIRCUITS, because an unreadable `.pyi` makes every
    # DOWNSTREAM answer unreliable: its declarations are missing, so `stubtest` is handed the
    # wrong relief and reports findings that belong to the typo, not to the module. Reporting
    # both at once would bury the cause under its own consequences.
    broken = [b for m in found for b in unreadable(m)]
    if broken:
        _render_unreadable(broken)
        return 1

    verdicts = [check(m) for m in found]
    if any(v.failed for v in verdicts):
        _render(verdicts)
        return 1
    _render_clean(verdicts, quiet="--quiet" in argv)
    return 0


def _selftest() -> int:
    """Cases pinning the population shape and the multi-valued classification."""
    cases: list[tuple[str, object, object]] = []

    def check_case(name: str, got: object, want: object) -> None:
        cases.append((name, got, want))

    # ⚑ MEMBERSHIP IS ASKED AS AN INTERSECTION, NOT A BOOL, so a failure prints WHICH
    # expectation broke. The discriminators live in this one comparison: `paperkit.bib` must be
    # ABSENT (a package is one unit) and `itertools` must be ABSENT (the population is not
    # every importable name).
    found = set(stubs())
    probe = {"paperkit", "paperkit.bib", "tsdbprobe", "psycopg", "itertools"}
    check_case(
        "the population is top-level stubs only",
        sorted(found & probe),
        ["paperkit", "psycopg", "tsdbprobe"],
    )

    # ⚑ A PACKAGE UNIT IS ALL ITS FILES, a bare stub is exactly one.
    check_case(
        "a package unit gathers every .pyi under it",
        [p.name for p in stub_sources("paperkit")],
        ["__init__.pyi", "bib.pyi", "grade.pyi"],
    )
    check_case(
        "a bare stub is its own single file",
        [p.name for p in stub_sources("tsdbprobe")],
        ["tsdbprobe.pyi"],
    )

    # ⚑ THE SEAM THAT MATTERS: an absent third-party dep must not read as drift, and — the
    # DISCRIMINATOR — a real contradiction must not be excused as a machine fact.
    check_case(
        "a missing third-party dep is absent-dep",
        classify(
            "paperkit",
            "error: paperkit.bib failed to import. ModuleNotFoundError: No module named 'bibparse'",
        ),
        ABSENT_DEP,
    )
    check_case(
        "a renamed parameter is drift, not an import failure",
        classify("panflute", 'error: stub parameter "source" differs from runtime "input_stream"'),
        DRIFT,
    )

    # ⚑⚑ THE SPLIT THIS GATE WAS WIRED FOR. Both arms below are `failed to import` with a
    # `ModuleNotFoundError`; only the NAME differs, and that name is the whole verdict. MEASURED
    # against a real `stubs/_ghostmod.pyi` before it was written down.
    check_case(
        "a stub whose OWN module is gone is orphaned",
        classify(
            "_ghostmod",
            "error: _ghostmod failed to import. ModuleNotFoundError: No module named '_ghostmod'",
        ),
        ORPHANED,
    )
    check_case(
        "a package stub missing its OWN submodule is orphaned",
        classify(
            "paperkit",
            "error: paperkit failed to import. ModuleNotFoundError: "
            "No module named 'paperkit.grade'",
        ),
        ORPHANED,
    )
    # ⚑ THE PREFIX TRAP: a SIBLING sharing a name prefix is not this stub's module. A bare
    # `startswith` would call this orphaned and send the reader to delete a healthy stub.
    check_case(
        "a prefix-sharing sibling is NOT orphaned",
        classify(
            "paperkit",
            "error: paperkit failed to import. ModuleNotFoundError: "
            "No module named 'paperkit_extras'",
        ),
        ABSENT_DEP,
    )
    # ⚑ AND AN IMPORT FAILURE WITH NO PARSEABLE NAME stays on the passing arm: an unparsed
    # message is not evidence of an orphan, and inventing one would fail a clean checkout.
    check_case(
        "an import failure naming no module is absent-dep",
        classify("paperkit", "error: paperkit failed to import. RuntimeError: boom"),
        ABSENT_DEP,
    )
    check_case(
        "the missing name is read out of the message",
        missing_module("ModuleNotFoundError: No module named 'bibparse'"),
        "bibparse",
    )
    check_case(
        "a message with no missing name reads None",
        missing_module("error: something else entirely"),
        None,
    )

    # ⚑ WHICH STATES ABORT THE COMMIT, asked as a set so a newly-added state cannot be
    # silently admitted as passing by whichever reader nobody updated.
    check_case(
        "exactly drift and orphaned fail the gate",
        sorted(s for s in (OK, DRIFT, ORPHANED, ABSENT_DEP) if Verdict("m", s, "", None).failed),
        [DRIFT, ORPHANED],
    )

    # ⚑ DISCRIMINATOR PAIR: a partial third-party stub declares, a complete first-party one
    # does not. Asking both of one expression pins that the reader discriminates rather than
    # answering "declined" to everything.
    declared = {
        m
        for m in ("psycopg", "panflute", "tsdbprobe", "agda_lex")
        if declared_surface(m) is not None
    }
    check_case("only the partial stubs declare declines", sorted(declared), ["panflute", "psycopg"])

    # ⚑ A SUBMODULE'S DECLARATION MUST REACH THE UNIT. psycopg's residue is documented in
    # `rows.pyi`, not the package root; reading only the root lost it.
    check_case(
        "a submodule's signature declaration reaches the package",
        sorted(declared_signatures("psycopg")),
        [
            "psycopg.rows.BaseRowFactory.__call__",
            "psycopg.rows.RowFactory.__call__",
            "psycopg.rows.RowMaker.__call__",
        ],
    )
    # ⚑ DISCRIMINATOR: a complete stub declares no entries at all.
    check_case(
        "a complete stub declares no signature exemptions", declared_signatures("tsdbprobe"), ()
    )

    # ⚑⚑ THE LIVE TREE HAS NO UNREADABLE STUB, and that is the DISCRIMINATOR for the parse
    # check: a predicate that flagged everything would pass a "the broken one is flagged" case
    # on its own. Both halves are asked.
    check_case(
        "no stub in the live tree fails to parse",
        [str(b.path) for m in stubs() for b in unreadable(m)],
        [],
    )

    # ⚑ THE RELIEF MUST REACH THE COMMAND LINE, AND ONLY WHEN DECLARED. Asking for the SET of
    # relief flags makes the discriminators readable: a complete stub gets NONE, and the
    # blanket `--ignore-positional-only` appears in no arm at all.
    check_case(
        "a declining stub is relieved of missing names only",
        relief_in(stubtest_argv("psycopg", None)),
        ["--ignore-missing-stub"],
    )
    check_case("a complete stub gets NO relief", relief_in(stubtest_argv("tsdbprobe", None)), [])
    check_case(
        "a declared allowlist reaches the command line",
        relief_in(stubtest_argv("networkx", Path("/nonexistent/a.txt"))),
        ["--allowlist", "--ignore-missing-stub"],
    )

    check_case(
        "the first line of a report is its verdict line",
        _first_line("\n\nerror: x failed to import\nStub: y"),
        "error: x failed to import",
    )

    ok = sum(1 for _n, g, w in cases if g == w)
    for n, g, w in cases:
        if g != w:
            sys.stdout.write(f"  FAIL {n}\n       got {g!r} want {w!r}\n")
    sys.stdout.write(f"check_stub_authority selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    sys.exit(main(sys.argv))
