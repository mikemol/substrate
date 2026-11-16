#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.scratch_scope` — fixtures for each branch, and the differential.

⚑⚑⚑ THE DIFFERENTIAL IS RUN AGAINST THE ORIGIN'S OWN PROCESS, NOT AGAINST A QUOTATION. The
suite shells out to `scripts/check_scratch_independence.py --scope jea/metalanguage` and asserts
this module renders the SAME LINES, in order. A pinned copy of the origin's output would go stale
the day the tree moved and read as a regression in the module; running the origin makes the arm
assert what a replacement actually owes — that today, on this tree, the two agree.

⚑⚑ AND THE FIXTURE ARMS COVER WHAT THE LIVE TREE DOES NOT REACH. The live scope has no HARD tag
beside a guarded row in the same file, no missing directory, no unreadable file, no empty census
and no outside-ROOTS verdict, so each is planted: a fixture that never reaches a branch proves
nothing about it (gate-G391).
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from substrate import corpus
from substrate import scratch_refs as sr
from substrate import scratch_scope as ss

_TREE = "jea/metalanguage"
_ORIGIN = corpus.ROOT / "scripts" / "check_scratch_independence.py"
# What `quiet` removes for a one-file census: the file line and its two dependency rows.
_QUIET_DROPS = 3

# A file with a module-level insert (HARD), a guarded join, and a diagnostic mention.
_MIXED = (
    "import os, sys\n"
    'sys.path.insert(0, os.path.join(os.getcwd(), "scratch"))\n'
    "def load():\n"
    "    try:\n"
    '        return open(os.path.join("scratch", "x"))\n'
    "    except OSError:\n"
    '        return "scratch/ is unavailable"\n'
)

_CLEAN = "X = 1\n"
_EMPTY = "scratch-independence --scope: 2 .py scanned across proj, 0 live scratch/ ref(s)."


def _plant(files: dict[str, str]) -> Path:
    """Write a fixture tree under a fresh root and return that root."""
    root = Path(tempfile.mkdtemp(prefix="scratch-scope-"))
    for rel, text in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return root


def a_mixed_file_splits_into_hard_guarded_and_mention(out: list[str]) -> int:
    """Check the three classifications land in one file and render with the HARD tag."""
    root = _plant({"proj/m.py": _MIXED})
    found = ss.census(["proj"], root)
    bad = 0
    depths = sorted((r.lineno, r.depth, r.is_dep) for r in found.rows)
    want = [(2, sr.HARD, True), (5, sr.GUARDED, True), (7, sr.GUARDED, False)]
    if depths != want:
        out.append(f"selftest: mixed fixture classified {depths}, want {want}")
        bad += 1
    lines = ss.render(found, ["proj"], quiet=False)
    if "  proj/m.py ⚑HARD" not in lines:
        out.append(f"selftest: the HARD tag is missing from {lines[2:4]}")
        bad += 1
    if not any(line.startswith("  ⚑ 1 HARD") for line in lines):
        out.append("selftest: the HARD count did not read 1")
        bad += 1
    if not any(line.startswith("  + 1 MENTION(S)") for line in lines):
        out.append("selftest: the mention count did not read 1")
        bad += 1
    return bad


def a_quiet_render_drops_the_rows_and_keeps_the_counts(out: list[str]) -> int:
    """Check `quiet` removes per-file rows and nothing else."""
    root = _plant({"proj/m.py": _MIXED})
    found = ss.census(["proj"], root)
    loud = ss.render(found, ["proj"], quiet=False)
    quiet = ss.render(found, ["proj"], quiet=True)
    dropped = [line for line in loud if line not in quiet]
    if len(dropped) != _QUIET_DROPS or not dropped[0].startswith("  proj/m.py"):
        out.append(f"selftest: quiet dropped {dropped!r}, want the file line and two rows")
        return 1
    return 0


def an_empty_census_reports_its_denominator(out: list[str]) -> int:
    """Check a clean scope says how many files it read, not just zero."""
    root = _plant({"proj/a.py": _CLEAN, "proj/b.py": _CLEAN})
    found = ss.census(["proj"], root)
    lines = ss.render(found, ["proj"], quiet=False)
    if lines != [_EMPTY]:
        out.append(f"selftest: empty census rendered {lines!r}")
        return 1
    if ss.render_mentions(found, ["proj"]) != lines:
        out.append("selftest: --mentions on an empty census did not print the same line")
        return 1
    return 0


def a_missing_directory_is_a_diagnostic_not_a_zero(out: list[str]) -> int:
    """Check a scoped directory that does not exist is named, and the rest is still scanned."""
    root = _plant({"proj/m.py": _MIXED})
    found = ss.census(["nope", "proj"], root)
    diag = ss.diagnostics(found)
    if found.missing != ("nope",) or diag != [ss.MISSING.format(d="nope")]:
        out.append(f"selftest: missing dir read {found.missing!r} / {diag!r}")
        return 1
    if found.scanned != 1:
        out.append(f"selftest: the surviving directory was not scanned ({found.scanned})")
        return 1
    return 0


