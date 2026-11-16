#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The T23 family — no name carries two reimplementations, partitioned by what resolves each.

⚑⚑⚑ THE FAMILY WAS ALREADY PARAMETERIZED, WHICH IS WHY THIS IS AN EXTRACTION AND NOT A DESIGN.
The origin's three sub-items are three-line delegators onto ONE body — *"shared body, N items;
three witnesses saying the same thing about different partitions would be three chances to
drift."* The shape this arc formalizes as `witness_family` was already being used by hand here;
what it lacked was a way to DECLARE the roster, so nothing could read the members without running
the aggregate.

⚑⚑ THE PARTITION IS BY RESOLUTION, NOT BY LOCATION, and each kind names a different repair —
`local` scoped apart by Python, `sibling` a candidate lift, `crossing` the class that bit. A
partition by directory would order by where a thing sits rather than by what fixes it.

⚑ THE AGGREGATE RESTS ON ITS PARTS AND MEASURES NOTHING ITSELF. The origin spelled that in prose
while implementing it as a re-run of each route with stdout redirected into a buffer; here it is
a premise edge, so a reader asks the roster instead of the interpreter.

⚑ MEASURED BEFORE WRITING — 533 colliding names: local 14, sibling 254, crossing 265. ⚑⚑ AND THE
FIRST READER REPORTED `local: 0` because it walked only top-level defs, which made that bucket
STRUCTURALLY UNFILLABLE: two same-named functions cannot both be top-level, so `T23-local` would
have closed on the reader's blindness. The walk was widened and the population went 341 → 533.

⚑⚑ THE FIGURE COMES FROM `warrant_records` AND THE EXCEPTION FROM `warrant_bib` (gate-G209). The
engine half — `records` / `claim_of` / `tag` — imports paperkit at module scope and lives in its
own module; `WarrantError` stays with the config half precisely so a caller catching it need not
import the engine to name the exception it is catching.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), rewritten rather than moved.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mikemol.witness import witness_family, witness_row
from mikemol.witness.warrant_bib import WarrantError

from substrate import name_collision, warrant_records

if TYPE_CHECKING:
    from collections.abc import Iterator

# ⚑ THE FAMILY, DECLARED. The apex says what having all three partitions establishes — which no
# one kind says alone — and `subject` names what it is parameterized over, so a tree gaining a
# module gains subjects without an edit here.
FAMILY = witness_family.of(
    key="T23",
    apex="no name carries two reimplementations with different return shapes, and each surviving "
    "collision is filed under the repair it actually needs",
    subject="every non-private, non-delegating definition in the corpus",
    members=[
        witness_family.Member(
            name="no_name_is_reimplemented_twice_within_one_file",
            claim="Python scopes these apart, so the bar is lowest here: a module-local helper "
            "reused under one name is not a shared authority and nothing is ambiguous to a "
            "reader",
        ),
        witness_family.Member(
            name="no_name_is_reimplemented_twice_within_one_directory",
            claim="sites in one directory are a candidate lift — or a genuine per-file entry "
            "point, which is why this is its own kind rather than folded into the wider one",
        ),
        witness_family.Member(
            name="no_name_is_reimplemented_across_two_trees",
            claim="the class that bit: `leverage` was a DAG cone in one tree and a two-grade "
            "reader in another, so a reader who finds one assumes the other's contract",
            premises=("no_name_is_reimplemented_twice_within_one_directory",),
        ),
    ],
)

# The bib key each kind answers for. ⚑ ONE MAPPING, so the witness cannot drift from the roster.
KEYS = {
    name_collision.LOCAL: ("T23-local", "name-collisions-local"),
    name_collision.SIBLING: ("T23-sibling", "name-collisions-sibling"),
    name_collision.CROSSING: ("T23-crossing", "name-collisions-crossing"),
}


def buckets() -> dict[str, tuple[name_collision.Collision, ...]]:
    """Return the corpus's collisions, partitioned by the repair each calls for."""
    return name_collision.by_kind(name_collision.collisions(name_collision.population()))


def sample(rows: tuple[name_collision.Collision, ...], width: int = 5) -> str:
    """Return a short `name xN` sample of a bucket, or `none`."""
    return ", ".join(f"{c.name} x{len(c.sites)}" for c in rows[:width]) or "none"


def witness(key: str, figure: str, kind: str) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Yield one part per colliding name in `kind`, then the verdict.

    ⚑ ONE BODY, N ITEMS — the shape the origin already used. Three witnesses saying the same
    thing about different partitions would be three chances to drift, and the drift would be
    invisible because each would agree with itself.
    """
    if kind not in KEYS:
        yield witness_row.opened(
            key,
            f"{kind!r} is not a partition this census knows "
            f"({', '.join(sorted(KEYS))}) — the claim is UNMEASURED, not satisfied",
        )
        return

    try:
        want = warrant_records.tag(key, figure)
    except WarrantError as exc:
        yield witness_row.opened(key, f"the claim carries no [{figure}=N] tag: {exc}")
        return

    rows = buckets()[kind]
    for got in rows:
        yield witness_row.part(
            key, got.name, route=f"{kind}: {len(got.sites)} site(s) — {got.sites[0].path}"
        )

    if len(rows) != want:
        yield witness_row.opened(
            key,
            f"claim says {want}; the corpus has {len(rows)} `{kind}` collision(s): {sample(rows)}",
        )
        return
    if rows:
        yield witness_row.opened(key, f"{len(rows)} `{kind}` collision(s): {sample(rows)}")
        return
    yield witness_row.closed(key, f"no `{kind}` name collision")


def witness_local(key: str, figure: str) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Yield the verdict for names reimplemented inside one file."""
    return witness(key, figure, name_collision.LOCAL)


def witness_sibling(key: str, figure: str) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Yield the verdict for names reimplemented within one directory."""
    return witness(key, figure, name_collision.SIBLING)


def witness_crossing(key: str, figure: str) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Yield the verdict for names reimplemented across two trees."""
    return witness(key, figure, name_collision.CROSSING)
