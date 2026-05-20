"""Eliza.TensorGrammar — opcode set + digram index + grammar growth as tensors.

M3+M4+M5 of the homoiconic matricisation arc.

Tensor shapes:
  * opcode_bodies:    (N_opc, max_body) int64; -1 padding beyond body length
  * opcode_lengths:   (N_opc,) int64
  * digram_index:     (max_digrams, 3) int64; rows (prev_emit, this_emit, rule_id)
                       Rule_id = -1 marks "seen once"; >= 0 marks composite rule index.
                       Empty rows have all -2.

Operations:
  * grow_opcodes(opcode_bodies, lengths, new_body) → (extended bodies, lengths)
    appends `new_body` (variable length) by row-concat with padding
  * digram_lookup(digram_index, prev, this) → rule_id or -2 (not seen)
  * digram_insert(digram_index, prev, this, rule_id) → updated index
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np


PAD = -1
EMPTY = -2


@dataclass
class OpcodeTensor:
    """Growing opcode-set tensor.

    `bodies` has shape (N_opc, max_body); rows are zero-padded to
    max_body and lengths are tracked in `lengths`.
    """
    bodies: np.ndarray         # (N_opc, max_body) int64
    lengths: np.ndarray        # (N_opc,) int64
    max_body: int              # capacity per row (grows by concat-and-repad)

    @property
    def n_opcodes(self) -> int:
        return self.bodies.shape[0]

    @classmethod
    def empty(cls, max_body: int = 64) -> "OpcodeTensor":
        return cls(
            bodies=np.zeros((0, max_body), dtype=np.int64) + PAD,
            lengths=np.zeros((0,), dtype=np.int64),
            max_body=max_body,
        )

    @classmethod
    def from_python_opcodes(
        cls, opcodes: list, chain_index_lookup,
    ) -> "OpcodeTensor":
        """Build from a list of `opcode_set.Opcode` instances.

        `chain_index_lookup`: callable mapping ChainSymbol → int.
        """
        if not opcodes:
            return cls.empty()
        max_body = max(op.length for op in opcodes)
        bodies = np.full((len(opcodes), max_body), PAD, dtype=np.int64)
        lengths = np.zeros((len(opcodes),), dtype=np.int64)
        for i, op in enumerate(opcodes):
            for j, sym in enumerate(op.body):
                bodies[i, j] = chain_index_lookup(sym)
            lengths[i] = op.length
        return cls(bodies=bodies, lengths=lengths, max_body=max_body)


def grow_opcodes(opc: OpcodeTensor, new_body: np.ndarray) -> OpcodeTensor:
    """Append `new_body` as a new opcode. Pads/extends max_body as needed.

    Tensor operation: row-concat with zero-padding. On GPU this is
    `concat([bodies, padded_new_body[None, :]], axis=0)`.
    """
    L_new = len(new_body)
    if L_new > opc.max_body:
        # Widen the body tensor to fit.
        new_max = max(opc.max_body * 2, L_new)
        wide = np.full((opc.bodies.shape[0], new_max), PAD, dtype=np.int64)
        wide[:, :opc.max_body] = opc.bodies
        opc = OpcodeTensor(bodies=wide, lengths=opc.lengths.copy(),
                            max_body=new_max)
    # Pad new body to max_body and stack.
    padded = np.full((1, opc.max_body), PAD, dtype=np.int64)
    padded[0, :L_new] = new_body
    bodies_new = np.concatenate([opc.bodies, padded], axis=0)
    lengths_new = np.concatenate([opc.lengths, np.array([L_new], dtype=np.int64)])
    return OpcodeTensor(bodies=bodies_new, lengths=lengths_new,
                          max_body=opc.max_body)


@dataclass
class DigramIndex:
    """Open-addressed hash tensor mapping (prev, this) → rule_id.

    `table` has shape (capacity, 3): (prev, this, rule_id). Empty
    rows are (-2, -2, -2). Linear probing; collisions resolved by
    walking forward.

    On GPU, lookup is parallelisable: hash → vectorised probe.
    """
    table: np.ndarray      # (capacity, 3) int64
    capacity: int

    @classmethod
    def empty(cls, capacity: int = 1024) -> "DigramIndex":
        table = np.full((capacity, 3), EMPTY, dtype=np.int64)
        return cls(table=table, capacity=capacity)

    @staticmethod
    def _hash(prev: int, this: int, capacity: int) -> int:
        # Simple Cantor pair, then mod.
        c = (prev + this) * (prev + this + 1) // 2 + this
        return int(c) % capacity


def digram_lookup(idx: DigramIndex, prev: int, this: int) -> int:
    """Return the value (rule_id) for (prev, this), or EMPTY if not present."""
    if idx.capacity == 0:
        return EMPTY
    h = DigramIndex._hash(prev, this, idx.capacity)
    for probe in range(idx.capacity):
        slot = (h + probe) % idx.capacity
        row = idx.table[slot]
        if int(row[0]) == EMPTY:
            return EMPTY
        if int(row[0]) == prev and int(row[1]) == this:
            return int(row[2])
    return EMPTY


def digram_insert(idx: DigramIndex, prev: int, this: int, value: int) -> DigramIndex:
    """Insert or update (prev, this) → value. Returns potentially-grown table."""
    if idx.capacity == 0:
        idx = DigramIndex.empty()
    h = DigramIndex._hash(prev, this, idx.capacity)
    for probe in range(idx.capacity):
        slot = (h + probe) % idx.capacity
        row = idx.table[slot]
        if int(row[0]) == EMPTY or (int(row[0]) == prev and int(row[1]) == this):
            new_table = idx.table.copy()
            new_table[slot] = [prev, this, value]
            return DigramIndex(table=new_table, capacity=idx.capacity)
    # Fully occupied — grow.
    new_capacity = idx.capacity * 2
    new_table = np.full((new_capacity, 3), EMPTY, dtype=np.int64)
    new_idx = DigramIndex(table=new_table, capacity=new_capacity)
    # Re-insert all old entries.
    for k in range(idx.capacity):
        row = idx.table[k]
        if int(row[0]) != EMPTY:
            new_idx = digram_insert(new_idx, int(row[0]), int(row[1]), int(row[2]))
    return digram_insert(new_idx, prev, this, value)


# --- Self-check ---------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    from eliza.matrix_ops import _manifold_index
    from eliza.opcode_set import build_full_opcode_set
    from eliza.chain_symbol import ChainSymbol

    chambers, idx_map = _manifold_index()
    def chain_to_idx(sym: ChainSymbol) -> int:
        return idx_map[sym.to_s4()]

    opcodes = build_full_opcode_set()
    opc = OpcodeTensor.from_python_opcodes(opcodes, chain_to_idx)
    assert opc.n_opcodes == len(opcodes)
    assert opc.bodies.shape == (len(opcodes), opc.max_body)

    # Grow with a new opcode body.
    new_body = np.array([0, 1, 2, 3], dtype=np.int64)
    opc2 = grow_opcodes(opc, new_body)
    assert opc2.n_opcodes == len(opcodes) + 1
    assert np.array_equal(opc2.bodies[-1, :4], new_body)

    # Digram index.
    di = DigramIndex.empty(capacity=64)
    di = digram_insert(di, 5, 7, -1)
    di = digram_insert(di, 5, 8, 42)
    assert digram_lookup(di, 5, 7) == -1
    assert digram_lookup(di, 5, 8) == 42
    assert digram_lookup(di, 9, 9) == EMPTY

    # Trigger growth: fill close to capacity.
    for k in range(70):
        di = digram_insert(di, k + 100, k + 200, k)
    for k in range(70):
        assert digram_lookup(di, k + 100, k + 200) == k

    if verbose:
        print("=== TensorGrammar self-check ===")
        print(f"  opcode tensor shape:       {opc.bodies.shape}")
        print(f"  opcode lengths shape:      {opc.lengths.shape}")
        print(f"  grow opcodes: {len(opcodes)} → {opc2.n_opcodes}  OK")
        print(f"  digram index final capacity: {di.capacity}")
        print(f"  digram lookup correctness: OK (70 inserts retrieved correctly)")
        print(f"\nResult: OK")
    return True


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
