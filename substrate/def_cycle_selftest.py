# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.def_cycle` — file cycle, def cycle, or co-location.

⚑⚑⚑ THE VERDICT LICENSES AN ACTION, so a wrong one is a wrong edit. Calling a genuine loop an
artifact sends an operator to extract something that cannot be extracted; calling an artifact a
loop sends them to CUT a dependency somebody genuinely has. Both are pinned, and so is the
third case the first cut got wrong — a pair with no backward edges is NOT MUTUAL, and
classifying it as an artifact produced a lift recommendation naming nothing.

⚑⚑ AND A REPORTED DEF-LEVEL LOOP IS A DEFECT IN THE READER, NOT A VERDICT ABOUT THE CODE. A
module-scope def cycle cannot execute — Python evaluates top to bottom, so the second
definition would reference an unbound name. The case therefore asserts the verdict is called
SUSPECT rather than treated as a legitimate finding about the program.

⚑ THE FIXTURES ARE REAL FILES, because the reader parses paths rather than sources. They are
written into the repo and removed, since a fixture left on disk becomes a file some other
census counts.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from substrate import corpus, def_cycle

_DIR = "_defcycle_fixture"

# Two one-way chains: mutual at FILE level, acyclic at DEF level.
_A_ARTIFACT = "def helper():\n    return 1\n\n\ndef selftest():\n    return other()\n"
_B_ARTIFACT = "def other():\n    return helper()\n"

# A genuine mutual reach — cannot execute at module scope, so SUSPECT.
_A_LOOP = "def ping():\n    return pong()\n"
_B_LOOP = "def pong():\n    return ping()\n"

# One direction only.
_A_ONEWAY = "def caller():\n    return callee()\n"
_B_ONEWAY = "def callee():\n    return 1\n"


def _write(name: str, text: str) -> str:
    """Write one fixture file and return its repo-relative path."""
    base = corpus.ROOT / _DIR
    base.mkdir(exist_ok=True)
    (base / name).write_text(text, encoding="utf-8")
    return f"{_DIR}/{name}"


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    try:
        # ── the artifact: mutual at file level, a chain at def level ─────────
        a = _write("a_art.py", _A_ARTIFACT)
        b = _write("b_art.py", _B_ARTIFACT)
        art = def_cycle.classify(a, b)
        check(
            "two one-way chains read as a co-location artifact",
            passed=art.kind == def_cycle.CO_LOCATION,
        )
        check("and the artifact is marked resolvable by lifting", passed=art.is_artifact)
        # ⚑ THE LIFT TARGET MUST BE NAMED, or the advice is not advice.
        check("and it names what to lift", passed=art.shared == ("helper",))

        # ── the genuine loop: SUSPECT, not a verdict about the code ─────────
        # ⚑ A MODULE-SCOPE DEF CYCLE CANNOT EXECUTE, so finding one means the READER is
        # wrong — most often call-time resolution, which is exactly this fixture.
        c = _write("a_loop.py", _A_LOOP)
        d = _write("b_loop.py", _B_LOOP)
        loop = def_cycle.classify(c, d)
        check("a mutual def reach is SUSPECT", passed=loop.kind == def_cycle.SUSPECT)
        check("and is NOT reported as an artifact", passed=not loop.is_artifact)
        check("and asks to be investigated", passed=loop.needs_investigation)

        # ── one direction only: not mutual, so nothing to lift ─────────────
        # ⚑ THE CASE THE FIRST CUT GOT WRONG. Classifying this as an artifact rendered
        # "LIFT one of: (none reached)" — advice naming nothing, which reads as a verdict.
        e = _write("a_one.py", _A_ONEWAY)
        f = _write("b_one.py", _B_ONEWAY)
        one = def_cycle.classify(e, f)
        check("a one-directional pair is NOT MUTUAL", passed=one.kind == def_cycle.NOT_MUTUAL)
        check("and is not offered as an artifact", passed=not one.is_artifact)
        # ⚑ AND ITS RENDERING SAYS THE EDGE CAME FROM SOMEWHERE UNSEEN, rather than
        # proposing an extraction with no subject.
        check(
            "and its rendering says the file edge is unexplained",
            passed="does not see" in def_cycle.render(e, f, one),
        )

        # ── the reach test sees attribute leaves ───────────────────────────
        # ⚑ A CROSS-FILE CALL IS `peer.census()`. Collecting only bare names would see the
        # receiver and miss the callee, reporting no edge exactly where the dependency is.
        g = _write("a_attr.py", "def use():\n    return peer.target()\n")
        h = _write("b_attr.py", "def target():\n    return 1\n")
        check(
            "an attribute call is seen as an edge",
            passed=def_cycle.def_edges(g, h) == [("use", "target")],
        )

        # ── an unreadable file yields no defs, rather than raising ─────────
        check(
            "an absent file yields no definitions",
            passed=def_cycle.top_level_defs("no/such/file.py") == {},
        )

        # ── top-level only: a method is not a movable unit ─────────────────
        # ⚑ A METHOD IS REACHED THROUGH ITS CLASS, so proposing to lift one would propose an
        # extraction nobody can perform without moving the class too.
        i = _write("a_meth.py", "class C:\n    def inner(self):\n        return 1\n")
        defs = def_cycle.top_level_defs(i)
        check("a class is a top-level definition", passed="C" in defs)
        check("but its method is not", passed="inner" not in defs)
    finally:
        shutil.rmtree(Path(corpus.ROOT / _DIR), ignore_errors=True)

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
