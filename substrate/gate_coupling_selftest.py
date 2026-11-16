# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.gate_coupling` — the hook's git-coupling reader.

⚑ THE LOAD-BEARING CASE IS EITHER-QUOTING. The hook writes its trigger patterns in single
quotes, and a double-quote-only reader matches nothing while rendering as "no conditional
gates" — a clean-looking answer asserting the opposite of the truth. That defect was
measured in the census this reader forks from, so it is pinned here rather than trusted.

⚑⚑ AND A COMMENTED-OUT git LINE MUST NOT COUNT. The hook carries prose about git in its
own comments, and a reader that matched them would report coupling the hook does not have
— inflating the very partition that decides what can become a build target.

⚑ THE FIXTURES ARE HOOK-SHAPED TEXT, NOT THE LIVE HOOK. A case reading the real file would
change verdict whenever the hook changes, which makes it a measurement rather than a case:
it could not fail for the reason it was written.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from substrate import gate_coupling

_HOOK = """\
#!/usr/bin/env bash
# This comment mentions git diff and must not be counted.
STAGED="$(git rev-parse --absolute-git-dir)/staged"
git checkout-index --all --prefix="$STAGED/"

if git diff --cached --name-only | grep -qE '^jea/metalanguage/'; then
  run "sigma regression" "$ROOT/scripts/check_sigma.py"
fi

if git diff --cached --name-only | grep -qE "^scratch/"; then
  run "scratch gate" "$ROOT/scripts/check_scratch.py"
fi

echo "no git here"
"""

TRIGGERS_IN_FIXTURE = 2
GIT_LINES_IN_FIXTURE = 4


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    with tempfile.TemporaryDirectory() as tmp:
        hook = Path(tmp) / "pre-commit"
        hook.write_text(_HOOK, encoding="utf-8")

        pats = gate_coupling.triggers(hook)
        rows = gate_coupling.couplings(hook)
        text = gate_coupling.render(hook)

    # ── EITHER QUOTING — the measured defect this reader forks around ────────
    check("a single-quoted trigger is found", passed="^jea/metalanguage/" in pats)
    check("a double-quoted trigger is found too", passed="^scratch/" in pats)
    check(
        "and both, so neither quoting is silently dropped", passed=len(pats) == TRIGGERS_IN_FIXTURE
    )

    # ── comments are not coupling ────────────────────────────────────────────
    # ⚑ The fixture's comment names `git diff`; counting it would inflate the partition
    # that decides what can become a build target.
    check(
        "a commented git line is not counted",
        passed=all("must not be counted" not in r.text for r in rows),
    )
    check("only the real git lines are counted", passed=len(rows) == GIT_LINES_IN_FIXTURE)

    # ── the two kinds ────────────────────────────────────────────────────────
    kinds = {r.kind for r in rows}
    check(
        "both couplings are represented",
        passed=kinds == {gate_coupling.TRIGGERED, gate_coupling.READS_GIT},
    )
    triggered = [r for r in rows if r.kind == gate_coupling.TRIGGERED]
    check("a staged-path line reads as TRIGGERED", passed=len(triggered) == TRIGGERS_IN_FIXTURE)
    check(
        "a bare git invocation reads as READS_GIT",
        passed=any(r.kind == gate_coupling.READS_GIT and "checkout-index" in r.text for r in rows),
    )

    # ⚑ A line invoking no script keeps a NULL script rather than being dropped: the
    # hook's own git work is the residue that cannot become a build target.
    check(
        "a hook-owned git line is kept with a null script",
        passed=any(r.script is None for r in rows),
    )

    # ── the render states its own scope ──────────────────────────────────────
    check("the render reports the trigger count", passed="2 staged-path trigger(s)" in text)
    check("and names its own blind spot", passed="a fact about this reader, not an absence" in text)
    check(
        "and warns that a triggered gate may still be portable",
        passed="PORTABLE BEHIND A NON-PORTABLE DISPATCH" in text,
    )

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


if __name__ == "__main__":
    raise SystemExit(0 if selftest() else 1)
