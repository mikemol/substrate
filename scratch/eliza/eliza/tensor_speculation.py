"""Eliza.TensorSpeculation — stack-machine state + batched speculation as tensors.

M6+M7+M8 of the homoiconic matricisation arc.

Stack-machine state tensor:
  * stack: (C, max_depth, 2) — C candidates, depth-d stack, (rewrite, observe)
  * depth_ptr: (C,) int — current top index per candidate

Speculation batch tensor:
  * candidates: (C, max_remainder, 2) — per-candidate sequence of
                (emit_idx, advance) per simulated step
  * costs: (C,) float — total bits per candidate

Parallel cost estimation:
  * given a batched simulation, sum bits along axis 1 to get per-candidate
    total; argmin selects the winner. On GPU this is a single reduction.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np


@dataclass
class StackTensor:
    """Stack-machine state for C candidate paths.

    Shape conventions:
      stack: (C, max_depth, 2) int8 — entry layout (rewrite_mode, observe_mode)
      depth: (C,) int — depth pointer per candidate (top = depth-1)
    """
    stack: np.ndarray         # (C, max_depth, 2) int8
    depth: np.ndarray         # (C,) int64

    @property
    def n_candidates(self) -> int:
        return self.stack.shape[0]

    @classmethod
    def initial(cls, n_candidates: int, max_depth: int = 8) -> "StackTensor":
        stack = np.zeros((n_candidates, max_depth, 2), dtype=np.int8)
        stack[:, 0, 0] = 1   # rewrite_mode = 1
        stack[:, 0, 1] = 1   # observe_mode = 1
        depth = np.ones((n_candidates,), dtype=np.int64)
        return cls(stack=stack, depth=depth)

    def top_modes(self) -> np.ndarray:
        """Get the top (rewrite, observe) tuple per candidate.

        Returns (C, 2) int8.
        """
        C = self.n_candidates
        result = np.zeros((C, 2), dtype=np.int8)
        for c in range(C):
            d = int(self.depth[c]) - 1
            if d < 0:
                continue
            result[c] = self.stack[c, d]
        return result

    def apply_toggle(self, candidate_mask: np.ndarray, axis: int) -> "StackTensor":
        """For each candidate where mask[c] = True, XOR the top entry's
        `axis` bit (0 = rewrite, 1 = observe).

        Tensor op: top entry indexed by depth-1; XOR with mask.
        """
        new_stack = self.stack.copy()
        for c in range(self.n_candidates):
            if not candidate_mask[c]:
                continue
            d = int(self.depth[c]) - 1
            if d < 0:
                continue
            new_stack[c, d, axis] ^= 1
        return StackTensor(stack=new_stack, depth=self.depth.copy())


@dataclass
class SpeculationBatch:
    """Per-candidate accumulated cost and emission log.

    For C candidate paths × at-most max_steps simulated emissions.
    """
    costs: np.ndarray              # (C,) float — running cost in bits
    emissions: np.ndarray          # (C, max_steps) int64 — emit_idx per step
    n_steps: np.ndarray            # (C,) int64 — how many steps each used
    stream_positions: np.ndarray   # (C,) int64 — position in input stream

    @classmethod
    def initial(cls, n_candidates: int, max_steps: int,
                start_pos: int = 0) -> "SpeculationBatch":
        return cls(
            costs=np.zeros((n_candidates,), dtype=np.float64),
            emissions=np.full((n_candidates, max_steps), -1, dtype=np.int64),
            n_steps=np.zeros((n_candidates,), dtype=np.int64),
            stream_positions=np.full((n_candidates,), start_pos, dtype=np.int64),
        )


def reduce_winner(batch: SpeculationBatch) -> int:
    """Parallel reduction: argmin over candidate costs."""
    return int(np.argmin(batch.costs))


# --- Self-check ---------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    # Stack tensor.
    st = StackTensor.initial(n_candidates=4, max_depth=8)
    modes_initial = st.top_modes()
    assert modes_initial.shape == (4, 2)
    assert np.all(modes_initial == 1)

    # Toggle observe on candidate 1 only.
    mask = np.array([False, True, False, False])
    st2 = st.apply_toggle(mask, axis=1)
    modes_after = st2.top_modes()
    assert modes_after[1, 1] == 0     # observe toggled
    assert modes_after[1, 0] == 1     # rewrite unchanged
    for c in (0, 2, 3):
        assert np.all(modes_after[c] == 1)

    # Speculation batch.
    batch = SpeculationBatch.initial(n_candidates=4, max_steps=16,
                                       start_pos=0)
    batch.costs[0] = 10.5
    batch.costs[1] = 5.2
    batch.costs[2] = 8.1
    batch.costs[3] = 12.0
    winner = reduce_winner(batch)
    assert winner == 1, f"argmin should be 1, got {winner}"

    if verbose:
        print("=== TensorSpeculation self-check ===")
        print(f"  stack tensor shape:     {st.stack.shape}")
        print(f"  initial top modes:      all (rewrite=1, observe=1)")
        print(f"  toggle observe on c=1:  observe(c=1)={modes_after[1, 1]} OK")
        print(f"  speculation batch shape: emissions {batch.emissions.shape}")
        print(f"  argmin winner:          {winner} (cost {batch.costs[winner]})")
        print(f"\nResult: OK")
    return True


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
