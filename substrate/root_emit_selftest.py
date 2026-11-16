# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.root_emit` — the committed root IS the parameterized render.

⚑⚑ THE FAITHFUL DIFFERENTIAL IS RETIRED, DELIBERATELY (t118). Until the build flipped, the faithful
render was held byte-for-byte against `agda/Makefile` as the ORIGIN generator wrote it — last green
8/8 on t117, run against the real origin just before the shim replaced it. The build now commits the
TENANT-AWARE render, so the artefact case compares that render to the file, and the faithful mode
is held only to differing from it by exactly the lines the parameterization declares.
"""

from __future__ import annotations

import sys

from substrate import corpus, root_emit

ROOT_MK = corpus.ROOT / "agda" / "Makefile"


def _first_difference(got: str, want: str) -> str:
    """Name the first line where two renderings differ, or their length difference."""
    a, b = got.split("\n"), want.split("\n")
    for i, (x, y) in enumerate(zip(a, b, strict=False)):
        if x != y:
            return f"line {i + 1}:\n    render: {x[:160]!r}\n    file:   {y[:160]!r}"
    return f"lengths differ: render {len(a)} lines, file {len(b)} lines"


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    faithful = root_emit.text()
    param = root_emit.text(parameterized=True)
    want = ROOT_MK.read_text(encoding="utf-8")
    same = param in {want, want.rstrip("\n")}
    if not same:
        sys.stdout.write(f"  DIFF {_first_difference(param, want)}\n")
    was, now = set(faithful.split("\n")), set(param.split("\n"))
    added, removed = now - was, was - now
    return [
        ("the committed agda/Makefile IS the parameterized render", same),
        (
            "parameterizing adds only tenant, python, catalog and venv-check lines",
            all(("TENANT" in x) or ("PYTHON" in x) or ("catalog" in x) for x in added),
        ),
        (
            "parameterizing removes only the two bare-python3 lines",
            removed == {root_emit.CATALOG_FAITHFUL, root_emit.CHECK_MAKEFILES_FAITHFUL},
        ),
        ("the tenant guard is emitted", "$(error TENANT must be live or sandbox)" in param),
        ("TENANT is exported so Flat.mk sub-makes inherit it", "export TENANT" in param),
        (
            "the venv python is absolute, via make's abspath",
            "PYTHON := $(abspath ../.venv/bin/python)" in param,
        ),
        ("no recipe names a relative ../.venv", "../.venv/bin/python " not in param),
        ("catalog no longer runs bare python3", "-- python3 ../scripts/sppf_db.py" not in param),
        (
            "check-makefiles checks the parameterized render on the venv",
            root_emit.CHECK_MAKEFILES_VENV in param,
        ),
    ]


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"root-emit selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(0 if ("--selftest" in sys.argv or len(sys.argv) == 1) and selftest() else 1)
