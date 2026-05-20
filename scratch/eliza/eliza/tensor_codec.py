"""Eliza.TensorCodec — homoiconic codec as a fused tensor pipeline.

M9 of the matricisation arc. Composes:
  * matrix_ops.walk_to_chamber_indices (chamber walk, M-arc L1-L2)
  * matrix_ops.longest_opcode_at_each_position (opcode match, L3)
  * tensor_grammar.OpcodeTensor + DigramIndex (grammar, M3-M5)
  * tensor_speculation.StackTensor (stack machine, M6)
  * tensor_range_coder.RCState (range coder, M1-M2)

Single tensor pipeline:
  bytes → chamber-walk → opcode-match-tensor → vm-stream-tensor
        → RC-state-evolution → encoded-bits

All stages take tensor input, produce tensor output. The composer
chains them; on GPU this becomes a single fused kernel chain.

This module proves the pipeline composes correctly on CPU. The GPU
port (N-arc) replaces the numpy backend with cupy without algorithmic
changes.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from eliza.alphabets import NIBBLE_TO_PERM, ORIGIN, perm_compose
from eliza.chain_symbol import ChainSymbol
from eliza.matrix_ops import (
    _manifold_index, longest_opcode_at_each_position,
    walk_to_chamber_indices,
)
from eliza.opcode_set import Opcode, build_full_opcode_set
from eliza.per_nibble_chain import nibbles_to_bytes, nibble_from_transition
from eliza.tensor_grammar import (
    DigramIndex, EMPTY, OpcodeTensor, digram_insert, digram_lookup,
    grow_opcodes,
)
from eliza.tensor_range_coder import (
    RCDecoderState, RCState, rc_finish, rc_step_decode, rc_step_encode,
)


# --- Encoder as fused tensor pipeline ----------------------------------


def encode(data: bytes, initial_opcodes: List[Opcode] = None
            ) -> Tuple[bytes, Dict]:
    """Tensor-fused encoder. Reads bytes, runs the matricised pipeline,
    returns encoded bytes + diagnostics.

    Pipeline:
      1. bytes → per-nibble chamber index stream  (tensor: (2N,) int64)
      2. opcode_match_tensor at each position  (tensor: (2N, N_opc))
      3. greedy commit: at each position, use longest match  (sequential)
      4. emit via range coder (tensor RCState evolution)
    """
    initial_opcodes = initial_opcodes if initial_opcodes is not None \
                      else build_full_opcode_set()
    chambers, idx_map = _manifold_index()

    # Stage 1: chamber walk as tensor.
    walk = walk_to_chamber_indices(data)
    n_chain = len(walk)

    # Stage 2: opcode tensor (initial).
    def chain_to_idx(sym: ChainSymbol) -> int:
        return idx_map[sym.to_s4()]
    opc = OpcodeTensor.from_python_opcodes(initial_opcodes, chain_to_idx)
    n_initial = opc.n_opcodes

    # Stage 3+4 fused: walk through the stream, at each position
    # commit longest matching opcode, grow opcode set via tensor concat,
    # emit via tensor RC.
    rc = RCState()
    digrams = DigramIndex.empty(capacity=2048)
    prev_emission = -1
    n_vm = 0
    n_terminal = 0
    n_opcode = 0
    n_growth = 0
    pos = 0
    while pos < n_chain:
        # Find longest matching opcode at this position.
        best_idx = -1
        best_len = 0
        for i in range(opc.n_opcodes):
            L = int(opc.lengths[i])
            if L > best_len and pos + L <= n_chain:
                body = opc.bodies[i, :L]
                if np.array_equal(walk[pos:pos + L], body):
                    best_idx = i
                    best_len = L
        if best_idx == -1:
            # Terminal emission.
            emit_idx = int(walk[pos])
            advance = 1
            n_terminal += 1
        else:
            emit_idx = 24 + best_idx
            advance = best_len
            n_opcode += 1
        # Tensor RC step.
        alphabet_size = 24 + opc.n_opcodes
        cumfreqs = _adaptive_cumfreqs(rc, emit_idx, alphabet_size, n_vm)
        rc_step_encode(rc, cumfreqs, emit_idx, int(cumfreqs[-1]))
        # Adaptive grammar growth via digram tensor.
        if prev_emission >= 0:
            existing = digram_lookup(digrams, prev_emission, emit_idx)
            if existing == EMPTY:
                digrams = digram_insert(digrams, prev_emission, emit_idx, -1)
            else:
                # Grow opcode tensor: composite body = prev's body ++ this's body.
                prev_body = _expand_emission_to_body(prev_emission, opc, walk[pos - advance])
                this_body = _expand_emission_to_body(emit_idx, opc, walk[pos])
                new_body = np.concatenate([prev_body, this_body])
                opc = grow_opcodes(opc, new_body)
                digrams = digram_insert(digrams, prev_emission, emit_idx,
                                          opc.n_opcodes - 1)
                n_growth += 1
        prev_emission = emit_idx
        pos += advance
        n_vm += 1

    encoded = rc_finish(rc)

    # Header: input chain length, n_initial_opcodes, n_vm.
    header = bytearray()
    header.extend(n_chain.to_bytes(4, "little"))
    header.extend(n_initial.to_bytes(4, "little"))
    header.extend(n_vm.to_bytes(4, "little"))
    output = bytes(header) + encoded
    return output, {
        "encoded_bytes": len(output),
        "n_chain": n_chain,
        "n_vm": n_vm,
        "n_terminal": n_terminal,
        "n_opcode": n_opcode,
        "n_growth": n_growth,
        "n_final_opcodes": opc.n_opcodes,
    }


def _adaptive_cumfreqs(rc: RCState, emit_idx: int, alphabet_size: int,
                        n_observed: int) -> np.ndarray:
    """Build cumulative frequencies adaptively. Stored implicitly in
    rc.buffer for now; here we use a uniform-with-laplace prior for
    simplicity (the real codec maintains counts per emit_idx)."""
    # For correctness in this M9 demo, use uniform cumfreqs scaled.
    SCALE = 1024
    cumfreqs = np.arange(alphabet_size + 1, dtype=np.int64) * SCALE
    return cumfreqs


def _expand_emission_to_body(emit_idx: int, opc: OpcodeTensor,
                              fallback_chain: int) -> np.ndarray:
    """Get the chain-index body that an emission represents."""
    if emit_idx < 24:
        return np.array([emit_idx], dtype=np.int64)
    op_idx = emit_idx - 24
    L = int(opc.lengths[op_idx])
    return opc.bodies[op_idx, :L].copy()


# --- Decoder mirror ----------------------------------------------------


def decode(encoded: bytes, initial_opcodes: List[Opcode] = None) -> bytes:
    """Reverse of encode. Tensor pipeline: RC decode → emit-index stream
    → unfold via opcode tensor → chamber sequence → byte sequence."""
    initial_opcodes = initial_opcodes if initial_opcodes is not None \
                      else build_full_opcode_set()
    chambers, idx_map = _manifold_index()

    n_chain = int.from_bytes(encoded[:4], "little")
    n_initial = int.from_bytes(encoded[4:8], "little")
    n_vm = int.from_bytes(encoded[8:12], "little")
    payload = encoded[12:]

    def chain_to_idx(sym: ChainSymbol) -> int:
        return idx_map[sym.to_s4()]
    opc = OpcodeTensor.from_python_opcodes(initial_opcodes, chain_to_idx)

    dec_state = RCDecoderState.from_stream(payload)
    digrams = DigramIndex.empty(capacity=2048)
    prev_emission = -1
    chain_terminals: List[int] = []

    for _ in range(n_vm):
        alphabet_size = 24 + opc.n_opcodes
        cumfreqs = _adaptive_cumfreqs(None, 0, alphabet_size, 0)
        emit_idx = rc_step_decode(dec_state, cumfreqs, int(cumfreqs[-1]))
        if emit_idx < 24:
            chain_terminals.append(emit_idx)
            advance_body = np.array([emit_idx], dtype=np.int64)
        else:
            op_idx = emit_idx - 24
            L = int(opc.lengths[op_idx])
            body = opc.bodies[op_idx, :L]
            chain_terminals.extend(int(b) for b in body)
            advance_body = body
        # Mirror grammar growth.
        if prev_emission >= 0:
            existing = digram_lookup(digrams, prev_emission, emit_idx)
            if existing == EMPTY:
                digrams = digram_insert(digrams, prev_emission, emit_idx, -1)
            else:
                prev_body = _expand_emission_to_body(prev_emission, opc, 0)
                this_body = _expand_emission_to_body(emit_idx, opc, 0)
                new_body = np.concatenate([prev_body, this_body])
                opc = grow_opcodes(opc, new_body)
                digrams = digram_insert(digrams, prev_emission, emit_idx,
                                          opc.n_opcodes - 1)
        prev_emission = emit_idx

    # Invert per-nibble chain indices to bytes.
    state = ORIGIN
    nibbles: List[int] = []
    for c_idx in chain_terminals:
        after = chambers[c_idx]
        n = nibble_from_transition(state, after)
        if n is None:
            raise ValueError(f"invalid transition ({state}, {after})")
        nibbles.append(n)
        state = after
    return nibbles_to_bytes(nibbles)


# --- Self-check ---------------------------------------------------------


def self_check(size: int = 256, verbose: bool = True) -> bool:
    from pathlib import Path
    HERE = Path(__file__).resolve().parent
    src = HERE / "engine.py"
    with open(src, "rb") as f:
        data = f.read()[:size]

    encoded, stats = encode(data)
    decoded = decode(encoded)
    ok = decoded == data

    if verbose:
        print("=== TensorCodec (matricised pipeline) self-check ===")
        print(f"  input bytes:       {len(data)}")
        print(f"  encoded:           {len(encoded)} bytes "
              f"({8 * len(encoded) / len(data):.3f} b/byte)")
        print(f"  n_vm steps:        {stats['n_vm']}")
        print(f"  growth events:     {stats['n_growth']}")
        print(f"  final opcodes:     {stats['n_final_opcodes']}")
        print(f"  round-trip:        {'OK' if ok else 'FAIL'}")
        if not ok:
            diffs = sum(1 for i in range(min(len(data), len(decoded)))
                        if data[i] != decoded[i])
            print(f"    bytes differ:    {diffs}")
            print(f"    decoded length:  {len(decoded)}")
        print(f"\nResult: {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
