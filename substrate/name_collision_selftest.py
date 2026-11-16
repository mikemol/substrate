#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.name_collision` — the three kinds, and the bucket that could not fill.

⚑⚑⚑ THE NESTED-DEF CASE IS HERE BECAUSE ITS ABSENCE ALREADY COST A FALSE ZERO. A first cut walked
only `tree.body`, so `local` — two definitions of one name in ONE file — was structurally
unfillable: two same-named functions cannot both be top-level. It reported `local: 0` and would
have gone on reporting it forever, so `T23-local` would have closed on the reader's blindness
rather than on the tree. MEASURED: 341 collisions with `local` at 0 before the walk was widened;
533 with `local` at 14 after.

⚑⚑ AND THE DELEGATOR CASE IS THE OPPOSITE DIRECTION. Four one-line wrappers named `agda_files`
are an alias family — one authority plus delegators — which a separate item measured as the
CONVERGED state. Counting them would report the repair as the defect, and the census would move
the wrong way as consolidation proceeds.

⚑ THE FIXTURES ARE SOURCE STRINGS. A case reading the live corpus measures today's tree, so it
would report the corpus rather than the reader — and go green the moment an unrelated file moved.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import name_collision

# Two top-level definitions of one name, in one file — the `local` shape a top-level-only reader
# CANNOT produce, since two same-named functions cannot both be top-level.
_NESTED = '''def outer() -> int:
    """A holder."""
    def shared() -> int:
        return 1
    return shared()


def other() -> int:
    """Another holder."""
    def shared() -> int:
        return 2
    return shared()
'''

# One real definition and one delegator — an alias family, not a collision.
_AUTHORITY = '''def agda_files() -> list[str]:
    """The authority: it has a body."""
    found: list[str] = []
    return found
'''

_DELEGATOR = '''def agda_files() -> list[str]:
    """A one-line delegator.

    ⚑ It carries its incident in the docstring, as this repo's delegators do.
    """
    return _agda_files(ROOT)
'''

# Two rivals, each with a body of its own.
_RIVAL = '''def leverage() -> int:
    """A body of its own."""
    total = 0
    return total
'''

# A private name — scoped by convention, never a shared authority.
_PRIVATE = '''def _helper() -> int:
    """Private."""
    value = 1
    return value
'''

_TWO_SITES = 2
_LOCAL_SITES = 2


def _found(files: dict[str, str]) -> tuple[name_collision.Collision, ...]:
    """Write fixture files under a temp root and read the collisions back."""
    with tempfile.TemporaryDirectory() as where:
        pairs = []
        for label, text in files.items():
            path = Path(where) / label
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            pairs.append((path, label))
        return name_collision.collisions(pairs)


def two_definitions_in_one_file_are_local(out: list[str]) -> int:
    """Check a name defined twice inside one file is found, and classed `local`.

    ⚑⚑⚑ THE CASE THAT WOULD HAVE CAUGHT THE FALSE ZERO. A reader walking only `tree.body` cannot
    produce this row at all — the bucket is unfillable, so it reports 0 forever and the sub-item
    closes on the reader's blindness. **A false absence gets banked; a false finding gets argued
    with.**
    """
    got = _found({"a/one.py": _NESTED})
    if len(got) != 1:
        out.append(f"selftest: a nested duplicate was not found: {got!r}")
        return 1
    if got[0].kind != name_collision.LOCAL:
        out.append(f"selftest: a one-file duplicate classed {got[0].kind!r}")
        return 1
    return 0


def two_files_in_one_directory_are_siblings(out: list[str]) -> int:
    """Check sites sharing a directory are classed `sibling` — a candidate lift."""
    got = _found({"a/one.py": _RIVAL, "a/two.py": _RIVAL})
    if len(got) != 1 or got[0].kind != name_collision.SIBLING:
        out.append(f"selftest: same-directory rivals classed {got!r}")
        return 1
    return 0


def two_directories_in_one_tree_are_crossing(out: list[str]) -> int:
    """Check sites in different directories of ONE tree are still `crossing`.

    ⚑ THE WIDER READING IS THE RIGHT ONE. A reader who finds one has no reason to expect the
    other, which is what makes `crossing` its own repair rather than a broader `sibling` — and
    classing these as siblings would put a genuine ambiguity in the bucket meaning *lift me*.
    """
    got = _found({"a/one.py": _RIVAL, "a/deeper/two.py": _RIVAL})
    if len(got) != 1 or got[0].kind != name_collision.CROSSING:
        out.append(f"selftest: cross-directory rivals classed {got!r}")
        return 1
    return 0


def two_trees_are_crossing(out: list[str]) -> int:
    """Check sites in different top-level trees are `crossing` — the class that bit.

    ⚑ `leverage` WAS A DAG CONE IN ONE TREE AND A TWO-GRADE READER IN ANOTHER, and a reader who
    found one assumed the other's contract. That is the recorded incident this kind exists for.
    """
    got = _found({"a/one.py": _RIVAL, "b/two.py": _RIVAL})
    if len(got) != 1 or got[0].kind != name_collision.CROSSING:
        out.append(f"selftest: cross-tree rivals classed {got!r}")
        return 1
    return 0


def a_delegator_is_not_a_rival(out: list[str]) -> int:
    """Check an authority plus a one-line delegator is NOT a collision.

    ⚑⚑ COUNTING IT WOULD REOPEN A CLOSED ITEM. An alias family is the CONVERGED state a separate
    item already measured; a census that counted it would report the repair as the defect, and
    its number would move the wrong way as consolidation proceeds.
    """
    got = _found({"a/one.py": _AUTHORITY, "b/two.py": _DELEGATOR})
    if got != ():
        out.append(f"selftest: a delegator was counted as a rival: {got!r}")
        return 1
    return 0


