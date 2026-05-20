"""Eliza.GaugeElement — `gauge_element(x, y)` extractor.

Mirrors `Substrate.Category.PrimeFactoredGauge.MultiRouteEquivariance::
gauge-element`. Given two orbit points x, y ∈ X (workspace states /
WalkCarrier values), return the gauge element g ∈ G with
`act g x ≡ y`.

For our codec instance: X = S₄ (workspace states) and the torsor
action is LEFT multiplication. Then `act g x = g · x`, so
`g · x = y ⇒ g = y · x⁻¹`.

This realises the existence part of `multi-route-equivariance`:
the gauge element exists and is uniquely determined by (x, y).
(The Sylow-chain decomposition of g lives in sylow_chain.py.)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from eliza.alphabets import Chamber, perm_compose, perm_inverse
from eliza.walk_carrier import WalkCarrier, WorkspaceState


def gauge_element(x: WorkspaceState, y: WorkspaceState) -> Chamber:
    """The unique g ∈ S₄ with g · x = y under left multiplication.

    g = y · x⁻¹.
    """
    return perm_compose(y, perm_inverse(x))


def act(g: Chamber, x: WorkspaceState) -> WorkspaceState:
    """Left torsor action of S₄ on workspace states: act g x = g · x."""
    return perm_compose(g, x)


# --- Convenience for WalkCarrier values ----------------------------------


def gauge_between_carriers(x: WalkCarrier, y: WalkCarrier) -> Chamber:
    return gauge_element(x.state, y.state)


# --- Self-check ----------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    from eliza.alphabets import ORIGIN
    from eliza.manifold import Manifold

    m = Manifold()
    chambers = m.nodes

    # (1) Identity case: gauge_element(x, x) ≡ ORIGIN.
    for x in chambers:
        g = gauge_element(x, x)
        assert g == ORIGIN, f"gauge_element(x, x) != ORIGIN for x={x}: got {g}"

    # (2) Existence: act(gauge_element(x, y), x) ≡ y for all (x, y).
    failed_existence = 0
    for x in chambers:
        for y in chambers:
            g = gauge_element(x, y)
            if act(g, x) != y:
                failed_existence += 1

    # (3) The gauge element is itself an S₄ element (in the chamber set).
    seen = set()
    for x in chambers[:6]:
        for y in chambers[:6]:
            g = gauge_element(x, y)
            assert g in chambers, f"gauge element {g} not in S₄"
            seen.add(g)

    if verbose:
        print("=== GaugeElement self-check ===")
        print(f"  identity case (g(x,x) = ORIGIN): {len(chambers)} chambers OK")
        print(f"  existence failures: {failed_existence} / {len(chambers)**2}")
        print(f"  sampled gauge elements (6×6 pairs): {len(seen)} distinct")
        print(f"\nResult: {'OK' if failed_existence == 0 else 'FAIL'}")
    return failed_existence == 0


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
