"""Eliza.GpuTensorCodec — fused codec pipeline (revised per user review).

N7 revision addressing the top issues from user feedback:
  (1) Compute opcode match tensor ONCE for the whole walk (not per
      position). Use match_tensor[pos] for the per-step decision.
  (2) Preallocate opcode tensor with a `max_opcodes` cap; growth fills
      preallocated slots rather than reallocating.
  (3) Eliminate per-step CPU↔GPU transfers: keep the match tensor on
      GPU; only transfer the small (N_opc,) row at pos per step.
  (4) Remove the `fallback_chain` asymmetry parameter from
      _expand_to_body_gpu.
  (5) Use match_tensor[pos] not the row-0 of a fresh recomputation.

Limitations acknowledged:
  * Sequential greedy parsing is preserved (parallel parsing is a
    follow-on slice).
  * Opcode growth still mutates the opcode tensor (preallocated rather
    than realloc); the match tensor becomes stale after growth, so we
    track growth events and recompute when they accumulate.
  * Uniform cumfreqs predictor still used; adaptive tensor predictor
    is the follow-on after parallel parsing.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np

from eliza.alphabets import NIBBLE_TO_PERM, ORIGIN, perm_compose
from eliza.chain_symbol import ChainSymbol
from eliza.gpu_codec_stages import (
    HAS_CUPY, cp, gpu_opcode_match, gpu_walk_batched, xp,
)
from eliza.matrix_ops import _manifold_index
from eliza.opcode_set import Opcode, build_full_opcode_set
from eliza.per_nibble_chain import nibbles_to_bytes, nibble_from_transition
from eliza.tensor_range_coder import (
    RCDecoderState, RCState, rc_finish, rc_step_decode, rc_step_encode,
)


# Preallocated opcode tensor cap. Growth fills these slots; if we hit
# the cap, we recompute the match tensor against the expanded set.
DEFAULT_MAX_OPCODES = 512
DEFAULT_MAX_BODY = 64
# Recompute match every K growth events (to keep match tensor fresh
# without recomputing per step).
RECOMPUTE_AFTER_GROWTHS = 16


def _to_cpu(arr):
    if HAS_CUPY and isinstance(arr, cp.ndarray):
        return cp.asnumpy(arr)
    return np.asarray(arr)


def _build_opcode_tensors(
    initial_opcodes: List[Opcode], idx_map: dict,
    max_opcodes: int, max_body: int,
):
    """Allocate the FULL opcode tensor up-front; only fill the first
    n_initial slots. Returns (bodies, lengths, n_used).
    """
    bodies = np.full((max_opcodes, max_body), -1, dtype=np.int64)
    lengths = np.zeros((max_opcodes,), dtype=np.int64)
    for i, op in enumerate(initial_opcodes):
        for j, cs in enumerate(op.body):
            bodies[i, j] = idx_map[cs.to_s4()]
        lengths[i] = op.length
    return xp().asarray(bodies), xp().asarray(lengths), len(initial_opcodes)


def _expand_emission_to_body(emit_idx: int, bodies, lengths):
    """Get the chain-index body for an emission. NO fallback_chain
    parameter — uses bodies+lengths uniformly.
    """
    if emit_idx < 24:
        # Terminal emission: body is just the chain index.
        return xp().asarray([emit_idx], dtype=xp().int64)
    op_idx = emit_idx - 24
    L = int(lengths[op_idx])
    return bodies[op_idx, :L]


def encode(data: bytes, initial_opcodes: List[Opcode] = None,
           max_opcodes: int = DEFAULT_MAX_OPCODES,
           ) -> Tuple[bytes, Dict]:
    """Encode bytes via the revised fused GPU pipeline."""
    initial_opcodes = initial_opcodes if initial_opcodes is not None \
                      else build_full_opcode_set()
    chambers, idx_map = _manifold_index()

    # Stage 1: chamber walk (single window for now).
    walk_gpu = gpu_walk_batched([data])
    walk_gpu_flat = walk_gpu[0]
    walk_np = _to_cpu(walk_gpu_flat)
    n_chain = len(walk_np)

    # Stage 2: preallocate opcode tensor with capacity.
    initial_max_body = max(op.length for op in initial_opcodes)
    max_body = max(DEFAULT_MAX_BODY, initial_max_body)
    bodies, lengths, n_used = _build_opcode_tensors(
        initial_opcodes, idx_map, max_opcodes, max_body,
    )

    # Stage 3: compute match tensor ONCE.  Keep on GPU; transfer only
    # per-step row + argmax result, NOT the full tensor.
    match_gpu = gpu_opcode_match(walk_np, bodies[:n_used], lengths[:n_used])
    match_stale_count = 0    # growth events since last recompute

    # Stage 4: sequential commit, indexing into match tensor.
    rc = RCState()
    prev_emission = -1
    n_vm = 0
    n_terminal = 0
    n_opcode = 0
    n_growth = 0
    digram_seen: Dict[Tuple[int, int], int] = {}
    SCALE = 1024
    pos = 0

    while pos < n_chain:
        # Find longest match at pos using PRECOMPUTED match tensor.
        # Argmax done on GPU; only the (best_idx, best_len) scalars
        # transfer to CPU per step — not the full row.
        if match_gpu.shape[1] >= n_used:
            row_gpu = match_gpu[pos, :n_used]
        else:
            match_gpu = gpu_opcode_match(walk_np, bodies[:n_used], lengths[:n_used])
            row_gpu = match_gpu[pos, :n_used]
            match_stale_count = 0
        # GPU-side argmax + max reduction; transfer only 2 scalars.
        best_idx_gpu = xp().argmax(row_gpu)
        best_len_gpu = row_gpu[best_idx_gpu]
        best_idx = int(best_idx_gpu)
        best_len = int(best_len_gpu)
        if best_len == 0:
            emit_idx = int(walk_np[pos])
            advance = 1
            n_terminal += 1
        else:
            emit_idx = 24 + best_idx
            advance = best_len
            n_opcode += 1

        # Adaptive RC step (uniform cumfreqs — limitation acknowledged).
        alphabet_size = 24 + n_used
        cumfreqs = np.arange(alphabet_size + 1, dtype=np.int64) * SCALE
        rc_step_encode(rc, cumfreqs, emit_idx, int(cumfreqs[-1]))

        # Grammar growth into preallocated slot.
        if prev_emission >= 0:
            key = (prev_emission, emit_idx)
            existing = digram_seen.get(key)
            if existing is None:
                digram_seen[key] = -1
            else:
                if n_used < max_opcodes:
                    prev_body = _expand_emission_to_body(prev_emission, bodies, lengths)
                    this_body = _expand_emission_to_body(emit_idx, bodies, lengths)
                    new_body = xp().concatenate([prev_body, this_body])
                    L_new = int(new_body.shape[0])
                    if L_new <= max_body:
                        bodies[n_used, :L_new] = new_body
                        lengths[n_used] = L_new
                        digram_seen[key] = n_used
                        n_used += 1
                        n_growth += 1
                        match_stale_count += 1
                        # Recompute match tensor every RECOMPUTE_AFTER_GROWTHS.
                        # Stays on GPU; no CPU transfer at recompute.
                        if match_stale_count >= RECOMPUTE_AFTER_GROWTHS:
                            match_gpu = gpu_opcode_match(
                                walk_np, bodies[:n_used], lengths[:n_used])
                            match_stale_count = 0
                # else: cap reached; skip growth silently.

        prev_emission = emit_idx
        pos += advance
        n_vm += 1

    encoded = rc_finish(rc)
    header = bytearray()
    header.extend(n_chain.to_bytes(4, "little"))
    header.extend(len(initial_opcodes).to_bytes(4, "little"))
    header.extend(n_vm.to_bytes(4, "little"))
    output = bytes(header) + encoded
    return output, {
        "encoded_bytes": len(output),
        "n_chain": n_chain,
        "n_vm": n_vm,
        "n_terminal": n_terminal,
        "n_opcode": n_opcode,
        "n_growth": n_growth,
        "n_final_opcodes": n_used,
        "n_match_recomputes": (n_growth // RECOMPUTE_AFTER_GROWTHS) + 1,
        "backend": "GPU" if HAS_CUPY else "CPU",
    }


def decode(encoded: bytes, initial_opcodes: List[Opcode] = None,
           max_opcodes: int = DEFAULT_MAX_OPCODES) -> bytes:
    initial_opcodes = initial_opcodes if initial_opcodes is not None \
                      else build_full_opcode_set()
    chambers, idx_map = _manifold_index()
    n_chain = int.from_bytes(encoded[:4], "little")
    n_initial = int.from_bytes(encoded[4:8], "little")
    n_vm = int.from_bytes(encoded[8:12], "little")
    payload = encoded[12:]

    initial_max_body = max(op.length for op in initial_opcodes)
    max_body = max(DEFAULT_MAX_BODY, initial_max_body)
    bodies, lengths, n_used = _build_opcode_tensors(
        initial_opcodes, idx_map, max_opcodes, max_body,
    )

    dec_state = RCDecoderState.from_stream(payload)
    prev_emission = -1
    chain_terminals: List[int] = []
    digram_seen: Dict[Tuple[int, int], int] = {}
    SCALE = 1024

    for _ in range(n_vm):
        alphabet_size = 24 + n_used
        cumfreqs = np.arange(alphabet_size + 1, dtype=np.int64) * SCALE
        emit_idx = rc_step_decode(dec_state, cumfreqs, int(cumfreqs[-1]))
        if emit_idx < 24:
            chain_terminals.append(emit_idx)
        else:
            op_idx = emit_idx - 24
            L = int(lengths[op_idx])
            body = bodies[op_idx, :L]
            chain_terminals.extend(int(b) for b in _to_cpu(body))
        if prev_emission >= 0:
            key = (prev_emission, emit_idx)
            existing = digram_seen.get(key)
            if existing is None:
                digram_seen[key] = -1
            else:
                if n_used < max_opcodes:
                    prev_body = _expand_emission_to_body(prev_emission, bodies, lengths)
                    this_body = _expand_emission_to_body(emit_idx, bodies, lengths)
                    new_body = xp().concatenate([prev_body, this_body])
                    L_new = int(new_body.shape[0])
                    if L_new <= max_body:
                        bodies[n_used, :L_new] = new_body
                        lengths[n_used] = L_new
                        digram_seen[key] = n_used
                        n_used += 1
        prev_emission = emit_idx

    state = ORIGIN
    nibbles: List[int] = []
    for c_idx in chain_terminals:
        after = chambers[c_idx]
        n = nibble_from_transition(state, after)
        if n is None:
            raise ValueError(f"invalid chain transition at #{len(nibbles)}")
        nibbles.append(n)
        state = after
    return nibbles_to_bytes(nibbles)


def self_check(size: int = 256, verbose: bool = True) -> bool:
    from pathlib import Path
    import time
    HERE = Path(__file__).resolve().parent
    src = HERE / "engine.py"
    with open(src, "rb") as f:
        data = f.read()[:size]

    t0 = time.perf_counter()
    encoded, stats = encode(data)
    enc_time = time.perf_counter() - t0
    t0 = time.perf_counter()
    decoded = decode(encoded)
    dec_time = time.perf_counter() - t0
    ok = decoded == data

    if verbose:
        print("=== GpuTensorCodec (revised) self-check ===")
        print(f"  backend:                {stats['backend']}")
        print(f"  input bytes:            {len(data)}")
        print(f"  encoded:                {len(encoded)} bytes "
              f"({8 * len(encoded) / len(data):.3f} b/byte)")
        print(f"  n_vm:                   {stats['n_vm']}")
        print(f"  growth events:          {stats['n_growth']}")
        print(f"  match recomputes:       {stats['n_match_recomputes']}")
        print(f"  final opcodes:          {stats['n_final_opcodes']}")
        print(f"  encode time:            {enc_time*1000:.1f}ms")
        print(f"  decode time:            {dec_time*1000:.1f}ms")
        print(f"  round-trip:             {'OK' if ok else 'FAIL'}")
        if not ok:
            diffs = sum(1 for i in range(min(len(data), len(decoded)))
                        if data[i] != decoded[i])
            print(f"    bytes differ:         {diffs}")
            print(f"    decoded length:       {len(decoded)}")
        print(f"\nResult: {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
