# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.climode` — and they are DIFFERENTIAL against the origin.

⚑⚑⚑ FOURTEEN CONSUMERS DEPEND ON THIS MODULE, SO A PROMOTION THAT CHANGES BEHAVIOUR IS A REWRITE
WEARING A MOVE'S CLOTHES. `scripts/climode.py` stays in place and every case below runs BOTH
implementations over the same input, asserting they agree. The origin is loaded by PATH rather than
imported, because importing it by leaf name is exactly the `sys.path` surgery this promotion exists
to remove — and a differential test that required the defect would be self-defeating.

⚑⚑ THE ORIGIN IS READ THROUGH A PROTOCOL, AND THAT IS STRICTER THAN A MODULE TYPE. A dynamically
loaded module is `Any`, so every read off it type-checks against nothing and a misspelled attribute
would pass the strict bar — which makes a differential test worthless, since it would agree with
anything. `_Origin` names EXACTLY the three members these cases read, so the comparison is against a
declared surface rather than an unchecked one.

⚑⚑ THE PROPERTY CASES ARE NOT REDUNDANT WITH THE DIFFERENTIAL ONES. A differential case proves the
two agree; it cannot prove they are both RIGHT. `mutates` being derived, `POSITIONAL` being keyed
apart from the flags, and `split_flag` keeping the operand spelling verbatim are the invariants the
source docstrings name as load-bearing, so they are asserted directly.

