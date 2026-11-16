#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Exercise `ratchet_core` end to end, asserting the decomposition still ratchets.

⚑⚑ THE SELFTEST IS ITS OWN MODULE, WHICH IS THE SAME LESSON ONE LAYER OUT. The original
`_selftest` was 139 statements inside `ratchet.py` — a `PLR0915` finding that was really
saying "the cases and the code under test are sharing a file". Keeping them together is
what made the module too large to author cleanly; separating them means neither has to
carry the other's size.

⚑ AND IT IS THE FIRST THING THAT RUNS THE EXTRACTED MODULES TOGETHER. Each was verified
alone; alone is not composed. `baseline_io` round-trips, `ratchet_render` formats and
`ratchet_core` rules — but nothing had yet asserted that a census handed in one end comes
out the other as the right verdict.
"""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
from pathlib import Path

from mikemol.ratchet import render

from substrate.baseline_io import WRITE_SWITCH, write_baseline
from substrate.ratchet_core import Census, Permission, mint, partition, set_ratchet

_QUIET = render.Report(quiet=True)


def _perm(*, write: bool) -> Permission:
    """Build a permission that never consults argv — a test states its own intent."""
    return Permission.resolve([], write=write, dry_run=False)


def _run(tmp: Path, keys: set[str], base: set[str] | None, *, write: bool) -> tuple[int, set[str]]:
    """Ratchet `keys` against `base`, returning (exit code, baseline on disk)."""
    tmp.mkdir(parents=True, exist_ok=True)
    path = tmp / "baseline.txt"
    if base is not None:
        write_baseline(str(path), base)
    code = set_ratchet(Census.of(keys, str(path), "probe"), _QUIET, _perm(write=write))
    on_disk = (
        set()
        if not path.exists()
        else {ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()}
    )
    return code, on_disk


def _would_mint(tmp: Path, report: render.Report) -> str:
    """Return what a read-only run prints for a baseline that does not exist yet."""
    census = Census.of({"a"}, str(tmp / "absent.txt"), "probe")
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        mint(census, render.Voice(label="probe", report=report), _perm(write=False))
    return out.getvalue()


def selftest() -> int:
    """Pin the four ratchet verdicts, composed across every extracted module."""
    cases: list[tuple[str, bool, str]] = []

    def equals(label: str, got: object, want: object) -> None:
        cases.append((label, got == want, f"{got!r} != {want!r}"))

    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)

        # ⚑ FROZEN: an unchanged census passes and leaves the baseline alone.
        equals(
            "an unchanged census passes",
            _run(tmp / "a", {"a", "b"}, {"a", "b"}, write=True),
            (0, {"a", "b"}),
        )

        # ⚑⚑ GROWTH REFUSES. This is the whole point of the gate, and the arm that would
        # matter most if the decomposition had inverted `cur` and `base` — both are
        # `set[str]`, and swapping them turns paydown into growth silently.
        equals("a NEW key refuses", _run(tmp / "b", {"a", "b"}, {"a"}, write=True)[0], 1)

        # ⚑ AND A REFUSAL MUST NOT BANK. If growth wrote the baseline, the offending key
        # would be grandfathered by the very run that reported it.
        equals(
            "...and does not record the addition",
            _run(tmp / "c", {"a", "b"}, {"a"}, write=True)[1],
            {"a"},
        )

        # ⚑ PAYDOWN AUTO-LOWERS when permitted, and does NOT when it is not — the
        # read-mutates-state defect measured twice (`--quiet` rewrote a baseline 48->45).
        equals(
            "paydown lowers the baseline when permitted",
            _run(tmp / "d", {"a"}, {"a", "b"}, write=True),
            (0, {"a"}),
        )
        equals(
            "...and a read-only run banks NOTHING",
            _run(tmp / "e", {"a"}, {"a", "b"}, write=False),
            (0, {"a", "b"}),
        )

        # ⚑ MINTING an absent baseline is opt-in, and verifies its own round-trip.
        equals(
            "an absent baseline is minted when permitted",
            _run(tmp / "f", {"a", "b"}, None, write=True),
            (0, {"a", "b"}),
        )

        # ⚑⚑ THE BYPASS WARNING NAMES THIS REPO'S SWITCH. mtools' default text does not (its
        # package has no such switch), so a would-mint run that fell through to the default
        # would warn about a bypass without naming what bypasses — the regression the move
        # onto `mikemol.ratchet.render` would otherwise have shipped silently.
        equals(
            "a would-mint run names the write switch",
            got=WRITE_SWITCH in _would_mint(tmp, _QUIET),
            want=True,
        )
        # ⚑ THE CONTROL: a gate that supplies its own wording keeps it, so the default is a
        # fallback rather than an override.
        own = render.Report(quiet=True, mint_bypass="  a gate's own wording")
        equals(
            "...and a gate's own mint_bypass is kept",
            got="a gate's own wording" in _would_mint(tmp, own),
            want=True,
        )

    # ⚑ A MOVE IS NEITHER PAYDOWN NOR GROWTH, so a decomposition cannot launder debt
    # through the relocation channel, and cannot be refused for relabelling it either.
    diff = partition({"b.agda::X"}, {"a.agda::X"}, lambda k: k.split("::")[1])
    equals(
        "a 1:1 relocation is neither added nor paid",
        (diff.added, diff.paid, len(diff.moved)),
        (set(), set(), 1),
    )

    failed = [(n, d) for n, good, d in cases if not good]
    for n, d in failed:
        sys.stderr.write(f"  FAIL {n}: {d}\n")
    sys.stdout.write(f"ratchet_core selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE — see `baseline_io`'s
# note (⟡selftest-discovery): ten promoted modules ran correctly and were invisible to the
# runner, because discovery keys on the literal `--selftest` appearing in the file.
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
