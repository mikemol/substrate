#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The sole reach into the engine's private edge roster — one module, one line, one reason.

⚑⚑⚑ THIS EXISTS BECAUSE THE ALTERNATIVE WAS A `noqa` IN A ZERO-TOLERANCE TREE. `SLF001` is right
that reaching for another package's `_`-prefixed name is fragile, and a per-site suppression would
say *"reviewed"* while leaving the fragility spread across every future consumer. Confining it to
one module makes the reach COUNTABLE — the same construction `check_ignore_holder.py` applies to
the numpy `Any` boundary: walled in its own module, sole holder, with concrete returns.

⚑⚑ AND THE REACH IS NECESSARY, NOT CONVENIENT. `_LIST` is the engine's authority on which bib
fields parse as LISTS of keys rather than scalars. The alternative is restating the roster locally
— which was tried and was WRONG: the engine's module docstring names three fields (`from`,
`rests-on`, `reads`) while the constant carries FOUR (`consumes` was added and the prose did not
follow). **The prose about an authority is not the authority.** A local copy reports a
newly-accepted field as engine-dropped: a false finding pointing at correct work.

⚑ THE NAME IS PRIVATE AND THAT IS A REAL RISK, ACCEPTED WITH AN INSTRUMENT. `stubs/paperkit/bib.pyi`
declares `_LIST: tuple[str, ...]` and `scripts/check_stub_authority.py` runs `stubtest` against the
live engine, so an upstream rename fails a GATE rather than silently degrading a census to zero.
That is the trade: depend on a private name, and make the dependency the thing that breaks loudly.

⚑ FILED UPSTREAM RATHER THAN ONLY WORKED AROUND — a consumer needing a private name is a missing
public surface, which is summit's intake shape (⟡engine-edge-roster-public).
"""

from __future__ import annotations

import paperkit.bib

# The engine attribute naming the fields it parses as key LISTS. Named so a reader can find the
# authority without reading past this module.
ENGINE_ATTR = "_LIST"


def edge_fields() -> tuple[str, ...]:
    """Return the bib fields the engine parses as lists of keys.

    ⚑ A FUNCTION, NOT A MODULE CONSTANT, so the read happens at CALL time. A constant binds at
    import and would freeze whatever the engine held when this module first loaded — which is the
    same staleness the local-copy version had, moved one layer in and made harder to see.
    """
    return paperkit.bib._LIST  # noqa: SLF001 — the sole sanctioned reach; see the module docstring
