#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.scratch_gate` — the verdict both ways, severity, and the differential.

⚑⚑⚑ THE DIFFERENTIAL RUNS THE ORIGIN GATE AND COMPARES STDERR LINE FOR LINE. The gate FAILS on
the live tree today (the seven runtime couplings in `jea/metalanguage`), so the failing report is
what the live differential covers; the OK line is planted under a clean fixture root, where the
origin cannot be pointed (it walks ROOTS from its own repo root), so that half is asserted
against the origin's wording rather than its process.

⚑⚑ THE STALE ARM IS REBUILT AS A PROPERTY. The origin's suite pinned `809 in _dep_sites(sql_lift)`
and the coupling moved to 811, reddening the whole 363-finding file behind the per-file gate
(gate-G376) — a one-line repair that could not land. The property that arm meant is: the
`sys.path.insert` feeding the import in that file is a RUNTIME hit, wherever it sits. So the
arm asks the classifier for the file's RUNTIME hits and asserts there is one — a moved line no
longer reddens a test that was never about the line.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from substrate import corpus
from substrate import scratch_gate as sg

_ORIGIN = corpus.ROOT / "scripts" / "check_scratch_independence.py"
_PROBE = corpus.ROOT / "jea" / "metalanguage" / "sql_lift.py"
# The fixture populations the arms plant.
_TWO = 2

# A module-level insert (RUNTIME) and a diagnostic (text) in one promoted file.
_MIXED = (
    "import os, sys\n"
    'sys.path.insert(0, os.path.join(os.getcwd(), "scratch"))\n'
    'MSG = "see scratch/ for the old tool"\n'
)

_OK = "scratch-independence (Λ8): OK (2 .py scanned across {roots}, 0 live refs)"
_NO_RUNTIME = "selftest: sql_lift.py has no RUNTIME hit — the insert feeding the import is text"


def _plant(files: dict[str, str]) -> Path:
    """Write a fixture tree under a fresh root and return that root."""
    root = Path(tempfile.mkdtemp(prefix="scratch-gate-"))
    for rel, text in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return root


def a_clean_corpus_is_ok_and_names_its_denominator(out: list[str]) -> int:
    """Check a scratch-free root passes, and the OK line carries the scanned count."""
    root = _plant({"jea/a.py": "X = 1\n", "el-atlas/b.py": "Y = 2\n"})
    result = sg.run(root)
    lines, err = sg.render(result)
    if not result.ok or err or result.scanned != _TWO:
        out.append(f"selftest: a clean root read ok={result.ok} err={err!r} n={result.scanned}")
        return 1
    if lines != [_OK.format(roots="/".join(result.roots))]:
        out.append(f"selftest: the OK line read {lines!r}")
        return 1
    return 0


def a_live_reference_fails_with_runtime_first(out: list[str]) -> int:
    """Check one file with a coupling and a mention fails, counts both, orders RUNTIME first."""
    root = _plant({"jea/m.py": _MIXED})
    result = sg.run(root)
    lines, err = sg.render(result)
    bad = 0
    if result.ok or lines or result.runtime != 1 or len(result.hits) != _TWO:
        out.append(f"selftest: a mixed file read ok={result.ok} hits={result.hits!r}")
        bad += 1
    if not err[0].endswith("— 1 RUNTIME, 1 text:"):
        out.append(f"selftest: the headline did not split the counts: {err[0]!r}")
        bad += 1
    runtime_first = err[1].startswith("    ⚑ RUNTIME  jea/m.py:2")
    text_second = err[2].startswith("      text     jea/m.py:3")
    if not (runtime_first and text_second):
        out.append(f"selftest: the rows are not RUNTIME-first: {err[1:3]!r}")
        bad += 1
    if not err[-2].startswith("  ⚑ The 1 RUNTIME ref(s)") or not err[-1].startswith("  A promoted"):
        out.append(f"selftest: the closing notes are missing: {err[-2:]!r}")
        bad += 1
    return bad