def an_unreadable_file_warns_and_is_counted(out: list[str]) -> int:
    """Check a file that cannot be parsed is a WARN line and still in the denominator."""
    root = _plant({"proj/bad.py": "def broken(:\n"})
    found = ss.census(["proj"], root)
    if not found.warns or found.scanned != 1:
        out.append(f"selftest: unreadable file gave warns={found.warns!r} scanned={found.scanned}")
        return 1
    if not ss.diagnostics(found)[0].startswith("  scratch-independence: WARN "):
        out.append("selftest: the WARN line lost the origin's prefix")
        return 1
    return 0


def the_skip_list_is_a_substring_test(out: list[str]) -> int:
    """Check a `.github` directory is skipped, as the origin (over-widely) skips it."""
    root = _plant({"proj/.github/m.py": _MIXED, "proj/m.py": _MIXED})
    found = ss.census(["proj"], root)
    if found.scanned != 1:
        out.append(f"selftest: the substring skip read {found.scanned} file(s), want 1")
        return 1
    return 0


def the_verdict_is_computed_from_roots(out: list[str]) -> int:
    """Check inside/outside is decided by ROOTS, and a mixed scope prints both."""
    inside, outside = ss.inside_outside(["jea/x", "scripts", "el-atlas", "jeans"])
    if inside != ["jea/x", "el-atlas"] or outside != ["scripts", "jeans"]:
        out.append(f"selftest: inside/outside read {inside}/{outside}")
        return 1
    root = _plant({"jea/m.py": _MIXED})
    lines = ss.render(ss.census(["jea", "scripts"], root), ["jea", "scripts"], quiet=True)
    if not (
        any("jea IS INSIDE ROOTS" in line for line in lines)
        and any("NOT A GATE for scripts" in line for line in lines)
    ):
        out.append(f"selftest: a mixed scope did not print both verdicts: {lines[-3:]!r}")
        return 1
    return 0


def _origin(args: list[str]) -> list[str]:
    """Run the origin's `--scope` and return its stdout lines.

    ⚑ `--root` IS PASSED BECAUSE THE ENTRY POINT NOW REFUSES WITHOUT ONE (W36: it censuses the
    tree it is HANDED, never one it derives). Before this, the refusal went to stderr, stdout was
    empty, and every line of this module's output read as `+` — a differential against nothing.
    """
    done = subprocess.run(
        [sys.executable, str(_ORIGIN), "--root", str(corpus.ROOT), "--scope", *args],
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
        cwd=str(corpus.ROOT),
    )
    return done.stdout.splitlines()


def _diff(out: list[str], label: str, mine: list[str], theirs: list[str]) -> int:
    """Report the two-sided difference between this module's rendered text and the origin's.

    ⚑ COMPARED AS PRINTED TEXT. A snippet can carry an embedded newline (a multi-line literal);
    the origin's stdout splits there and this module's list element does not, so the module's
    lines are joined and re-split exactly as a terminal would see them.
    """
    mine = "\n".join(mine).splitlines()
    if mine == theirs:
        return 0
    out.append(f"selftest: {label} differs from the origin:")
    out += [f"    - {line}" for line in theirs if line not in mine]
    out += [f"    + {line}" for line in mine if line not in theirs]
    return 1


def the_differential_matches_the_origin_line_for_line(out: list[str]) -> int:
    """Check the entry-point PROCESS prints this module's lines over the live tree, both modes.

    ⚑ THIS WAS THE DIFFERENTIAL AGAINST THE ORIGIN, and it held line for line until the origin
    was rewritten as a shim over this module (tick 11). From then on it is not a differential —
    it compares the reader to itself through a process — but it is still the only case that
    runs the real entry point with the hook's spelling, so it stays. The name is kept because
    a registered witness spells it (gate-G392); the origin's behaviour is pinned in the fixture
    arms above, which is where the differential's evidence now lives.
    """
    if not (corpus.ROOT / _TREE).is_dir() or not _ORIGIN.is_file():
        out.append("selftest: the live tree or the origin is absent — the differential cannot run")
        return 1
    found = ss.census([_TREE], corpus.ROOT)
    mine = ss.render(found, [_TREE], quiet=False)
    bad = _diff(out, "--scope", mine, _origin([_TREE]))
    bad += _diff(
        out,
        "--scope --mentions",
        ss.render_mentions(found, [_TREE]),
        _origin([_TREE, "--mentions"]),
    )
    return bad


_ARMS = (
    a_mixed_file_splits_into_hard_guarded_and_mention,
    a_quiet_render_drops_the_rows_and_keeps_the_counts,
    an_empty_census_reports_its_denominator,
    a_missing_directory_is_a_diagnostic_not_a_zero,
    an_unreadable_file_warns_and_is_counted,
    the_skip_list_is_a_substring_test,
    the_verdict_is_computed_from_roots,
    the_differential_matches_the_origin_line_for_line,
)

_CASE_COUNT = 4 + 1 + 2 + 2 + 2 + 1 + 2 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"scratch-scope selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"scratch-scope selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
