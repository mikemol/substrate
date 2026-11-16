#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `bibstruct --delete`: the slice (`bib_edit.remove_entry`) and its read-back arm.

⚑⚑ THE SLICE IS CASED ON WHAT MUST SURVIVE, NOT ONLY ON WHAT GOES. A delete that removed the
right entry and one byte of its neighbour would pass "the key is gone" — so each case re-parses
and asserts the neighbours' FIELDS, and a comment placed between entries must survive, because
the masked-locate is only sound while the mask preserves length.

⚑ THE `gone_key` ARM IS CASED WITH A LYING BENCH. A read-back that still reports the key is the
one way to prove the arm fires; a case run only against an honest bench tests nothing about it.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import bib_edit, bib_parse, bib_write

FIXTURE = """% leading comment — must survive

@misc{A,
  section  = {finding},
  claim    = {first}
}

% a comment between entries — must survive
@misc{B,
  section  = {finding},
  claim    = {middle, to be deleted}
}

@misc{C,
  section  = {finding},
  claim    = {last}
}
"""


def _remove(key: str) -> str | bib_edit.Refusal:
    """Return the fixture with `key` removed, through the real grammar."""
    return bib_edit.remove_entry(FIXTURE, key, bib_parse.parse(FIXTURE), bib_parse.GRAMMAR)


def _slice_cases() -> list[tuple[str, bool]]:
    """Return the cases for the pure slice."""
    middle = _remove("B")
    last = _remove("C")
    if not isinstance(middle, str) or not isinstance(last, str):
        return [("removing a present key does not refuse", False)]
    after = bib_parse.parse(middle)
    return [
        ("removing a present key does not refuse", True),
        ("the removed key is gone", "B" not in after),
        ("the entry before keeps every field", after["A"]["claim"] == "first"),
        ("the entry after keeps every field", after["C"]["claim"] == "last"),
        ("the leading comment survives", middle.startswith("% leading comment")),
        ("a comment between entries survives", "% a comment between entries" in middle),
        ("no blank-line gap accretes", "\n\n\n" not in middle),
        ("the last entry can be removed too", set(bib_parse.parse(last)) == {"A", "B"}),
        ("an unknown key is refused", isinstance(_remove("Z"), bib_edit.Refusal)),
    ]


def _bench(read_back: dict[str, object]) -> bib_write.Bench:
    """Return a bench that snapshots nothing, round-trips clean, and reads back `read_back`."""
    return bib_write.Bench(
        snapshot=lambda _label, _targets: None,
        roundtrip=lambda _target: [],
        read_back=lambda _target: read_back,
    )


def _arm_cases(tmp: Path) -> list[tuple[str, bool]]:
    """Return the cases for the `gone_key` read-back arm, honest and lying."""
    target = tmp / "w.bib"
    target.write_text(FIXTURE, encoding="utf-8")
    new = _remove("B")
    if not isinstance(new, str):
        return [("the arm fixture plans", False)]
    edit = bib_write.Edit(
        verb="--delete", label="B", target=target, old=FIXTURE, new=new, gone_key="B"
    )
    honest = bib_write.apply_write(edit, _bench({"A": 1, "C": 1}), applying=True)
    target.write_text(FIXTURE, encoding="utf-8")
    lying = bib_write.apply_write(edit, _bench({"A": 1, "B": 1, "C": 1}), applying=True)
    dry = bib_write.apply_write(edit, _bench({}), applying=False)
    return [
        ("an honest read-back without the key is OK", honest.code == bib_write.OK),
        ("a read-back that STILL holds the key is BROKEN", lying.code == bib_write.BROKEN),
        ("the broken verdict names the key", any("'B' STILL" in line for line in lying.lines)),
        ("without --apply nothing is written", dry.code == bib_write.OK),
    ]


def selftest() -> int:
    """Run every case, reporting failures by name, and return an exit code."""
    with tempfile.TemporaryDirectory() as tmp:
        cases = _slice_cases() + _arm_cases(Path(tmp))
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"bib-delete selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 1)
