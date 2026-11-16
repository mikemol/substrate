#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""What a ratchet gate HOLDS, and how much of it is over baseline.

⚑⚑ `added` IS WHAT A RATCHET REFUSES ON, and `held` is the census size. The two are different
questions and a report giving only one is unactionable: `held` alone cannot say whether anything
is new, and `added` alone hides whether the population is 3 keys or 3,000.

⚑⚑⚑ A GATE WHOSE BASELINE FILE IS ABSENT REPORTS `added == held`, WHICH IS THE HONEST READING.
With nothing recorded, every key is new. That is why a zero-byte baseline reports a LEVEL rather
than a delta — and it is the opposite of the free pass an absent baseline gives elsewhere in this
tree, where a missing file takes the record-and-pass branch and exits 0 regardless of what it
measured.

⚑ AN UNMEASURABLE CENSUS IS NOT A CLEAN ONE. Every failure path returns a REASON — the gate would
not import, exposes no census, raised, declared itself unrunnable — because a refusal that cannot
say what it hit is a guard degraded to measuring nothing. A caller reporting "0 added" for a gate
it could not read has banked a false green.

⚑ THE KEY PARTITION IS A SEPARATE MODULE. A census key is `<field>::<field>[::<field>]` with
exactly one PATH field whose position differs per gate, and that schema lives in a file this one
does not import: pulling it in would drag an untyped `namedtuple` — and its module's findings —
through this file's own type check.

⚑ A GATE IS AN ARBITRARY MODULE, SO EVERY READ OF ONE IS AN UNTYPED BOUNDARY. `census()` and
`BASELINE` are narrowed here, at the seam, rather than letting an unchecked attribute read carry
`Any` into the comparison that decides whether a gate is at baseline.

⚑ EXTRACTED FROM `catalog/library/figures.py` (⟡items-n-split), which is dirty and cannot be
edited. Six ratchet witnesses depend on this census.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from substrate import gate_module

# The sentinel a census uses to declare that it cannot run in this environment.
_UNRUNNABLE = "__unrunnable__"

# The container types a census may return. ⚑ A `dict` COUNTS: several gates return `{key: why}`
# and iterating one yields its keys, which is the census.
_KEY_SETS = (dict, set, frozenset, list, tuple)


@dataclass(frozen=True, slots=True)
class Census:
    """One gate's census: how many keys it holds, and which are over baseline."""

    held: int
    added: tuple[str, ...]

    @property
    def over(self) -> int:
        """How many keys are over baseline — what the ratchet refuses on."""
        return len(self.added)


def baseline_keys(path: str | None) -> set[str]:
    """Return the recorded baseline's keys, or an empty set when there is no file.

    ⚑ AN ABSENT BASELINE IS AN EMPTY SET, NOT A REFUSAL. Every key then reads as added, which is
    the honest state: nothing has been recorded, so nothing is grandfathered.
    """
    if not path:
        return set()
    file = Path(path)
    if not file.exists():
        return set()
    return {line.strip() for line in file.read_text(encoding="utf-8").splitlines() if line.strip()}


def baseline_path(mod: object) -> str | None:
    """Return a gate's declared baseline path, narrowed to text.

    ⚑ NARROWED AT THE SEAM. `getattr` on an arbitrary module returns `Any`; a gate declaring a
    `BASELINE` that is not a path string is reported as having none, rather than reaching the
    filesystem with whatever it declared.
    """
    declared: object = getattr(mod, "BASELINE", None)
    return declared if isinstance(declared, str) else None


def _keys_of(mod: object) -> tuple[set[str] | None, str | None]:
    """Call one gate's census and narrow its result to a key set, or say why not."""
    reader: object = getattr(mod, "census", None)
    if not callable(reader):
        return None, "module exposes no census() — not a set-form ratchet"

    try:
        current: object = reader()
    except BaseException as exc:  # noqa: BLE001 — a census may exit or raise anything
        return None, f"census() raised {type(exc).__name__}: {exc}"

    if current is None:
        return None, "census() returned None"
    if isinstance(current, dict) and _UNRUNNABLE in current:
        return None, "census declared itself UNRUNNABLE"
    if not isinstance(current, _KEY_SETS):
        return None, f"census() returned {type(current).__name__}, which is not a key set"

    return {str(key) for key in current}, None


def census(name: str) -> tuple[Census | None, str | None]:
    """Return `(census, None)` or `(None, why)` for one gate by name."""
    mod, why = gate_module.gate_module(name)
    if mod is None:
        return None, why

    keys, why = _keys_of(mod)
    if keys is None:
        return None, why

    base = baseline_keys(baseline_path(mod))
    return Census(held=len(keys), added=tuple(sorted(keys - base))), None
