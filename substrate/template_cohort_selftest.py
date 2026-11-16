# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.template_cohort` — which files are one template.

⚑⚑⚑ BOTH ERROR DIRECTIONS MATTER AND THEY COST DIFFERENTLY. Grouping files that are NOT one
template understates the work and licenses a batch fix that breaks something; failing to group
files that ARE one overstates it and sends an operator at nine copies of one decision. The
cases pin both, with the false-grouping direction weighted more heavily because its failure is
silent — a batch fix looks like it worked until the odd member is exercised.

⚑⚑ THE VARYING PART IS EXACTLY THE CONSTANTS. Two instantiations differ in the strings that
were substituted, so a case must show that differing literals still group AND that a differing
STRUCTURE does not. Without the second, the reader would call every short script the same.

⚑ AND A SINGLETON IS NOT A COHORT. Reporting one-member groups would bury a real finding in
noise, which is the shape that gets a reader ignored.
"""

from __future__ import annotations

from substrate import template_cohort

_A = "import os\nx = os.path.join('alpha', 'one')\nprint('claim alpha')\n"
_B = "import os\nx = os.path.join('beta', 'two')\nprint('claim beta')\n"
_DIFFERENT = "import os\nfor i in range(3):\n    print(i)\n"
_EXTRA_STMT = "import os\nx = os.path.join('alpha', 'one')\nprint('claim alpha')\nprint('extra')\n"


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── differing CONSTANTS group; differing STRUCTURE does not ─────────────
    check(
        "two files differing only in constants share a skeleton",
        passed=template_cohort.skeleton_of(_A) == template_cohort.skeleton_of(_B),
    )
    # ⚑ THE FALSE-GROUPING GUARD. Without this the reader calls every short script the same.
    check(
        "a different control shape does NOT share it",
        passed=template_cohort.skeleton_of(_A) != template_cohort.skeleton_of(_DIFFERENT),
    )
    # ⚑ AND ONE EXTRA STATEMENT IS A DIFFERENT SKELETON — a drifted cohort member must fall
    # out rather than be swept in, since a batch fix would miss exactly that file.
    check(
        "an extra statement breaks the match",
        passed=template_cohort.skeleton_of(_A) != template_cohort.skeleton_of(_EXTRA_STMT),
    )

    # ── grouping ────────────────────────────────────────────────────────────
    found = template_cohort.cohorts({"a.py": _A, "b.py": _B, "z.py": _DIFFERENT})
    real = [c for c in found if c.is_cohort]
    check("the two twins form one cohort", passed=len(real) == 1)
    check(
        "and the cohort names both members",
        passed=bool(real) and real[0].members == ("a.py", "b.py"),
    )
    # ⚑ A SINGLETON IS REPORTED AS NOT-A-COHORT rather than omitted, so a caller can count
    # its whole input without a second pass.
    singles = [c for c in found if not c.is_cohort]
    check("the odd file stands alone", passed=len(singles) == 1 and singles[0].members == ("z.py",))

    # ── ordering is largest-first and stable ────────────────────────────────
    many = template_cohort.cohorts(
        {"a.py": _A, "b.py": _B, "c.py": _B, "y.py": _DIFFERENT, "z.py": _DIFFERENT}
    )
    check("the larger cohort leads", passed=many[0].size == 3)  # noqa: PLR2004
    # ⚑ STABLE ACROSS INPUT ORDER, or two runs over an unchanged tree disagree and a diff
    # of two reports shows churn rather than movement.
    reordered = template_cohort.cohorts(
        {"z.py": _DIFFERENT, "c.py": _B, "y.py": _DIFFERENT, "b.py": _B, "a.py": _A}
    )
    check(
        "and the ordering does not depend on input order",
        passed=[c.members for c in many] == [c.members for c in reordered],
    )

    # ── a file that does not parse is omitted, not grouped ─────────────────
    # ⚑ SKELETON `None` MUST NOT BECOME A GROUP KEY, or every unparseable file would join
    # one large phantom cohort.
    check(
        "an unparseable file yields no skeleton",
        passed=template_cohort.skeleton_of("def (\n") is None,
    )
    broken = template_cohort.cohorts({"a.py": _A, "bad.py": "def (\n"})
    check("and is omitted from the grouping", passed=all("bad.py" not in c.members for c in broken))

    # ── the rendering states the planning consequence ──────────────────────
    text = template_cohort.render(found)
    check("the rendering names a cohort member", passed="a.py" in text)
    # ⚑ THE WHOLE POINT: a per-file count over a cohort overstates the work.
    check("and says a per-file count overstates the work", passed="overstates" in text)

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
