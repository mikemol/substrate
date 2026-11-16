#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Which colliding names TOUCH a given tree, partitioned by the repair each calls for.

⚑⚑⚑ THIS IS THE MODE THE ⟡scratch-dedup ARC HAD TO HAVE AND DID NOT. `name_collision` answers
*how many names collide in the corpus*; the retirement question is *how many collisions have at
least one site in `scratch/`* — a different question, and the census could not be asked it. Under
this repo's standing rule a missing mode is WORK, not grounds for a shell composition: the
alternative was a `python3 -c` wrapper around `by_kind`, which puts the judgement in the turn
instead of in a program, where it evaporates when the turn ends.

⚑⚑ TOUCHING IS NOT CONTAINMENT, AND THE DIFFERENCE IS THE WHOLE FINDING. A name with one site in
`scratch/` and one in `scripts/` is precisely the `crossing` class that bit — the class a
containment reader (*every* site in the tree) would DROP, because it is the one collision the
tree does not own outright. So `scope` is *at least one site*, and `confined` is reported
SEPARATELY rather than instead: a collision confined to `scratch/` can be retired inside the
tree, while one that escapes it needs an authority chosen between trees.

⚑ EVERY FIGURE CARRIES ITS DENOMINATOR. A bare `14 crossing` cannot be told apart from a query
that could not see the rest; `14 of 268` can. This is the same false-zero discipline
`name_collision.by_kind` already applies by keying empty buckets, one layer out.

⚑ IT ADDS NO READER OF ITS OWN. The population, the delegator test and the three kinds all come
from `name_collision`; duplicating any of them here would make this module a second authority on
the very question the arc exists to reduce.

⚑⚑⚑ AND BUILDING IT SURFACED A DEFECT IN THE CENSUS IT READS. `name_collision.population` names
its second element a *repo-relative label*, but it takes that label from `corpus.py_files`, which
returns ABSOLUTE path strings. So every site's `path` starts with `/`, and THE FIRST CUT OF THIS
MODULE DUTIFULLY REPORTED `0 of 270` FOR EVERY TREE IN THE REPO — a clean, plausible, entirely
false zero, caught only because a zero in all buckets for all trees is not a shape the substrate
can have. The consequence reaches past this module: `Collision.kind` computes a tree as
`path.split("/")[0]`, which on an absolute path is the EMPTY STRING for every site, so its
`len(trees) > 1` test can never fire and `crossing` has only ever been decided by the directory
arm. The distinction is not wrong — a cross-DIRECTORY collision is still crossing — but the
cross-TREE arm the kind was written for has never run.

⚑ SO THIS MODULE NORMALIZES RATHER THAN TRUSTING THE LABEL. Repairing `population` is the better
fix and belongs to that module; normalizing here is what lets the census be READ correctly today,
and it stays correct if the label is later made relative — `relative_to` is skipped when the path
is already relative.

