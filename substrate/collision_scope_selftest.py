#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.collision_scope` — touching versus confined, and the denominator.

⚑⚑⚑ THE CASE THAT MATTERS IS `a_shared_collision_touches_both_trees`. A containment reader —
*every* site in the tree — is the natural first cut and it DROPS exactly the `crossing` class the
arc exists to retire, because a cross-tree collision is by definition not owned outright by
either tree. That reader would report a smaller, cleaner number and hide the only rows worth
acting on.

⚑⚑ AND `an_absolute_label_still_names_its_tree` IS HERE BECAUSE ITS ABSENCE ALREADY COST A FALSE
ZERO IN THIS VERY MODULE. The first cut of the reader trusted `name_collision.population`'s
*repo-relative label*, which is sourced from `corpus.py_files` and is in fact ABSOLUTE; every
tree-scoped figure came back `0 of 270`, for every tree in the repo at once. Every case below it
passed, because a FIXTURE naturally uses relative labels — the cases agreed with each other and
with nothing in the corpus.

⚑ AND `a_prefix_does_not_count_as_the_tree` IS THE OVER-COUNTING TWIN. A predicate matching
`path.startswith(tree)` passes every touching case above while silently pulling in a `scratchpad/`
sibling — a reader that over-counts is as false as one that under-counts, and only a case naming
the near-miss separates them.

⚑ THE FIXTURES ARE SOURCE STRINGS, never the live corpus: a case reading today's tree reports the
corpus rather than the reader, and goes green when an unrelated file moves.

⚑ THE TREE IS A FIXTURE ROOT TOO (2026-09-24, no-ROOT rule). The module now takes the tree as an
argument, so the absolute-label case builds its path under `_ROOT` rather than the live
`corpus.ROOT` — the suite reads no real tree at all.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import collision_scope, name_collision

# A tree root that exists only in these cases — labels below are relative to it.
_ROOT = Path("/fixture-root")

# Two real bodies — a rival, not a delegator.
_RIVAL = '''def leverage() -> int:
    """A body of its own."""
    total = 0
    return total
'''

_OTHER = '''def other() -> int:
    """A body."""
    n = 1
    return n
'''

_TWO = 2


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


def a_shared_collision_touches_both_trees(out: list[str]) -> int:
    """Check a collision with one site per tree is TOUCHING for each, confined to neither.

    ⚑⚑⚑ THE ROW A CONTAINMENT READER DROPS. A cross-tree collision is the `crossing` class that
    bit — the one a tree does not own outright — so a reader defining scope as *every site here*
    reports a smaller, cleaner census with precisely the actionable rows missing.
    """
    got = _found({"scratch/one.py": _RIVAL, "scripts/two.py": _RIVAL})
    scoped = collision_scope.scope(got, "scratch", _ROOT)[name_collision.CROSSING]
    if len(scoped.touching) != 1:
        out.append(f"selftest: a shared collision did not touch scratch: {scoped!r}")
        return 1
    if scoped.confined:
        out.append(f"selftest: a shared collision was called confined: {scoped!r}")
        return 1
    return 0


def a_collision_inside_one_tree_is_confined(out: list[str]) -> int:
    """Check every-site-in-the-tree is reported as confined — the POSITIVE CONTROL.

    ⚑ WITHOUT THIS, A READER THAT NEVER CALLS ANYTHING CONFINED passes the case above. The pair
    says `confined` discriminates rather than being permanently empty, which is the false-zero
    this whole census family is built against.
    """
    got = _found({"scratch/a/one.py": _RIVAL, "scratch/b/two.py": _RIVAL})
    scoped = collision_scope.scope(got, "scratch", _ROOT)[name_collision.CROSSING]
    if len(scoped.confined) != 1:
        out.append(f"selftest: an in-tree collision was not confined: {scoped!r}")
        return 1
    return 0


def a_collision_elsewhere_does_not_touch_the_tree(out: list[str]) -> int:
    """Check a collision with no site in the tree is excluded from every bucket."""
    got = _found({"scripts/one.py": _RIVAL, "catalog/two.py": _RIVAL})
    scoped = collision_scope.scope(got, "scratch", _ROOT)
    touching = sum(len(scoped[k].touching) for k in name_collision.KINDS)
    if touching:
        out.append(f"selftest: an unrelated collision touched scratch: {scoped!r}")
        return 1
    return 0


