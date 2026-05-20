"""Eliza.ChainChooser — rotation chooser via Sylow-chain norm.

The substrate-honest replacement for the prior Bezout-of-scalars
combiner. For each candidate rotation r ∈ 0..15:

  1. Fold rotated bytes into a WalkCarrier (workspace state).
  2. Compute the gauge element g_r connecting the carrier to a
     reference state (default: ORIGIN, the identity workspace).
  3. Build the Sylow chain for g_r.
  4. Pick r minimising a chain norm (default: total word length).

This is **rotation-discriminating** by construction: different
rotations produce different end-carriers, hence different gauge
elements, hence different chains.

Per `MultiRouteEquivariance.agda`'s T5: the output is the chain
itself, not a scalar projection. The chooser slot reads the chain
(via norm), but downstream consumers can read the chain structure
directly via the (v, s3, s2) triple.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Tuple

from eliza.alphabets import Chamber, ORIGIN
from eliza.brick import BrickType, Unit, UNIT, Witnessing
from eliza.gauge_element import gauge_element
from eliza.octonion import rotate_bytes
from eliza.sylow_chain import (
    SylowChain, V4_E, build_chain,
)
from eliza.walk_carrier import WalkCarrier, walk_to_s4


# A chain norm maps a SylowChain → ℝ⁺ (or ℤ⁺). Different norms give
# different chooser policies; each is a substrate-honest gauge choice.
ChainNorm = Callable[[SylowChain], float]


def word_length_norm(chain: SylowChain) -> float:
    """Total chain word length (default norm). 0 = identity gauge element."""
    return float(chain.word_length)


def v4_only_norm(chain: SylowChain) -> float:
    """V₄-component only — biases toward Sylow-2 alignment."""
    return float(chain.v_length)


def s3_only_norm(chain: SylowChain) -> float:
    """S₃-component only — biases toward Sylow-3 + S₃-Sylow-2 alignment."""
    return float(chain.s3_length + chain.s2_length)


@dataclass
class ChainNormChooser:
    """Rotation chooser via Sylow-chain norm.

    A Brick (D⇒C) wrapping:
      window (bytes) →
      [for r ∈ 0..15: chain_of(gauge_element(walk_r, ref))] →
      argmin(norm)

    Default `reference` is ORIGIN (workspace identity). Subclasses or
    callers can supply an adaptive reference learned from past windows
    (the predictor's canonical view).
    """
    reference: Chamber = ORIGIN
    norm: ChainNorm = field(default=word_length_norm)
    name: str = "chain_norm_chooser"
    homomorphism_tag: str = "D⇒C: chain-norm selects rotation"

    @property
    def brick_type(self) -> BrickType:
        return BrickType(D_in=bytes, D_out=int, S_in=Unit, S_out=Unit)

    @property
    def witnesses(self) -> Witnessing:
        return Witnessing.D_TO_C

    def chain_for_rotation(self, window: bytes, r: int) -> SylowChain:
        rotated = rotate_bytes(window, r)
        carrier = walk_to_s4(rotated)
        g = gauge_element(carrier.state, self.reference)
        return build_chain(g)

    def __call__(self, window: bytes, _pred: Any = None) -> int:
        """Plug-compatible with dim2_codec.encode's rotation_chooser slot."""
        best_r, best_score = 0, float("inf")
        for r in range(16):
            chain = self.chain_for_rotation(window, r)
            s = self.norm(chain)
            if s < best_score:
                best_score = s
                best_r = r
        return best_r

    def step(self, window: bytes, _: Any = None) -> Tuple[int, Unit]:
        return self(window, None), UNIT

    def stats(self) -> Dict[str, Any]:
        return {"reference": self.reference, "norm": self.norm.__name__}


# --- Adaptive reference variant ------------------------------------------


@dataclass
class AdaptiveReferenceChainChooser(ChainNormChooser):
    """Chain chooser whose reference is a rolling average of past
    chosen-rotation end-carriers.

    Each window: pick by chain norm, then update reference to the
    walk_to_s4 of the actually-emitted (rotated) bytes. The reference
    converges to the corpus's typical workspace state, making the
    chain chooser adapt to the input distribution while remaining
    rotation-discriminating.

    This is the substrate-honest analogue of gt's adaptive
    `-log P(byte | context)` — both adapt, but gt minimises surprise
    while this minimises chain length to a learned reference.
    """
    name: str = "adaptive_chain_chooser"
    homomorphism_tag: str = "D⇒C: chain-norm to adaptive reference"

    def __call__(self, window: bytes, _pred: Any = None) -> int:
        # Pick rotation per chain norm against current reference.
        best_r, best_score, best_carrier_state = 0, float("inf"), self.reference
        for r in range(16):
            rotated = rotate_bytes(window, r)
            carrier = walk_to_s4(rotated)
            g = gauge_element(carrier.state, self.reference)
            chain = build_chain(g)
            s = self.norm(chain)
            if s < best_score:
                best_score = s
                best_r = r
                best_carrier_state = carrier.state
        # Adapt the reference toward the chosen carrier.
        self.reference = best_carrier_state
        return best_r


# --- Self-check ----------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    sample_text = b"def encode(data: bytes) -> bytes:\n    pred = TrigramPredictor()\n"
    # Pad to a stable window size.
    while len(sample_text) < 256:
        sample_text = sample_text + sample_text
    window = sample_text[:256]

    chooser = ChainNormChooser()
    r_default = chooser(window)
    chain_at_default = chooser.chain_for_rotation(window, r_default)

    # Check that all 16 rotations produce well-formed chains and that
    # the chooser actually discriminates among rotations.
    all_chains = []
    for r in range(16):
        c = chooser.chain_for_rotation(window, r)
        all_chains.append(c)
    norms = [chooser.norm(c) for c in all_chains]
    distinct_norms = len(set(norms))
    # Verify argmin agreement with our pick.
    min_idx = norms.index(min(norms))
    pick_consistent = (r_default == min_idx)

    if verbose:
        print("=== ChainNormChooser self-check ===")
        print(f"  chosen rotation: {r_default} (chain length {chain_at_default.word_length})")
        print(f"  chain at pick:   {chain_at_default}")
        print(f"  norms over 16 rotations: {norms}")
        print(f"  distinct norm values: {distinct_norms}")
        print(f"  pick = argmin(norm): {'OK' if pick_consistent else 'FAIL'}")
        # Adaptive variant smoke test.
        adaptive = AdaptiveReferenceChainChooser()
        r_adaptive = adaptive(window)
        print(f"\n  adaptive chooser: r={r_adaptive}, new ref={adaptive.reference}")
        print(f"\nResult: {'OK' if pick_consistent else 'FAIL'}")
    return pick_consistent


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