def two_bodies_are_still_rivals(out: list[str]) -> int:
    """Check two real implementations ARE reported — the POSITIVE CONTROL for the delegator case.

    ⚑ WITHOUT THIS, A READER THAT EXCUSED EVERYTHING would pass the case above. The pair says the
    delegating test discriminates rather than suppressing the whole population.
    """
    got = _found({"a/one.py": _RIVAL, "b/two.py": _RIVAL})
    if len(got) != 1 or len(got[0].sites) != _TWO_SITES:
        out.append(f"selftest: two bodies were not reported as rivals: {got!r}")
        return 1
    return 0


def a_docstring_does_not_make_a_delegator_a_rival(out: list[str]) -> int:
    """Check the docstring is skipped before the one-statement test.

    ⚑⚑ FORGETTING THIS INVERTS THE ANSWER. This repo's delegators each carry their incident in a
    docstring, so a reader counting statements without skipping it sees a two-statement body and
    calls every documented delegator a rival — the consolidation that fixes a collision would
    then register as making it worse.
    """
    got = _found({"a/one.py": _AUTHORITY, "b/two.py": _DELEGATOR})
    if got != ():
        out.append(f"selftest: a documented delegator was counted: {got!r}")
        return 1
    return 0


def a_private_name_is_not_a_collision(out: list[str]) -> int:
    """Check `_`-prefixed names are excluded.

    ⚑ A PRIVATE NAME IS SCOPED BY CONVENTION and is not a shared authority; counting it would put
    every module's `_helper` into a census about ambiguous contracts.
    """
    got = _found({"a/one.py": _PRIVATE, "b/two.py": _PRIVATE})
    if got != ():
        out.append(f"selftest: a private name was counted: {got!r}")
        return 1
    return 0


def a_single_definition_is_not_a_collision(out: list[str]) -> int:
    """Check one definition of a name yields nothing."""
    got = _found({"a/one.py": _RIVAL})
    if got != ():
        out.append(f"selftest: a lone definition was reported: {got!r}")
        return 1
    return 0


def every_kind_is_a_bucket_even_when_empty(out: list[str]) -> int:
    """Check the partition keys every kind, including ones with no members.

    ⚑⚑ A BUCKET THAT VANISHES WHEN IT EMPTIES makes a caller unable to distinguish *no crossing
    collisions* from *crossing is not a kind this census knows* — the false-zero shape, one layer
    in, and the same defect the `local` walk had at the reader level.
    """
    buckets = name_collision.by_kind(())
    missing = [k for k in name_collision.KINDS if k not in buckets]
    if missing:
        out.append(f"selftest: the partition omits empty kinds: {missing!r}")
        return 1
    return 0


def a_collision_carries_every_site(out: list[str]) -> int:
    """Check all sites are reported, not just the first two.

    ⚑ THE SITES ARE THE WORK. A reader told a name collides but not where cannot act; and a
    census truncating at two under-reports the cost of the ones that matter most.
    """
    got = _found({"a/one.py": _RIVAL, "a/two.py": _RIVAL, "a/three.py": _RIVAL})
    if len(got) != 1 or len(got[0].sites) != _LOCAL_SITES + 1:
        out.append(f"selftest: not every site was carried: {got!r}")
        return 1
    return 0


def an_unparseable_file_yields_nothing(out: list[str]) -> int:
    """Check a syntax error is skipped rather than raising.

    ⚑ ONE BAD FILE MUST NOT TAKE THE CENSUS DOWN. A corpus-wide reader that raised on the first
    unparseable file would report nothing about the 989 that parse.
    """
    got = _found({"a/one.py": "def broken(:\n"})
    if got != ():
        out.append(f"selftest: an unparseable file yielded {got!r}")
        return 1
    return 0


def an_empty_census_says_so(out: list[str]) -> int:
    """Check the render names its own emptiness rather than printing nothing.

    ⚑ SILENCE AND SUCCESS ARE THE SAME BYTES — the false-zero shape every census in this tree
    prints its denominator to avoid.
    """
    if "no name carries" not in name_collision.render(()):
        out.append("selftest: an empty census does not name its emptiness")
        return 1
    return 0


def the_render_names_every_kind(out: list[str]) -> int:
    """Check all three kinds appear in the report, including empty ones."""
    rows = _found({"a/one.py": _RIVAL, "b/two.py": _RIVAL})
    text = name_collision.render(rows)
    missing = [k for k in name_collision.KINDS if k not in text]
    if missing:
        out.append(f"selftest: the render omits {missing!r}:\n{text}")
        return 1
    return 0


_ARMS = (
    two_definitions_in_one_file_are_local,
    two_files_in_one_directory_are_siblings,
    two_directories_in_one_tree_are_crossing,
    two_trees_are_crossing,
    a_delegator_is_not_a_rival,
    two_bodies_are_still_rivals,
    a_docstring_does_not_make_a_delegator_a_rival,
    a_private_name_is_not_a_collision,
    a_single_definition_is_not_a_collision,
    every_kind_is_a_bucket_even_when_empty,
    a_collision_carries_every_site,
    an_unparseable_file_yields_nothing,
    an_empty_census_says_so,
    the_render_names_every_kind,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"name-collision selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"name-collision selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