def a_prefix_does_not_count_as_the_tree(out: list[str]) -> int:
    """Check `scratchpad/` is not read as `scratch/`.

    ⚑⚑ THE OVER-COUNTING TWIN. `path.startswith(tree)` passes every touching case above and
    silently widens the census by whatever siblings share a prefix — the same substring-versus-
    component defect `corpus.excluded` records for `build` eating `rebuild/`.
    """
    got = _found({"scratchpad/one.py": _RIVAL, "scripts/two.py": _RIVAL})
    scoped = collision_scope.scope(got, "scratch", _ROOT)
    touching = sum(len(scoped[k].touching) for k in name_collision.KINDS)
    if touching:
        out.append(f"selftest: a prefix sibling counted as the tree: {scoped!r}")
        return 1
    return 0


def an_absolute_label_still_names_its_tree(out: list[str]) -> int:
    """Check a site labelled with an ABSOLUTE path is still attributed to its tree.

    ⚑⚑⚑ THE DEFECT THAT ACTUALLY BIT, AND IT BIT SILENTLY. `name_collision.population` documents
    its label as *repo-relative* and sources it from `corpus.py_files`, which returns absolute
    strings. A reader trusting the label splits on the leading `/` and gets the empty string for
    every site in the repo, so every tree-scoped question answers `0 of 270` — clean, plausible,
    and wrong for the whole corpus at once. It survived the first round of cases here because
    every FIXTURE used relative labels, which is precisely the shape a fixture defaults to.
    """
    got = collision_scope.tree_of(str(_ROOT / "scratch" / "one.py"), _ROOT)
    if got != "scratch":
        out.append(f"selftest: an absolute label named tree {got!r}, not 'scratch'")
        return 1
    return 0


def a_relative_label_names_the_same_tree(out: list[str]) -> int:
    """Check a repo-relative label is read unchanged — the POSITIVE CONTROL for normalization.

    ⚑ WITHOUT THIS, A READER THAT ONLY EVER STRIPPED A ROOT would pass the case above while
    breaking the day the upstream label is repaired to be relative as documented. The pair says
    the normalization is tolerant in BOTH directions rather than trading one blindness for the
    other.
    """
    if collision_scope.tree_of("scratch/one.py", _ROOT) != "scratch":
        out.append("selftest: a relative label lost its tree")
        return 1
    return 0


def a_path_outside_the_root_names_no_tree(out: list[str]) -> int:
    """Check an absolute path outside the corpus root yields no tree rather than raising.

    ⚑ `relative_to` RAISES ON A NON-DESCENDANT. A census that died on one stray path would report
    nothing about the rest of the corpus — the same reason `name_collision.defs` swallows a
    SyntaxError instead of taking the whole run down.
    """
    if collision_scope.tree_of("/elsewhere/one.py", _ROOT) != "":
        out.append("selftest: a path outside the root claimed a tree")
        return 1
    return 0


def the_tree_roster_is_discovered(out: list[str]) -> int:
    """Check `trees` reports the trees actually present, not a frozen list.

    ⚑ A FROZEN ROSTER WOULD HAVE HIDDEN THE NORMALIZATION BUG. A hardcoded list naming the right
    trees still renders zero counts against every one of them, with nothing in the output to
    contradict it — the roster would agree with itself while the reader saw nothing.
    """
    got = _found({"scratch/one.py": _RIVAL, "scripts/two.py": _RIVAL})
    roster = collision_scope.trees(got, _ROOT)
    if roster != ("scratch", "scripts"):
        out.append(f"selftest: the roster was not discovered: {roster!r}")
        return 1
    return 0


