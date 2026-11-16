#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Names carrying two reimplementations, partitioned by what RESOLVES each one.

⚑⚑⚑ THE PARTITION IS BY RESOLUTION, NOT BY LOCATION, AND THAT DISTINCTION IS THE ITEM. A first
cut would have split "the tool corpus versus the rest", which orders by where a thing sits rather
than by what fixes it. These three each name a different repair:

    local     every site in ONE file. Python scopes these apart; a module-local helper reused
              under one name is not a shared authority and nothing is ambiguous to a reader.
    sibling   sites in one directory. A candidate lift, or a genuine per-file entry point.
    crossing  sites in DIFFERENT trees. The class that bit: `leverage` was a DAG cone in one
              tree and a two-grade reader in another, so a reader who finds one assumes the
              other's contract.

⚑⚑ A DELEGATING DEF IS NOT A RIVAL, AND COUNTING ONE WOULD REOPEN A CLOSED ITEM. Four one-line
wrappers named `agda_files` are an ALIAS FAMILY — one authority plus delegators, which is the
CONVERGED state a separate item already measured. A census counting them as collisions would
report the repair as the defect, and its count would move the wrong way as consolidation proceeds.

⚑ PROMOTED AS THE READER, NOT THE TOOLKIT (⟡items-n-split). The origin sits on a libcst pass
behind a content-and-deriver-keyed parse cache — machinery a witness does not need. The whole
delegating test is *"the body is one `return <call>`, docstring ignored"*, a few lines of `ast`;
carrying the cache across would be the promotion-takes-the-toolkit error this arc has corrected
three times (775→60, 2204→160, 540→160).

⚑ AND `scratch/` IS FORBIDDEN AT RUNTIME to promoted code, so reaching sideways for the census
was never an option — `check_scratch_independence` refuses it, and its message names the fix:
promote the module, do not repath the import.
"""

from __future__ import annotations

import ast
import sys
from typing import TYPE_CHECKING, NamedTuple

from substrate import corpus

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

# The three resolutions, narrowest first. ⚑ NAMED ONCE: the witness, the render and the cases all
# cite these rather than spelling them again.
LOCAL, SIBLING, CROSSING = "local", "sibling", "crossing"
KINDS = (LOCAL, SIBLING, CROSSING)


class Site(NamedTuple):
    """One definition of a name."""

    path: str
    line: int


class Collision(NamedTuple):
    """One name with two or more reimplementing definitions.

    ⚑ `name` IS THE FIRST FIELD SO THE TUPLE SORTS BY IT. A `key=lambda c: c.name` would infer
    `Callable[[Any], Any]` under the strict bar and carry that `Any` into the sorted result — the
    same untyped-lambda defect a `re.sub` replacement hit in this tree.
    """

    name: str
    sites: tuple[Site, ...]

    @property
    def kind(self) -> str:
        """Return which resolution this collision calls for.

        ⚑ DIRECTORY BEFORE TREE, AND BOTH BEFORE `sibling`. Two sites in different directories of
        the SAME tree are still a crossing — a reader who finds one has no reason to expect the
        other, which is what makes `crossing` its own repair rather than a wider `sibling`.
        """
        files = {s.path for s in self.sites}
        if len(files) == 1:
            return LOCAL
        trees = {f.split("/")[0] for f in files}
        dirs = {f.rsplit("/", 1)[0] if "/" in f else "" for f in files}
        if len(trees) > 1 or len(dirs) > 1:
            return CROSSING
        return SIBLING


def is_delegating(node: ast.FunctionDef) -> bool:
    """Report whether a function's whole body is one `return <call>`.

    ⚑⚑ THE DOCSTRING IS SKIPPED BEFORE THE TEST, and forgetting that inverts the answer. A
    delegator that documents WHY it delegates — exactly what this repo's delegators do, each
    carrying its incident in the docstring — would read as a two-statement body and be counted as
    a rival. The consolidation that FIXES a collision would then register as making it worse.
    """
    body = [
        s
        for s in node.body
        if not (
            isinstance(s, ast.Expr)
            and isinstance(s.value, ast.Constant)
            and isinstance(s.value.value, str)
        )
    ]
    return (
        len(body) == 1 and isinstance(body[0], ast.Return) and isinstance(body[0].value, ast.Call)
    )


def defs(path: Path, label: str) -> tuple[tuple[str, Site], ...]:
    """Return `(name, site)` for every non-private, non-delegating def in `path`.

    ⚑⚑⚑ IT WALKS THE WHOLE TREE, NOT JUST `tree.body`, AND THE FIRST CUT DID NOT — which made the
    `local` bucket structurally unfillable. Two same-named functions cannot both be top-level in
    one file, so a top-level-only reader reports `local: 0` FOREVER: a bucket that can never fill
    reads as a closed sub-item, and `T23-local` would have closed on the reader's blindness rather
    than on the tree. MEASURED before the fix: 341 collisions with `local` at 0, against an origin
    that partitions into three non-empty buckets.

    ⚑⚑ A METHOD ARTEFACT REPORTED AS A SUBSTRATE FACT is the class this repo names repeatedly, and
    it is worse in the ZERO direction: a false finding gets argued with, a false absence gets
    banked. The repair is the walk, not an exemption for the bucket.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, ValueError):
        return ()

    return tuple(
        (node.name, Site(path=label, line=node.lineno))
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and not node.name.startswith("_")
        and not is_delegating(node)
    )