⚑ AND THE DATACLASS CONVERSION IS THE ONE DELIBERATE DIFFERENCE. The origin uses `__slots__` and a
hand-written `__init__`; this uses a frozen slotted dataclass, which adds equality and immutability
the origin lacked. Neither is exercised by any consumer — the cases assert the SHARED surface, and
this note records what was intentionally not preserved.
"""

from __future__ import annotations

import importlib.util
from typing import Protocol, cast

from substrate import climode, corpus

# Where the module this one was promoted from still lives.
_ORIGIN = corpus.ROOT / "scripts" / "climode.py"


class _Origin(Protocol):
    """The surface of `scripts/climode.py` these cases read — and nothing else.

    ⚑ A PROTOCOL IS THE HONEST DECLARATION HERE, and mypy's own refusal named it: a module is not a
    type. Listing the three members read makes the differential's reach explicit, so a case that
    later reaches for a fourth is a type error rather than a silent `Any` read.
    """

    POSITIONAL: str

    def split_flag(self, spelling: str) -> tuple[str, str | None]: ...

    def from_pairs(self, pairs: object) -> dict[str, climode.Mode]: ...


def _origin() -> _Origin | None:
    """Load `scripts/climode.py` by PATH, or None when it is gone.

    ⚑ BY PATH, NEVER BY NAME. Importing it as `climode` needs the `sys.path` insert this promotion
    removes, so the differential check would depend on the defect it is verifying the fix for.

    ⚑ AND ITS ABSENCE IS NOT A FAILURE. Once the origin is retired the differential cases have
    nothing to compare against and are SKIPPED rather than failed — a test that goes red when its
    baseline is deliberately deleted would punish finishing the job.
    """
    if not _ORIGIN.exists():
        return None
    spec = importlib.util.spec_from_file_location("_climode_origin", _ORIGIN)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return cast("_Origin", module)


# The spellings both implementations are differenced over. ⚑ EACH IS A SHAPE THE ORIGIN'S OWN
# DOCSTRING NAMES: a bare flag, a flag with a named operand, one with a bracketed optional, one
# with an alternation, and the positional entry that must be keyed apart.
_SPELLINGS = (
    "--census",
    "--core PATH",
    "--sample REL [N]",
    "--fixpoint {--dry-run|--apply}",
    "  --padded  ",
    "path/to/thing",
)


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── `mutates` is derived, in both directions ─────────────────────────────
    # ⚑ THE INVARIANT EVERY DERIVED ROSTER RESTS ON. If it were ever a stored peer field it could
    # disagree with `writes`, and every consumer deriving a write set would split silently.
    check(
        "a mode declaring an artifact kind mutates", passed=climode.Mode(writes=(".bib",)).mutates
    )
    check("and one declaring none does not", passed=not climode.Mode(writes=()).mutates)
    check("the default mode is a pure read", passed=not climode.Mode().mutates)
    check(
        "mutates tracks writes rather than being set beside it",
        passed=climode.Mode(writes=(".py", "store")).mutates
        and climode.Mode(writes=()).mutates is False,
    )

    # ── the declared fields keep their defaults ──────────────────────────────
    # ⚑ THE DEFAULTS ARE CLAIMS THE GATE HOLDS A TOOL TO — `scans=False` asserts the verdict does
    # not rest on a scan. A default that drifted would silently retract every roster's contract.
    bare = climode.Mode()
    check("a bare mode is nullary", passed=bare.operand is None)
    check("takes no paths by default", passed=not bare.paths)
    check("claims no scan contract by default", passed=not bare.scans)
    check("and declares no writes by default", passed=bare.writes == ())

    # ── split_flag keeps the operand spelling VERBATIM ───────────────────────
    # ⚑⚑ NORMALISING WOULD BE A SECOND AUTHORITY over what the dispatch accepts. The spelling is
    # what a reader needs, brackets and alternations included.
    check("a bare flag has no operand", passed=climode.split_flag("--census") == ("--census", None))
    check("a named operand is kept", passed=climode.split_flag("--core PATH") == ("--core", "PATH"))
    check(
        "a bracketed optional is kept verbatim",
        passed=climode.split_flag("--sample REL [N]") == ("--sample", "REL [N]"),
    )
    check(
        "an alternation is kept verbatim",
        passed=climode.split_flag("--fixpoint {--dry-run|--apply}")
        == ("--fixpoint", "{--dry-run|--apply}"),
    )
    check(
        "surrounding whitespace is stripped",
        passed=climode.split_flag("  --padded  ") == ("--padded", None),
    )

    # ── the positional entry is keyed APART from the flags ───────────────────
    # ⚑ A ROSTER STORING IT AS A FLAG would compare a bare operand spelling against a `-`-prefixed
    # token and silently never fire.
    lifted = climode.from_pairs([("--core PATH", "read a core"), ("file.py", "the positional")])
    check(
        "a flag pair lifts under its flag",
        passed="--core" in lifted and lifted["--core"].operand == "PATH",
    )
    check("a positional pair is keyed apart", passed=climode.POSITIONAL in lifted)
    check(
        "...and the positional key is not flag-shaped",
        passed=not climode.POSITIONAL.startswith("-"),
    )
    check("...and it takes paths", passed=lifted[climode.POSITIONAL].paths)
    check("a lifted pair carries its gloss", passed=lifted["--core"].why == "read a core")
    check("and a lifted pair claims no writes", passed=not lifted["--core"].mutates)

    # ── DIFFERENTIAL: the promoted module agrees with the one it replaces ────
    origin = _origin()
    if origin is None:
        check("the origin is retired, so the differential cases are skipped", passed=True)
        return out

    check(
        "split_flag agrees with the origin on every shape",
        passed=all(climode.split_flag(s) == origin.split_flag(s) for s in _SPELLINGS),
    )

    pairs = [(s, f"gloss for {s}") for s in _SPELLINGS]
    mine = climode.from_pairs(pairs)
    theirs = origin.from_pairs(pairs)
    check("from_pairs produces the same keys", passed=sorted(mine) == sorted(theirs))
    check(
        "...with the same operands", passed=all(mine[k].operand == theirs[k].operand for k in mine)
    )
    check("...the same paths flags", passed=all(mine[k].paths == theirs[k].paths for k in mine))
    check("...the same glosses", passed=all(mine[k].why == theirs[k].why for k in mine))
    check(
        "...and the same mutates verdict",
        passed=all(mine[k].mutates == theirs[k].mutates for k in mine),
    )
    check(
        "the positional key is spelled identically", passed=climode.POSITIONAL == origin.POSITIONAL
    )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"climode selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