def the_denominator_is_the_whole_kind(out: list[str]) -> int:
    """Check `total` counts the corpus's collisions of that kind, not the scoped ones.

    ⚑ A BARE COUNT CANNOT BE TOLD FROM A QUERY THAT COULD NOT SEE THE REST. The denominator is
    what makes `14 of 268` a finding rather than an assertion, and a `total` equal to `touching`
    would be a denominator that agrees with itself by construction.
    """
    got = _found(
        {
            "scratch/one.py": _RIVAL,
            "scripts/two.py": _RIVAL,
            "scripts/a/three.py": _OTHER,
            "catalog/four.py": _OTHER,
        }
    )
    scoped = collision_scope.scope(got, "scratch", _ROOT)[name_collision.CROSSING]
    if scoped.total != _TWO or len(scoped.touching) != 1:
        out.append(f"selftest: the denominator is not the whole kind: {scoped!r}")
        return 1
    return 0


def every_kind_is_a_key_even_when_empty(out: list[str]) -> int:
    """Check the scoped partition keys all three kinds.

    ⚑ A BUCKET THAT VANISHES WHEN IT EMPTIES leaves a caller unable to tell *no crossing
    collisions touch this tree* from *crossing is not a kind this reader knows*.
    """
    scoped = collision_scope.scope((), "scratch", _ROOT)
    missing = [k for k in name_collision.KINDS if k not in scoped]
    if missing:
        out.append(f"selftest: the scoped partition omits {missing!r}")
        return 1
    return 0


def the_render_carries_every_denominator(out: list[str]) -> int:
    """Check each printed line shows `n of m`, not a bare count."""
    got = _found({"scratch/one.py": _RIVAL, "scripts/two.py": _RIVAL})
    text = collision_scope.render(collision_scope.scope(got, "scratch", _ROOT), "scratch")
    if text.count(" of ") != len(name_collision.KINDS):
        out.append(f"selftest: a line lacks its denominator:\n{text}")
        return 1
    return 0


def the_listing_carries_every_site(out: list[str]) -> int:
    """Check `listing` names every site of every touching collision, not a sample.

    ⚑⚑ THE SUMMARY CANNOT DRIVE A RETIREMENT. `render` shows five names in SORT ORDER, which on
    this corpus surfaces `add`, `all`, `analyse` — generic per-file entry points that are not
    duplicated capability at all. A reader choosing work from the sample works on precisely the
    rows least worth working on, and nothing in the sample says so.
    """
    got = _found({"scratch/one.py": _RIVAL, "scripts/two.py": _RIVAL, "scratch/a/three.py": _RIVAL})
    text = collision_scope.listing(
        collision_scope.scope(got, "scratch", _ROOT), name_collision.CROSSING, "scratch", _ROOT
    )
    if text.count(":") != len(got[0].sites):
        out.append(f"selftest: the listing dropped sites:\n{text}")
        return 1
    return 0


def the_listing_is_empty_when_nothing_touches(out: list[str]) -> int:
    """Check an empty listing still states its denominator — the POSITIVE CONTROL's twin.

    ⚑ SILENCE AND SUCCESS ARE THE SAME BYTES. A listing that printed nothing when nothing
    matched cannot be told from one whose scope was wrong, which is the exact failure the first
    cut of this module shipped: `0 of 270` for every tree, silently.
    """
    got = _found({"scripts/one.py": _RIVAL, "catalog/two.py": _RIVAL})
    text = collision_scope.listing(
        collision_scope.scope(got, "scratch", _ROOT), name_collision.CROSSING, "scratch", _ROOT
    )
    if " of " not in text:
        out.append(f"selftest: an empty listing states no denominator:\n{text}")
        return 1
    return 0


_ARMS = (
    a_shared_collision_touches_both_trees,
    the_listing_carries_every_site,
    the_listing_is_empty_when_nothing_touches,
    a_collision_inside_one_tree_is_confined,
    a_collision_elsewhere_does_not_touch_the_tree,
    a_prefix_does_not_count_as_the_tree,
    an_absolute_label_still_names_its_tree,
    a_relative_label_names_the_same_tree,
    a_path_outside_the_root_names_no_tree,
    the_tree_roster_is_discovered,
    the_denominator_is_the_whole_kind,
    every_kind_is_a_key_even_when_empty,
    the_render_carries_every_denominator,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"collision-scope selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"collision-scope selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