def a_text_only_failure_omits_the_runtime_note(out: list[str]) -> int:
    """Check the RUNTIME note is conditional — a mention-only failure does not print it."""
    root = _plant({"jea/m.py": 'MSG = "see scratch/"\n'})
    _lines, err = sg.render(sg.run(root))
    noted = any("RUNTIME ref(s)" in line for line in err)
    if noted or not err[0].endswith("0 RUNTIME, 1 text:"):
        out.append(f"selftest: a text-only failure printed the runtime note: {err!r}")
        return 1
    return 0


def an_unreadable_file_warns_and_does_not_pass_silently(out: list[str]) -> int:
    """Check a file that cannot be parsed is a WARN line on stderr, with the verdict unchanged."""
    root = _plant({"jea/bad.py": "def broken(:\n"})
    result = sg.run(root)
    _lines, err = sg.render(result)
    if not result.warns or not err or not err[0].startswith("  scratch-independence: WARN "):
        out.append(f"selftest: an unreadable file gave warns={result.warns!r} err={err!r}")
        return 1
    return 0


def an_absent_root_is_skipped_not_fatal(out: list[str]) -> int:
    """Check a promoted root missing from a tree is skipped, as the origin skips it."""
    root = _plant({"jea/a.py": "X = 1\n"})
    result = sg.run(root)
    if not result.ok or result.scanned != 1:
        out.append(f"selftest: a tree with one root present read {result!r}")
        return 1
    return 0


def the_insert_feeding_an_import_is_runtime_wherever_it_sits(out: list[str]) -> int:
    """Check the property the stale `809 in _dep` arm meant, without pinning a line."""
    if not _PROBE.is_file():
        out.append(f"selftest: {_PROBE.name} is absent — the property cannot be checked")
        return 1
    hits, _w = sg._hits_of(_PROBE, corpus.ROOT)  # noqa: SLF001 - the classifier is the unit
    if not any(h.severity == sg.DEP for h in hits):
        out.append(_NO_RUNTIME)
        return 1
    return 0


def _origin() -> list[str]:
    """Run the origin gate and return its stderr lines."""
    done = subprocess.run(
        [sys.executable, str(_ORIGIN), "--root", str(corpus.ROOT)],  # noqa: S603
        capture_output=True,
        text=True,
        check=False,
        timeout=600,
        cwd=str(corpus.ROOT),
    )
    return done.stderr.splitlines()


def the_differential_matches_the_origin_gate_on_the_live_tree(out: list[str]) -> int:
    """Check the entry-point PROCESS prints this gate's stderr over the origin's two roots.

    ⚑ A DIFFERENTIAL UNTIL TICK 11, when the origin became a shim over this module; now the
    end-to-end run of the real entry point, kept under its registered name (gate-G394). The
    origin's report shape is pinned by the fixture arms above. ⚑ The process side runs the
    shim BARE, i.e. over `promoted.ROOTS`, so it is compared against `run()` over the SAME
    roster — not `_ORIGIN_ROOTS`, which only the retired origin ever meant.
    """
    if not _ORIGIN.is_file():
        out.append("selftest: the origin is absent — the differential cannot run")
        return 1
    result = sg.run(corpus.ROOT)
    _lines, err = sg.render(result)
    mine = "\n".join(err).splitlines()
    theirs = _origin()
    if result.ok and not theirs:
        return 0
    if mine != theirs:
        out.append("selftest: the gate's stderr differs from the origin:")
        out += [f"    - {line}" for line in theirs if line not in mine]
        out += [f"    + {line}" for line in mine if line not in theirs]
        return 1
    return 0


_ARMS = (
    a_clean_corpus_is_ok_and_names_its_denominator,
    a_live_reference_fails_with_runtime_first,
    a_text_only_failure_omits_the_runtime_note,
    an_unreadable_file_warns_and_does_not_pass_silently,
    an_absent_root_is_skipped_not_fatal,
    the_insert_feeding_an_import_is_runtime_wherever_it_sits,
    the_differential_matches_the_origin_gate_on_the_live_tree,
)

_CASE_COUNT = 2 + 4 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"scratch-gate selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"scratch-gate selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
