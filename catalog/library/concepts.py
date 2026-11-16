#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The keyed witness library: one worklist key to the reader that answers it.

⚑⚑⚑ THE ROSTER AND THE CLAIMS MUST NOT SHARE A HOME, AND THAT IS THE ITEM. While every witness
was defined in the dispatch module, the file saying WHICH items exist was the file saying WHAT
each measures — so it grew to 2,736 lines carrying 1,804 findings, and the per-file gate then
refused every edit to it. **A module that cannot be edited cannot be repaired**, which is how a
roster and its witnesses become one uneditable artifact.

⚑⚑ SO THIS FILE HOLDS DISPATCH, NOT BODIES. Two tables answer between them: `concept_bindings`
for readers that produce a RENDERING, framed into rows by `concept_rows`; `concept_families` for
readers that emit rows directly. A witness is added by writing a module and binding it in one of
those — never by growing this file, which is what the origin's shape made unavoidable.

⚑⚑ THE TWO TABLES ARE NOT A DUPLICATION, AND THE CHECKER IS WHAT ESTABLISHED THAT. A reader
either renders or emits rows; binding a rendering-shaped module as a row emitter was refused with
*"module has no attribute render"*, and the reverse would re-derive a verdict the reader already
reached. **One dispatch over two shapes, rather than one shape imposed on every reader.**

⚑ A KEY BOUND IN BOTH TABLES IS A DEFECT, NOT A PREFERENCE. Two readers for one key would answer
the same question twice and drift; the overlap is reported rather than silently resolved by
lookup order.

⚑ AN UNBOUND KEY IS UNMEASURED, NEVER SATISFIED. Returning nothing would let a key nobody answers
read as a clean item — the false green this whole family exists to refuse.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mikemol.witness import witness_row

from substrate import concept_bindings, concept_families, concept_rows

if TYPE_CHECKING:
    from collections.abc import Iterator


def keys() -> tuple[str, ...]:
    """Return every key this library answers, sorted."""
    return tuple(sorted({*concept_bindings.bound_keys(), *concept_families.bound_keys()}))


def overlapping() -> tuple[str, ...]:
    """Return keys both tables claim to answer.

    ⚑ TWO READERS FOR ONE KEY IS A DEFECT. They would answer the same question twice and drift
    apart, with lookup order deciding which verdict a caller sees — so the overlap is a reported
    fact rather than a silent resolution.
    """
    return tuple(sorted(set(concept_bindings.bound_keys()) & set(concept_families.bound_keys())))


def witness(key: str) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Yield the rows for one key.

    ⚑ THE FAMILY TABLE IS ASKED FIRST because its readers emit rows directly; the rendering table
    is the adapted path. With no overlap the order is immaterial, and `overlapping()` is what
    makes that checkable rather than assumed.
    """
    if concept_families.family(key) is not None:
        yield from concept_families.rows(key)
        return

    found = concept_bindings.reading(key)
    if found is None:
        yield witness_row.opened(
            key,
            f"{key!r} is registered but no witness is bound in the keyed library — "
            f"the claim is UNMEASURED, not satisfied",
        )
        return

    text = found()
    yield from concept_rows.from_render(key, text, concept_rows.marked(text))


def unbound(registered: tuple[str, ...]) -> tuple[str, ...]:
    """Return the registered keys this library cannot answer.

    ⚑ THE ROSTER IS THE CALLER'S, NOT THIS FILE'S. Holding a second copy of what exists is exactly
    the roster-beside-a-roster shape the split is removing — the dispatch answers about the keys
    it is asked about.
    """
    return tuple(sorted(set(registered) - set(keys())))
