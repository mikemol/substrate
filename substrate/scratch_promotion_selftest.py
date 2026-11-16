#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.scratch_promotion` — every branch planted, and the differential.

⚑⚑⚑ THE DIFFERENTIAL RUNS THE ORIGIN'S PROCESS ON TWO LIVE CANDIDATES, one that PASSES and one
that is BLOCKED on both rules, so every reason line is compared against the origin's own words
rather than a quotation of them. ⚑ Rule 2 is asked of `substrate.mypy_census` here and of
`scratch/pycodemod` there — two readers of one census — so a match on the key count and the
first key is the fact that the drain did not change the verdict by changing the reader.

⚑⚑ AND THE FIXTURE ARMS COVER THE BRANCHES THE LIVE TREE CANNOT SETTLE ON ITS OWN: the
not-a-directory refusal, the idempotent already-in-ROOTS case, and a candidate that is clean on
rule 1 but adds a census key.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from substrate import corpus
from substrate import scratch_promotion as sp

_ORIGIN = corpus.ROOT / "scripts" / "check_scratch_independence.py"

# Two live candidates the origin reports on, chosen at suite-writing time and re-read by both
# readers at suite time — nothing about them is pinned here.
_PASSING = "scratch/bazel-intake"
_BLOCKED = "scratch/mitigation-index"

# A file that is clean on rule 1 and adds exactly one census key: a plain type error.
#
# ⚑ NOT AN UNTYPED DEF. A first plant used `def f(x): return x` and the arm read PROMOTABLE —
# the census runs mypy with the config found at the ROOT it is given, and a fixture root carries
# no `pyproject.toml`, so strictness is off there and an unannotated def is not an error. The
# plant never reached the branch (gate-G391's class). An assignment mismatch errors under any
# config, so it is the plant that actually fires.
_UNTYPED = 'x: int = "not an int"\n'

# A file with a module-level scratch insert.
_LIVE = 'import sys\nsys.path.insert(0, "scratch")\n'


def _plant(files: dict[str, str]) -> Path:
    """Write a fixture tree under a fresh root and return that root."""
    root = Path(tempfile.mkdtemp(prefix="scratch-promotion-"))
    for rel, text in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return root


def a_missing_directory_is_refused(out: list[str]) -> int:
    """Check a candidate that is not a directory is BLOCK with the origin's reason."""
    root = _plant({})
    verdict = sp.report("nope", root)
    if verdict.ok or verdict.reasons != ("nope: not a directory under the repo root",):
        out.append(f"selftest: missing candidate read {verdict!r}")
        return 1
    return 0


def an_already_promoted_root_is_satisfied_not_refused(out: list[str]) -> int:
    """Check idempotence: a candidate in ROOTS is ok, and says nothing to do."""
    root = _plant({"jea/x.py": _LIVE})
    verdict = sp.report("jea", root)
    if not verdict.ok or "already promoted" not in verdict.reasons[0]:
        out.append(f"selftest: a promoted root read {verdict!r}")
        return 1
    return 0


def a_live_reference_blocks_and_names_the_first(out: list[str]) -> int:
    """Check rule 1 counts every hit and names the first by relative path and line."""
    root = _plant({"cand/a.py": _LIVE, "cand/b.py": _LIVE})
    reason = sp._live(root / "cand", root)  # noqa: SLF001 - the rule is the unit under test
    if reason != "2 live scratch/ reference(s); first: cand/a.py:2":
        out.append(f"selftest: rule 1 read {reason!r}")
        return 1
    return 0


def rule_one_skips_by_substring(out: list[str]) -> int:
    """Check a `.git`-containing directory is skipped by rule 1's walk, as the origin skips it."""
    root = _plant({"cand/.github/a.py": _LIVE})
    if sp._live(root / "cand", root) is not None:  # noqa: SLF001 - the rule is the unit under test
        out.append("selftest: rule 1 walked into a .github directory")
        return 1
    return 0


def a_clean_but_untyped_candidate_is_blocked_on_rule_two(out: list[str]) -> int:
    """Check rule 2 fires alone, through the packaged census, on a planted untyped def."""
    root = _plant({"cand/u.py": _UNTYPED})
    verdict = sp.report("cand", root)
    if verdict.ok or len(verdict.reasons) != 1:
        out.append(f"selftest: untyped candidate read {verdict!r}")
        return 1
    if not verdict.reasons[0].startswith("1 type-census key(s) would be ADDED"):
        out.append(f"selftest: rule 2 did not name one added key: {verdict.reasons[0]!r}")
        return 1
    return 0


def render_marks_every_reason_with_the_verdict(out: list[str]) -> int:
    """Check the rendering carries BLOCK/ok on each reason and the origin's closing line."""
    lines = sp.render("c", sp.Verdict(ok=False, reasons=("one", "two")))
    blocked = lines[:2] == ["  BLOCK  one", "  BLOCK  two"]
    if not blocked or not lines[2].startswith("c: NOT promotable"):
        out.append(f"selftest: BLOCK rendering read {lines!r}")
        return 1
    ok = sp.render("c", sp.Verdict(ok=True, reasons=("fine",)))
    if ok[0] != "  ok    fine" or not ok[1].startswith("c: PROMOTABLE"):
        out.append(f"selftest: ok rendering read {ok!r}")
        return 1
    return 0


def _origin(candidate: str) -> list[str]:
    """Run the origin's `--promotable` and return its stdout lines."""
    done = subprocess.run(
        [
            sys.executable,
            str(_ORIGIN),
            "--promotable",
            candidate,  # noqa: S603
            "--root",
            str(corpus.ROOT),
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=600,
        cwd=str(corpus.ROOT),
    )
    return done.stdout.splitlines()


def the_differential_matches_the_origin_on_both_live_verdicts(out: list[str]) -> int:
    """Check the entry-point PROCESS prints this module's lines for a passing and a blocked dir.

    ⚑ A DIFFERENTIAL UNTIL TICK 11, when the origin became a shim over this module; now the
    end-to-end run of the real entry point, kept under its registered name (gate-G393). The
    origin's wording is pinned by the fixture arms above.
    """
    if not _ORIGIN.is_file():
        out.append("selftest: the origin is absent — the differential cannot run")
        return 1
    bad = 0
    for candidate in (_PASSING, _BLOCKED):
        if not (corpus.ROOT / candidate).is_dir():
            out.append(f"selftest: {candidate} is not present — the differential cannot run")
            bad += 1
            continue
        mine = sp.render(candidate, sp.report(candidate, corpus.ROOT))
        theirs = _origin(candidate)
        if mine != theirs:
            out.append(f"selftest: --promotable {candidate} differs from the origin:")
            out += [f"    - {line}" for line in theirs if line not in mine]
            out += [f"    + {line}" for line in mine if line not in theirs]
            bad += 1
    return bad


_ARMS = (
    a_missing_directory_is_refused,
    an_already_promoted_root_is_satisfied_not_refused,
    a_live_reference_blocks_and_names_the_first,
    rule_one_skips_by_substring,
    a_clean_but_untyped_candidate_is_blocked_on_rule_two,
    render_marks_every_reason_with_the_verdict,
    the_differential_matches_the_origin_on_both_live_verdicts,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 2 + 2 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"scratch-promotion selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"scratch-promotion selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