⚑⚑ THE TREE IS AN ARGUMENT, THREADED FROM THE ENTRY POINT (2026-09-24, operator: "We should not
have things [like] corpus.ROOT"). `tree_of` used to default `root` to `corpus.ROOT`, and three
functions leaned on that default silently; mypy named all three the moment it was removed. Now
every function that normalizes a path takes the tree, and `main` reads it from a required
`--root <dir>` (`mikemol.corpus.tree_root.from_argv`), refusing without it.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from mikemol.corpus import tree_root

from substrate import name_collision


@dataclass(frozen=True, slots=True)
class Scoped:
    """One kind's collisions, split by how a tree relates to them.

    ⚑ THREE COUNTS, NOT ONE RATIO. `total` is the corpus denominator, `touching` the collisions
    with at least one site in the tree, and `confined` the subset with EVERY site there. A ratio
    would collapse the distinction between *the tree owns this* and *the tree shares it*, which
    is exactly the distinction that decides whether a retirement is local or cross-tree.
    """

    kind: str
    total: int
    touching: tuple[name_collision.Collision, ...]
    confined: tuple[name_collision.Collision, ...]


def tree_of(path: str, root: Path) -> str:
    """Return the top-level tree a site's path lies in, absolute or relative to `root`.

    ⚑⚑ THE NORMALIZATION IS THE POINT. `name_collision.population` labels its sites *repo-
    relative* and hands over what `corpus.py_files` produces, which is ABSOLUTE — so a reader
    trusting the label splits on a leading `/` and gets the empty string for every site in the
    repo. That is not a small offset: it makes every tree-scoped question answer `0`.

    ⚑ AND IT IS TOLERANT IN BOTH DIRECTIONS. A path already relative to the root is returned
    unchanged, so this keeps working — rather than inverting — if the label is repaired upstream.
    """
    p = Path(path)
    if p.is_absolute():
        try:
            p = p.relative_to(root)
        except ValueError:
            return ""
    parts = p.parts
    return parts[0] if len(parts) > 1 else ""


def in_tree(site: name_collision.Site, tree: str, root: Path) -> bool:
    """Report whether a site lies under `tree` of the repository at `root`.

    ⚑ A PATH COMPONENT, NOT A PREFIX. `path.startswith("scratch")` also matches a hypothetical
    `scratchpad/` sibling — the same substring-versus-component defect `corpus.excluded` records
    for `build` eating `rebuild/`, and it would silently widen every count here.
    """
    return tree_of(site.path, root) == tree


def scope(found: tuple[name_collision.Collision, ...], tree: str, root: Path) -> dict[str, Scoped]:
    """Partition the corpus's collisions by kind, scoped to one tree.

    ⚑ EVERY KIND IS A KEY, EVEN WITH NOTHING IN IT — inherited from `by_kind` deliberately. A
    caller must be able to distinguish *no crossing collisions touch this tree* from *crossing is
    not a partition this reader knows*.
    """
    buckets = name_collision.by_kind(found)
    out: dict[str, Scoped] = {}
    for kind in name_collision.KINDS:
        rows = buckets[kind]
        touching = tuple(c for c in rows if any(in_tree(s, tree, root) for s in c.sites))
        confined = tuple(c for c in touching if all(in_tree(s, tree, root) for s in c.sites))
        out[kind] = Scoped(kind=kind, total=len(rows), touching=touching, confined=confined)
    return out


def trees(found: tuple[name_collision.Collision, ...], root: Path) -> tuple[str, ...]:
    """Return every tree any colliding site lies in, sorted.

    ⚑ DISCOVERED, NOT FROZEN. A hardcoded roster of trees can only be as current as its last
    edit — the defect `corpus.SKIP_DIRS` records happening three times in this repo — and here it
    would also HIDE the normalization bug this module exists downstream of: a frozen list that
    happened to name the right trees would still report zero, with nothing to contradict it.
    """
    return tuple(sorted({t for c in found for s in c.sites if (t := tree_of(s.path, root))}))


def render(scoped: dict[str, Scoped], tree: str) -> str:
    """Return the scoped census — one line per kind, every figure with its denominator."""
    lines = [f"  collisions touching {tree}/"]
    for kind in name_collision.KINDS:
        row = scoped[kind]
        sample = ", ".join(f"{c.name} x{len(c.sites)}" for c in row.touching[:5])
        lines.append(
            f"    {kind:<9} {len(row.touching):>4} of {row.total:<4} "
            f"({len(row.confined)} confined)  {sample or 'none'}"
        )
    return "\n".join(lines) + "\n"


def listing(scoped: dict[str, Scoped], kind: str, tree: str, root: Path) -> str:
    """Return every collision of one kind touching `tree`, with all its sites.

    ⚑⚑ THE SUMMARY CANNOT DRIVE A RETIREMENT AND THE SAMPLE ACTIVELY MISLEADS. `render` shows
    five names in sort order, which on this corpus means `add x11`, `all x2`, `analyse x2` — the
    generic per-file entry points that are NOT duplicated capability. Choosing what to retire
    needs the sites, and a reader who chose from the sample would work on exactly the rows least
    worth working on.

    ⚑ SITES, NOT A COUNT. A name reported as colliding without WHERE cannot be acted on, and the
    site list is what separates a genuine shared capability from a shared name over two concepts
    — the `wedge`/`join`/`leverage` error this census family exists to stop.
    """
    rows = scoped[kind].touching
    lines = [f"  {len(rows)} of {scoped[kind].total} `{kind}` collision(s) touching {tree}/"]
    for got in rows:
        lines.append(f"    {got.name}  x{len(got.sites)}")
        lines.extend(
            f"      {tree_of(s.path, root)}/{Path(s.path).name}:{s.line}" for s in got.sites
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    """Read `--root <dir>`, then print the scoped census or one kind's listing (`--sites`)."""
    try:
        tree_arg, args = tree_root.from_argv(argv[1:])
    except tree_root.RootError as exc:
        sys.stderr.write(f"collision_scope: {exc}\n")
        return 2
    root = tree_arg.path
    found = name_collision.collisions(name_collision.population())
    flags = [a for a in args if a.startswith("-")]
    rest = [a for a in args if not a.startswith("-")]
    if "--sites" in flags:
        kind = rest[0] if rest else name_collision.CROSSING
        tree = rest[1] if len(rest) > 1 else "scratch"
        if kind not in name_collision.KINDS:
            sys.stderr.write(f"  {kind!r} is not a kind ({', '.join(name_collision.KINDS)})\n")
            return 2
        sys.stdout.write(listing(scope(found, tree, root), kind, tree, root))
        return 0
    for tree in rest or list(trees(found, root)):
        sys.stdout.write(render(scope(found, tree, root), tree))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
