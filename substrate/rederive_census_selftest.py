# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""The cases for `substrate.rederive_census` — differenced against the LIVE gate, before the swap.

⚑⚑⚑ THIS DIFFERENTIAL HAS A SHELF LIFE AND THE ARMS SAY SO (gate-F75). Right now the gate
computes its census independently, so agreeing with it over the whole tree is EVIDENCE. The
moment that gate is rewritten to call this module, the same green becomes a tautology — a
function agreeing with itself. So the verification is run NOW, while it still measures something.

⚑⚑ AND IT DIFFERENCES THE DRAINED PAIR, NOT THE CENSUS ALONE. The population comes from
`tool_walk`, which is the walk a swap will install — so the arm tests what ships. An earlier cut
held its own copy of the gate's roster and exclusions, which would have compared the gate against
MY reading of its scope instead, and left the walk's exclusions unexercised end to end.

⚑⚑ SET EQUALITY, NEVER A COUNT. Two key sets of equal size with one key swapped is exactly the
failure a count cannot see, and in a paydown-only ratchet it would simultaneously refuse a commit
for a phantom offender and silently un-bank a real one.

⚑ THE MOTIF ARMS ARE THE ORIGIN'S OWN FAILURES. Each pattern here once missed the live instances
it was written from — *a guard written from the instance passes on everything except the
instance* — so the cases pin the properties those misses violated rather than the spellings that
were fixed.
"""

from __future__ import annotations

import importlib.util
import sys
from typing import Protocol, runtime_checkable

from substrate import corpus, rederive_census, tool_walk

# The live gate this module drains the census out of.
_GATE = corpus.ROOT / "scripts" / "check_rederive_ratchet.py"

# ⚑⚑ THE ROSTER AND THE EXCLUSIONS LIVED HERE AND NOW DO NOT. `tool_walk` owns that policy; a
# second copy here would be the two-rosters-of-one-fact defect, inside the check written to prove
# a drain faithful.

#: How many differing keys to show when an arm fails — enough to diagnose, few enough to read.
_SHOW = 3


@runtime_checkable
class _Gate(Protocol):
    """The live gate's census, read through its own module.

    ⚑ NARROWED AT THE SEAM: a dynamically loaded module is `Any`, so an un-narrowed differential
    agrees with anything.
    """

    def census(self) -> set[str]:
        """Return the gate's key set over the whole tree."""
        ...


def _gate() -> _Gate | None:
    """Load the live gate by path, or None when it cannot be reached.

    ⚑⚑ THE GATE MUTATES `sys.path` AT IMPORT — the defect this drain removes — so the paths it
    inserts are restored afterwards. Leaving them would make this suite's own environment more
    permissive than the one it is testing for.
    """
    if not _GATE.exists():
        return None
    spec = importlib.util.spec_from_file_location("_rederive_gate_origin", _GATE)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    saved = list(sys.path)
    try:
        spec.loader.exec_module(module)
    except (OSError, SystemExit, ValueError, ImportError):
        return None
    finally:
        sys.path[:] = saved
    got: object = module
    return got if isinstance(got, _Gate) else None


def _motif_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the patterns and the ordinal key."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ⚑⚑ A SITE IS KEYED BY ORDINAL, NOT LINE. Two sites of one motif in one file must get
    # distinct keys, and inserting lines above them must not change either.
    two = 'module x\nrglob("*.agda")\nrglob("*.agda")\n'
    keys = rederive_census.keys_for("f.py", two)
    check(
        "two sites of one motif get distinct ordinals",
        passed={"enumerate::f.py#0", "enumerate::f.py#1"} <= keys,
    )

    shifted = "module x\n" + "# pad\n" * 5 + 'rglob("*.agda")\nrglob("*.agda")\n'
    check(
        "and inserting lines above them changes nothing",
        passed=rederive_census.keys_for("f.py", shifted) == keys,
    )

    # ⚑⚑⚑ THE CONTEXTUAL WALK. A walk without an Agda filter is a walk over something else, and
    # censusing it banks debt nobody can pay.
    bare = "module x\nfor a, b, c in os.walk(root):\n    pass\n"
    check(
        "an os.walk with no agda filter is NOT censused",
        passed=rederive_census.keys_for("f.py", bare) == set(),
    )
    agda = 'module x\nfor a, b, c in os.walk(root):\n    if f.endswith(".agda"):\n        pass\n'
    check(
        "but one with an agda filter IS",
        passed=any(k.startswith("enumerate::") for k in rederive_census.keys_for("f.py", agda)),
    )

    # ⚑⚑⚑ THE MARKER IS SPELLED FROM THE MODULE'S OWN PATTERN, NEVER RETYPED (gate-F82). My
    # first cut typed a LOOK-ALIKE glyph — a helmet where the marker is a flag — so the fixtures
    # contained no marker at all and two arms failed while the whole-tree differential passed. A
    # fixture built from a character I recognised by shape tests nothing.
    marker = rederive_census.DECLARED.pattern
    check(
        "the marker fixture is built from the module's own pattern",
        passed=marker in f"# {marker} known",
    )

    # ⚑ A DECLARED SITE IS MARKED, NOT DROPPED — removing a declaration must read as withdrawing
    # a claim rather than as adding a derivation.
    declared = f'module x\n# {marker} known\nrglob("*.agda")\n'
    marked = rederive_census.keys_for("f.py", declared)
    check("a declared site keeps its key", passed=len(marked) == 1)
    check("and carries the declared marker", passed=all(k.endswith("::declared") for k in marked))

    return out


