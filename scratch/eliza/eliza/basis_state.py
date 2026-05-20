"""Eliza.BasisState — the codec's current basis, modeled as a torsor.

V-arc structural pivot per the user's design iteration:

  * The codec's "current basis" is an element of a torsor over the
    basis-change Lie group (block-diagonal under S₄'s irrep
    decomposition).
  * No basis is privileged as "the home" — algebraic chambers and
    Laplacian eigenbasis are both labeled points in the same torsor.
  * Two complementary access patterns:
      - Heading (absolute): `S_BASIS_AT(label)` — jump to a named point.
      - Bearing (relative): `S_BASIS_BY(quaternion-word)` — apply a
        group element to current state. (V2 lands the relative form.)

V1 implements only the labeled-point set + absolute jump. The encoder
defaults to ALGEBRAIC and never emits S_BASIS_AT; V7 reproduces V6
exactly. Subsequent V-slices wire the basis-state into emission
semantics.

The basis-state is purely metadata at V1 — emissions are still
interpreted in chamber-label coordinates. V3 wires it into the
adaptive predictor's alphabet selection.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class BasisLabel(IntEnum):
    """Labeled points in the basis-torsor.

    These are the discrete labels the codec's current-basis state can
    take. The relevant group acts continuously between them; V1 only
    exposes the discrete labels (heading), V2 will add relative
    transitions (bearing).

    Default: ALGEBRAIC = chamber-label basis, the current V6 reading.
    """

    ALGEBRAIC      = 0    # S₄ chambers as labels (V6 default).
    SPECTRAL       = 1    # Laplacian eigenvector coordinates.
    ISOTYPIC_TRIV  = 2    # Trivial-irrep projection (1d).
    ISOTYPIC_SIGN  = 3    # Sign-irrep projection (1d).
    ISOTYPIC_STD   = 4    # Standard 3d-irrep projection.
    ISOTYPIC_STDSGN = 5   # Standard ⊗ sign (3d).
    ISOTYPIC_2D    = 6    # 2d irrep projection.


N_BASIS_LABELS = 7

DEFAULT_BASIS = BasisLabel.ALGEBRAIC


@dataclass(frozen=True)
class BasisState:
    """The codec's current basis state.

    V1: just a label. V2 will add a quaternion-word component to
    track relative rotations within the Lie-group block of the
    current label.
    """

    label: BasisLabel = DEFAULT_BASIS

    def is_default(self) -> bool:
        return self.label == DEFAULT_BASIS


IDENTITY = BasisState()
