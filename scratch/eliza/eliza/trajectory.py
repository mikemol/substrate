"""Eliza.Trajectory — walk + period detection.

Implements:

  * `walk(gens, start)`: Word Gen → Chamber → Word Chamber. Folds the
    manifold's `apply` over a sequence of generators.

  * `detect_period(traj)`: the local HasOrder witness — smallest k > 0
    such that traj[-1-k] == traj[-1], else None.

Per the Agda contract, these depend only on the Manifold's `apply`; no
spectral, orbit, or recorder data leaks in here.
"""

from __future__ import annotations

from typing import List, Optional, Sequence

from eliza.alphabets import Chamber, Gen
from eliza.manifold import apply


def walk(gens: Sequence[Gen], start: Chamber) -> List[Chamber]:
    """Successive chambers after applying each generator. The first
    output is `apply(gens[0], start)`, NOT `start` itself."""
    out: List[Chamber] = []
    x = start
    for g in gens:
        x = apply(g, x)
        out.append(x)
    return out


def endpoint(gens: Sequence[Gen], start: Chamber) -> Chamber:
    """Final chamber after walking. O(len(gens))."""
    x = start
    for g in gens:
        x = apply(g, x)
    return x


def detect_period(trajectory: Sequence[Chamber]) -> Optional[int]:
    """Smallest k ≥ 1 with trajectory[-1-k] == trajectory[-1]; None if
    no such k within the window. The local Z/k cyclic witness on the
    recent walk; per Substrate.Category.Coalgebra.FiniteOrder, this is
    the runtime trace of `HasOrder γ k`."""
    n = len(trajectory)
    if n < 2:
        return None
    current = trajectory[-1]
    for k in range(1, n):
        if trajectory[-1 - k] == current:
            return k
    return None