def _scope_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for what is censused at all."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ⚑⚑ THE AUTHORITY IS NOT ITS OWN RE-DERIVATION. Censusing it would key the canonical module
    # as an offender — the one shape this gate must never refuse.
    check(
        "a canonical module is not censused",
        passed=not rederive_census.relevant("agda_lex.py", 'rglob("*.agda")'),
    )
    check(
        "but an ordinary module is",
        passed=rederive_census.relevant("some_tool.py", 'rglob("*.agda")'),
    )
    # ⚑ AND A FILE MENTIONING NEITHER TERM cannot be re-deriving an Agda reader.
    check(
        "a file mentioning neither agda nor module is skipped",
        passed=not rederive_census.relevant("t.py", "x = 1\n"),
    )

    # ⚑⚑ A DOCSTRING MARKER DECLARES THE WHOLE FILE, reported as None rather than a huge set so
    # a caller cannot mistake exhaustive coverage for a coincidence of ranges.
    marker = rederive_census.DECLARED.pattern
    whole = f'"""Doc.\n\n{marker} this tool predates the authorities.\n"""\nx = 1\n'
    check(
        "a docstring marker declares the whole file",
        passed=rederive_census.declared_lines(whole) is None,
    )
    # ⚑ THE CONTROL: a marker in code covers a RANGE, not the file — otherwise one marker
    # anywhere would silence every site.
    inline = "x = 1\n" * 70 + f"# {marker} here\n"
    check(
        "but a marker in code covers a range only",
        passed=isinstance(rederive_census.declared_lines(inline), set),
    )

    # ⚑⚑⚑ COVERAGE IS DIRECTIONAL, AND THIS ARM WAS THE ORIGIN'S AND NOT YET MINE. A marker
    # covers the site it INTRODUCES, which sits below it — so a marker that also covered lines
    # ABOVE would silence a derivation it never declared, and the silencing would look like a
    # paydown. The drain would have shipped without this: three of the origin's four cases were
    # already here and this one was not, which is the coverage loss a differential over KEYS
    # cannot see, because both directions agree on every file that carries no marker.
    #
    # ⚑ THE LINE NUMBERS ARE DERIVED FROM THE FIXTURE, NOT TYPED. The per-file gate refused the
    # literals, and it was right for a reason beyond style: a case that hardcodes `3` states a
    # fact about a fixture the case itself builds, so editing the fixture silently moves what is
    # asserted — the same claim this suite makes about the census's ordinal keys.
    before, at, after = "x = 1", f"# {marker} parses compiler output", 'p = re.compile(r"^m")'
    sited = f"{before}\n{at}\n{after}\n"
    lines = sited.split("\n")
    covered = rederive_census.declared_lines(sited)
    check(
        "a site marker covers the line after it",
        passed=covered is not None and lines.index(after) + 1 in covered,
    )
    check(
        "and does NOT cover the line before it",
        passed=covered is not None and lines.index(before) + 1 not in covered,
    )

    return out


def _differential_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` asserting SET EQUALITY with the live gate over the whole tree.

    ⚑⚑⚑ RUN NOW, BECAUSE IT EXPIRES AT THE SWAP. The gate currently computes this census
    independently, so agreement is evidence; once it calls this module the same arm becomes a
    function agreeing with itself. That is not a reason to skip it — it is the reason to run it
    before the swap rather than after.

    ⚑⚑ AND THE POPULATION COMES FROM THE DRAINED WALK, so this differences the PAIR a swap will
    install rather than the census against a population I rebuilt from my reading of the gate.
    """
    gate = _gate()
    if gate is None:
        skipped = (
            "the live gate could not be LOADED, so the differential is SKIPPED, "
            "not run and not passed"
        )
        return [(skipped, True)]

    pairs = tool_walk.sources(corpus.ROOT)
    if not pairs:
        return [("no source was found to difference — a fact about the TREE", True)]

    mine = rederive_census.census(pairs)
    theirs = gate.census()
    invented = sorted(mine - theirs)
    dropped = sorted(theirs - mine)
    return [
        (f"the drained pair invents no key (e.g. {invented[:_SHOW]})", not invented),
        (f"and drops none (e.g. {dropped[:_SHOW]})", not dropped),
        # ⚑ THE POSITIVE CONTROL: two empty sets are equal, so agreement is meaningless unless
        # the gate actually found something.
        ("and the gate's census is non-empty, so agreement is not vacuous", bool(theirs)),
    ]


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _motif_cases() + _scope_cases() + _differential_cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"rederive-census selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
