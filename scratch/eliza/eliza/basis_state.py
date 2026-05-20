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


class QuaternionComponent(IntEnum):
    """The four fundamental quaternion components.

    V2 relative-bearing opcode: each emission of S_BASIS_BY carries
    one of these as a single-bit-per-component selector. Cumulative
    multiplication generates the quaternion group Q_8 = {±1, ±i, ±j,
    ±k}, which acts as V₄ in SO(3) (180° rotations about coordinate
    axes).

    Per the substrate identification: 90°-rotations-around-axes
    generate the octahedral group ≅ S₄ — the same group the chain
    walk operates on. The basis-bearing walk reuses the chain
    machinery.
    """

    W = 0      # real (identity contribution)
    I = 1      # x-axis 90° rotation generator
    J = 2      # y-axis
    K = 3      # z-axis


@dataclass(frozen=True)
class BasisState:
    """The codec's current basis state.

    V1: label. V2: + quaternion accumulator (an integer 0..7 indexing
    Q_8 = {1, -1, i, -i, j, -j, k, -k}). Cumulative multiplication
    by quaternion-component opcodes drives the rotation state.
    """

    label: BasisLabel = DEFAULT_BASIS
    quat: int = 0           # Q_8 index ∈ [0, 8); 0 = identity quaternion

    def is_default(self) -> bool:
        return self.label == DEFAULT_BASIS and self.quat == 0


IDENTITY = BasisState()


# Q_8 multiplication table indexed by Q_8 index.
# Q_8 elements ordered: 0=1, 1=-1, 2=i, 3=-i, 4=j, 5=-j, 6=k, 7=-k.
# Cayley table _Q8_MUL[a, b] = a · b.
_Q8_MUL = (
    (0, 1, 2, 3, 4, 5, 6, 7),
    (1, 0, 3, 2, 5, 4, 7, 6),
    (2, 3, 1, 0, 6, 7, 5, 4),
    (3, 2, 0, 1, 7, 6, 4, 5),
    (4, 5, 7, 6, 1, 0, 2, 3),
    (5, 4, 6, 7, 0, 1, 3, 2),
    (6, 7, 4, 5, 3, 2, 1, 0),
    (7, 6, 5, 4, 2, 3, 0, 1),
)


def quat_multiply(a: int, b: int) -> int:
    """Multiply two Q_8 elements (by index)."""
    return _Q8_MUL[a][b]


def apply_quat_component(quat: int, component: int) -> int:
    """Multiply current quaternion by a fundamental component (W/I/J/K).

    Component ∈ {0, 1, 2, 3} ↦ Q_8 index {0, 2, 4, 6} (the positive
    fundamentals). Returns the updated quaternion index.
    """
    pos_q8 = (0, 2, 4, 6)[component]
    return quat_multiply(quat, pos_q8)
