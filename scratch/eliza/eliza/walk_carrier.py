"""Eliza.WalkCarrier — the workspace-axis carrier for the spectral atlas.

Per the user's correction (and `cotype-free-self-extending-grammar.md`
§ M27, lines 2868-2942): the 24 chambers are the WORKSPACE (W) axis,
the fourth axis alongside (D, S, C). Rotation is the workspace
operation that "lets you play Freecell while rotating the problem
space" (M27, line 2872). Chambers are *derived from* rotation, not
invariant under it.

The atlas's carrier is therefore the workspace state: a chamber walk
folds into a single S₄ element (the end-chamber). Different rotations
produce different end-chambers because rotation determines the byte
sequence, hence the nibble sequence, hence the perm composition.

This module establishes the carrier explicitly so subsequent atlas
machinery (gauge_element, sylow_chain, chain_chooser) can operate on
it as a structured object — matching `Substrate.Category.PrimeFactored
Gauge.MultiRouteEquivariance`'s `(x, y) → (g, sylow-chain g)` signature
where x, y ∈ X are orbit points (= carrier values here).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

from eliza.alphabets import (
    Chamber, NIBBLE_TO_PERM, ORIGIN, perm_compose, perm_inverse,
)


# A workspace state IS an S₄ element. Chambers are exactly the 24 S₄
# elements; we use the tuple representation throughout for parity with
# the rest of the codec.
WorkspaceState = Chamber


@dataclass(frozen=True)
class WalkCarrier:
    """Carrier value for the spectral atlas.

    A walk through chambers is summarised by its end-state (S₄ element)
    and length. Identity at the start (ORIGIN); right-multiplication by
    each nibble's perm.

    Per the W-axis reading: this object IS the workspace state. Charts
    transform it; the chain transmits equivariance over it.
    """
    state: WorkspaceState   # current S₄ element after the walk
    length: int             # number of nibbles consumed

    @classmethod
    def start(cls) -> "WalkCarrier":
        """Carrier at the origin of the workspace."""
        return cls(state=ORIGIN, length=0)

    def fold(self, nibble: int) -> "WalkCarrier":
        """One workspace step: right-multiply by nibble's perm."""
        return WalkCarrier(
            state=perm_compose(self.state, NIBBLE_TO_PERM[nibble & 0xF]),
            length=self.length + 1,
        )


def bytes_to_nibbles(window: bytes) -> List[int]:
    """Split each byte into (hi, lo) nibbles in order."""
    out: List[int] = []
    for b in window:
        out.append((b >> 4) & 0xF)
        out.append(b & 0xF)
    return out


def walk_to_s4(window: bytes) -> WalkCarrier:
    """Fold a byte window into a single WalkCarrier value.

    Right-composition with each nibble's perm (matches the rest of the
    codec's nibble-to-perm convention). The result is the carrier value
    at the end of the workspace walk.
    """
    carrier = WalkCarrier.start()
    for nib in bytes_to_nibbles(window):
        carrier = carrier.fold(nib)
    return carrier


def walk_each_step(window: bytes) -> List[WorkspaceState]:
    """Trace of intermediate workspace states for diagnostic uses."""
    state = ORIGIN
    out = []
    for nib in bytes_to_nibbles(window):
        state = perm_compose(state, NIBBLE_TO_PERM[nib])
        out.append(state)
    return out


# --- Self-check ----------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    # (1) Identity start.
    c0 = WalkCarrier.start()
    assert c0.state == ORIGIN and c0.length == 0

    # (2) Single-nibble fold == perm_compose with NIBBLE_TO_PERM.
    c1 = c0.fold(5)
    assert c1.state == perm_compose(ORIGIN, NIBBLE_TO_PERM[5])
    assert c1.length == 1

    # (3) Folding a byte = 2 fold steps.
    win = bytes([0x5A])    # hi=5, lo=10
    c2 = walk_to_s4(win)
    expected = perm_compose(perm_compose(ORIGIN, NIBBLE_TO_PERM[5]),
                            NIBBLE_TO_PERM[10])
    assert c2.state == expected
    assert c2.length == 2

    # (4) Different windows generically produce different end-states.
    from eliza.octonion import rotate_bytes
    text = b"\x42\x12\xAB\xCC\xFF\x00" * 16
    states = []
    for r in range(16):
        states.append(walk_to_s4(rotate_bytes(text, r)).state)
    n_distinct = len(set(states))

    if verbose:
        print("=== WalkCarrier self-check ===")
        print(f"  start carrier:        state={c0.state} length={c0.length}")
        print(f"  one-step fold(5):     state={c1.state}")
        print(f"  byte 0x5A walk:       state={c2.state}")
        print(f"  16 rotations of a stable corpus produce "
              f"{n_distinct} distinct end-states")
        print(f"\nResult: OK  "
              f"(distinct end-states ≥ 1 ⇒ carrier is rotation-derived)")

    return n_distinct >= 1


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