def collisions(paths: Iterable[tuple[Path, str]]) -> tuple[Collision, ...]:
    """Return every name with two or more reimplementing definitions.

    ⚑ ONE CORPUS PASS, NOT ONE PER NAME. The origin records that its first cut re-parsed every
    file once per duplicated name, which took the item past a 120-second timeout — *"the work was
    REPEATED, and the fix is to do it once rather than to do it faster."*
    """
    by_name: dict[str, list[Site]] = {}
    for path, label in paths:
        for name, site in defs(path, label):
            by_name.setdefault(name, []).append(site)
    return tuple(
        sorted(
            Collision(name=name, sites=tuple(sites))
            for name, sites in by_name.items()
            if len(sites) > 1
        )
    )


def _relative(found: str, root: str) -> str:
    """Return a repo-relative label, or the path itself when it sits outside the root.

    ⚑ TOLERANT IN BOTH DIRECTIONS, because the enumerator's spelling is not this module's to fix
    and has already changed once. An already-relative label passes through; an absolute one is
    trimmed; one from another tree is returned whole rather than raising, since a reader handed
    an outside path wants a row, not a crash.

    ⚑ STRING WORK, NOT `Path` WORK. The label is a string and stays one, so `Path` remains a
    type-only import — the alternative was hoisting it to runtime for one `relative_to` call,
    trading a real dependency for a cosmetic one.
    """
    prefix = root if root.endswith("/") else root + "/"
    return found.removeprefix(prefix)


def population(root: Path | None = None) -> tuple[tuple[Path, str], ...]:
    """Return the corpus to scan, as `(path, repo-relative label)` pairs.

    ⚑⚑⚑ THE LABEL WAS ABSOLUTE WHILE THIS DOCSTRING SAID REPO-RELATIVE, AND THAT KILLED AN ARM OF
    THE CLASSIFIER. `corpus.py_files()` returns absolute paths, so `where / rel` was already
    absolute and every label carried a leading `/`. `Collision.kind` computes a tree as
    `path.split("/")[0]`, which is then `""` for every site — so its `len(trees) > 1` test **has
    never fired**, and `crossing` has only ever been decided by the directory arm.

    ⚑⚑ THE VERDICTS WERE NOT WRONG, WHICH IS WHY NOTHING CAUGHT IT. Cross-directory genuinely IS
    crossing, so every row was correctly classified by the surviving arm while the arm written for
    the recorded incident — one name meaning different things in two TREES — was dead code. **A
    predicate that cannot fire is indistinguishable from one that never had a case**, and the
    census it feeds reads as healthy either way.

    ⚑ FOUND FROM OUTSIDE, BY A CONSUMER. A reader asking *"which collisions touch `scratch/`"*
    reported `0 of 270` for EVERY tree in the repo — clean, plausible, entirely false, and caught
    only because all-zero-for-all-trees is not a shape the substrate can have.
    """
    where = root if root is not None else corpus.ROOT
    base = str(where)
    return tuple(
        (where / _relative(found, base), _relative(found, base))
        for found in corpus.py_files(root=where)
    )


def by_kind(found: tuple[Collision, ...]) -> dict[str, tuple[Collision, ...]]:
    """Return the collisions bucketed by the resolution each calls for.

    ⚑ EVERY KIND IS A KEY, INCLUDING THE EMPTY ONES. A bucket that vanishes when it empties makes
    a caller unable to distinguish *"no crossing collisions"* from *"crossing is not a kind this
    census knows"* — the false-zero shape, one layer in.
    """
    out: dict[str, list[Collision]] = {kind: [] for kind in KINDS}
    for got in found:
        out[got.kind].append(got)
    return {kind: tuple(rows) for kind, rows in out.items()}


def render(found: tuple[Collision, ...]) -> str:
    """Return the census — one line per kind, with a sample."""
    if not found:
        return "  no name carries two reimplementations\n"

    buckets = by_kind(found)
    lines = [f"  {len(found)} colliding name(s)"]
    for kind in KINDS:
        rows = buckets[kind]
        sample = ", ".join(f"{c.name} x{len(c.sites)}" for c in rows[:5])
        lines.append(f"    {kind:<9} {len(rows):>4}  {sample or 'none'}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.stdout.write(render(collisions(population())))
    sys.exit(0)
