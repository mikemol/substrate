# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Build a gate's `key_move` from its declared key grammar, rather than by hand.

⚑⚑⚑ THE MECHANISM ALREADY EXISTS AND EXACTLY ONE GATE USES IT. `set_ratchet` takes a
`key_move` and `partition` calls `split_moves` with it, so a decomposition that relocates a
key is credited as a MOVE rather than as one paydown plus one addition — and `rule` records
a baseline on a move-only run. All of that is built. But `--calls key_move` reports ONE
supplying gate (`check_public_ratchet`), so every other ratchet reads a file split as
growth and refuses, and the paydown that split earned cannot record behind it.

⚑⚑ AND THE ONE INSTANCE IS A HAND-WRITTEN LAMBDA — `lambda k: k.split("::", 1)[1]`. It is
correct for a path-first key and SILENTLY WRONG for a reversed one: the sumtype census
emits `name::relpath`, where that same expression returns the PATH as the identity, so
every relocation looks like a genuine violation and every genuine violation at a shared
name looks like churn. Copying the lambda to the other six gates would have propagated a
grammar assumption that holds for four of them. The schema already knows which field is the
path; deriving from it cannot make that error.

⚑ THE IDENTITY IS JOINED BACK INTO A STRING because `set_ratchet`'s contract is
`Callable[[str], str]` — a key maps to the token two keys share when one moved. The
separator is the gate's own, so a gate keying on something other than `::` needs a schema
entry rather than a change here.

⚑⚑ A MALFORMED KEY MAPS TO ITSELF, DELIBERATELY, AND THAT IS THE CONSERVATIVE DIRECTION. A
baseline written before a grammar settled may hold a key of the wrong arity, and `parse`
refuses it. Refusing inside `key_move` would abort the gate — turning a stale baseline line
into a crash — while a key that is its own identity simply pairs with nothing and stays
reported as growth. ⚑ AN UNPARSEABLE KEY IS THEREFORE NEVER ABSOLVED AS CHURN, which is the
error direction that matters: absolving real debt is unrecoverable, reporting churn as debt
costs one operator read.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from substrate import ratchet_key

if TYPE_CHECKING:
    from collections.abc import Callable


def move_of(gate: str, key: str) -> str:
    """Return the token `key` shares with the same violation at another path."""
    spec = ratchet_key.SCHEMA[gate]
    try:
        ident = ratchet_key.identity(gate, key)
    except ratchet_key.MalformedKeyError:
        return key
    return spec.sep.join(ident)


def key_move(gate: str) -> Callable[[str], str]:
    """Return the `key_move` for `gate`, ready to hand to `set_ratchet`.

    ⚑ THE GATE NAME IS VALIDATED NOW, NOT AT THE FIRST KEY. An undeclared gate would
    otherwise raise once per key from inside the ratchet's comparison, where the failure
    reads as a census defect rather than as a caller naming a gate that does not exist.
    """
    if gate not in ratchet_key.SCHEMA:
        msg = f"{gate!r} is not a declared gate; have {', '.join(ratchet_key.GATES)}"
        raise KeyError(msg)
    return lambda key: move_of(gate, key)
