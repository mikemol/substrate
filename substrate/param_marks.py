#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Render the parameter placeholders a statement needs — one paramstyle, one authority.

⚑⚑⚑ THE PARAMSTYLE WAS BACKEND-SPECIFIC AND WAS BEING SPELLED PER CALL SITE, which is the
defect this exists to make unconstructible. sqlite takes `?`, psycopg takes `%s`, and psycopg
REFUSES the wrong one outright ("the query has 0 placeholders but 1 parameters were passed")
rather than misbinding. Loud, at least — but loud at RUNTIME, at whichever site happened to run.

⚑⚑ AND THE FUNCTION THAT FIXED THE PER-SITE SPELLING ONCE CARRIED THE DEFECT ONE LEVEL UP,
which is the measured reason there is no backend parameter here. The retired signature took a
`back` argument resolving to `back or store.backend()` — the AMBIENT backend, an environment
variable — while the placeholder it returns is bound to a specific CONNECTION. Those two can
disagree, and every time they did the failure was the same: a postgres ambient emitting `%s`
into a sqlite cursor, or a sqlite ambient emitting `?` into a psycopg one. FOUR recorded
occurrences, and the tell was a fixture that had to pin the backend BY HAND to work around the
parameter's own defect — a parameter whose only user in the corpus was a workaround for itself.

⚑ REMOVING THE PARAMETER RATHER THAN IGNORING IT. An accepted-and-ignored backend argument
still reads, at every call site, as though the backend were selectable there — which is exactly
how the branch gets re-added by the next reader. Passing one is a `TypeError` here: loud, at the
one place that could reintroduce the disagreement, and before anything reaches a cursor.

⚑⚑ MEASURED BEFORE THE PARAMETER WAS REMOVED, AND THE TWO MEASUREMENTS DISAGREED IN A WAY WORTH
KEEPING. A keyword-shaped census reported ZERO call sites forwarding it — which reads as
"nothing uses it". But the parameter was also passed POSITIONALLY, and a literal-shaped census
found those. Same population, two spellings, and the first census could not see the second: a
fact about the METHOD reported as a fact about the substrate. The conclusion held; the evidence
for it did not, until it was asked the other way.

⚑ IT IS PURE AND REACHES FOR NOTHING. No connection, no declaration, no ambient state — so a
caller can build a statement with postgres unreachable, and every case here runs offline. A
placeholder renderer that had to ask the environment which style to emit would be reintroducing
the ambient the removed parameter carried.
"""

from __future__ import annotations

#: The one paramstyle this store speaks. ⚑ NAMED RATHER THAN INLINED so the fact that there is
#: exactly ONE has a place to be read, rather than being implied by a literal in a join.
MARK = "%s"

#: How the placeholders are joined into a `VALUES (...)` list.
SEPARATOR = ", "

#: The fewest placeholders a statement can ask for. ⚑ ZERO IS LEGAL AND MEANS THE EMPTY STRING:
#: a statement with no parameters is a real statement, and refusing it here would push the caller
#: into an `if` that spells the empty case by hand — the per-site branch this module removes.
MINIMUM = 0


def marks(n: int = 1) -> str:
    """Return `n` parameter placeholders, comma-separated and ready to interpolate.

    ⚑ A NEGATIVE COUNT REFUSES RATHER THAN RENDERING EMPTY. `["%s"] * -1` is the empty list in
    Python, so a caller that computed its arity wrong would receive a syntactically plausible
    statement with no placeholders and learn about it from the driver, several frames away and
    naming neither the arity nor its source. Refusing here names the count that was wrong.
    """
    if n < MINIMUM:
        msg = (
            f"marks({n}): a placeholder count cannot be negative. Rendering it would silently "
            f"produce the empty string, which composes a statement the driver rejects for a "
            f"reason naming neither this count nor where it came from."
        )
        raise ValueError(msg)
    return SEPARATOR.join([MARK] * n)
