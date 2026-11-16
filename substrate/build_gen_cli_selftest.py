# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.build_gen_cli` — refusal, `--jobs`, `--check`, driven with fakes.

⚑ THE HOOKS ARE FAKES WHERE A REAL ONE WOULD WRITE: the snapshot and census record their calls,
and no case runs the bare regenerate against the real `agda/`. The graph is the origin's real one,
because `--check` against the working tree is only meaningful over the real graph.
"""

from __future__ import annotations

import contextlib
import io
import sys
from typing import TYPE_CHECKING

from substrate import build_gen_cli as cli
from substrate import flat_origin

if TYPE_CHECKING:
    from pathlib import Path

_USAGE = 2


def _hooks(calls: list[str]) -> cli.Hooks:
    """Return hooks whose writes are recorded, never performed; the graph is the origin's."""
    origin = flat_origin.load()

    def snapshot(path: Path) -> None:
        calls.append(f"snapshot {path.name}")

    def census(sync: bool) -> int:  # noqa: FBT001 - the injected signature
        calls.append(f"census sync={sync}")
        return 0

    return cli.Hooks(graph=lambda: flat_origin.graph(origin), snapshot=snapshot, census=census)


def _run(argv: list[str], hooks: cli.Hooks) -> tuple[int, str]:
    """Run the CLI capturing stdout."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = cli.main(argv, hooks)
    return code, out.getvalue()


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    calls: list[str] = []
    hooks = _hooks(calls)
    code_bad, out_bad = _run(["--chek"], hooks)
    code_jobs, out_jobs = _run(["--jobs"], hooks)
    # ⚑ THE COMMITTED MAKEFILES ARE THE PARAMETERIZED RENDERS (the tenant-aware build, 2026-09-23),
    # and pre-commit checks them with `--check --parameterized`; this case asks the same question.
    code_check, out_check = _run(["--check", "--parameterized"], hooks)
    code_census, _ = _run(["--check-census"], hooks)
    return [
        ("an unknown flag is refused, not read as regenerate", code_bad == _USAGE),
        ("and it wrote nothing", out_bad == "" and not any("snapshot" in c for c in calls)),
        ("--jobs exits 0", code_jobs == 0),
        ("--jobs prints ONLY the number", out_jobs.strip().isdigit()),
        ("--check --parameterized passes on the committed makefiles", code_check == 0),
        ("--check says OK", "OK" in out_check),
        ("--selftest is a known flag, not refused", "--selftest" in cli.FLAGS),
        (
            "--check-census hands off to the census hook",
            code_census == 0 and "census sync=False" in calls,
        ),
        ("no case armed a snapshot (nothing was written)", not any("snapshot" in c for c in calls)),
    ]


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"build-gen-cli selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(0 if ("--selftest" in sys.argv or len(sys.argv) == 1) and selftest() else 1)
