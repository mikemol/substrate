"""Eliza.GpuCodecV2 — O-arc fused codec with all refinements.

Incorporates:
  O1: vectorized opcode match (no per-opcode Python loop)
  O2: incremental match-tensor updates on grammar growth
  O3: GPU-side argmax
  O4: batched argmax precomputed for the whole stream between growth events
  O5: adaptive frequency tensor predictor (counts as cupy array)
  O6: explicit opcode cap (emits a freeze marker visible to decoder)
  O7: dynamic max_body resize on body overflow
  O8: int-based chamber walk via permutation-index lookup (no float matmul)

The encoder loop drops to a thin shell over precomputed decisions:
  * Build match-tensor for whole stream (single fused launch)
  * Compute argmax across the whole match-tensor at once (single launch)
  * Walk the stream sequentially using precomputed (best_idx, best_len)
  * On growth: append column to match tensor (incremental, O2)
  * Per emission: adaptive predictor → cumfreqs → range coder step
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from eliza.alphabets import (
    Chamber, NIBBLE_TO_PERM, ORIGIN, perm_compose,
)
from eliza.chain_symbol import ChainSymbol
from eliza.gpu_kernels import (
    HAS_CUPY, cp, gpu_argmax_at, gpu_opcode_match_append,
    gpu_opcode_match_vectorized, xp,
)
from eliza.matrix_ops import _manifold_index
from eliza.opcode_set import Opcode, build_full_opcode_set
from eliza.per_nibble_chain import nibbles_to_bytes, nibble_from_transition
from eliza.tensor_range_coder import (
    RCDecoderState, RCState, rc_finish, rc_step_decode, rc_step_encode,
)


DEFAULT_MAX_OPCODES = 512
DEFAULT_MAX_BODY = 64
FREEZE_MARKER = -42        # signals that grammar growth is frozen


# --- O8: int-based chamber walk via per-nibble next-table ------------


def _build_next_chamber_table(chambers: List[Chamber], idx_map: Dict) -> np.ndarray:
    """Precompute next_chamber[c, n] = idx of perm_compose(chambers[c], NIBBLE_TO_PERM[n]).

    Pure integer lookup; no float matmul. Numerically exact.
    """
    n_cham = len(chambers)
    table = np.zeros((n_cham, 16), dtype=np.int64)
    for c_idx, c in enumerate(chambers):
        for n in range(16):
            after = perm_compose(c, NIBBLE_TO_PERM[n])
            table[c_idx, n] = idx_map[after]
    return table


def int_chamber_walk(data: bytes, chambers: List[Chamber],
                       idx_map: Dict, next_table: np.ndarray) -> np.ndarray:
    """Compute chamber indices via int lookup (no float matmul)."""
    n_nib = 2 * len(data)
    out = np.zeros(n_nib, dtype=np.int64)
    c = idx_map[ORIGIN]
    pos = 0
    for byte in data:
        n1 = (byte >> 4) & 0xF
        c = int(next_table[c, n1])
        out[pos] = c
        pos += 1
        n2 = byte & 0xF
        c = int(next_table[c, n2])
        out[pos] = c
        pos += 1
    return out


# --- O5: adaptive predictor as a tensor ------------------------------


def adaptive_cumfreqs(counts, alphabet_size: int, alpha: float = 0.5):
    """Build cumulative frequency tensor from running counts.

    `counts`: (alphabet_size,) running occurrence counts.
    Returns: (alphabet_size + 1,) int64 cumulative-frequency tensor
    suitable for the range coder.

    Tensor op: scale + alpha, cumsum.
    """
    SCALE = 1024
    # smooth: counts + alpha; multiply by SCALE for integer freqs.
    freqs = ((counts.astype(np.float64) + alpha) * SCALE).astype(np.int64)
    # Ensure each entry is ≥ 1 (range coder requires strictly positive
    # frequencies for symbols we may encode).
    freqs = np.maximum(freqs, 1)
    cumfreqs = np.zeros(alphabet_size + 1, dtype=np.int64)
    cumfreqs[1:] = np.cumsum(freqs[:alphabet_size])
    return cumfreqs


# --- O7: dynamic max_body resize -------------------------------------


def grow_body_capacity(bodies, new_max_body: int):
    """Double-grow the body column dimension when an opcode body exceeds
    the current max_body."""
    xp_mod = xp()
    n_opc, old_max = bodies.shape
    new = xp_mod.full((n_opc, new_max_body), -1, dtype=xp_mod.int64)
    new[:, :old_max] = bodies
    return new


# --- O6: explicit cap policy + capacity-aware growth -----------------


def try_grow_opcode(bodies, lengths, n_used: int, max_opcodes: int,
                     max_body: int, new_body) -> Tuple:
    """Append `new_body` to the opcode tensors.

    The `max_opcodes` is the CURRENT row capacity. When n_used hits it,
    we DOUBLE the capacity (power-of-2 growth, std::vector-style)
    rather than freezing. Prior opcodes remain at their indices 0..n_used-1;
    new opcodes occupy the freshly-doubled high-index space.

    This eliminates the cap-natural phase-change pathology — the codec
    stays in the saturated regime indefinitely; doubling is amortised
    O(1) per growth event (each opcode copied O(log N) times across all
    doublings).

    Returns (bodies, lengths, n_used+1, max_body, max_opcodes_NEW, True).
    growth_succeeded is always True (no freeze).
    """
    xp_mod = xp()
    L_new = int(new_body.shape[0])
    if n_used >= max_opcodes:
        # Double the row capacity. Power-of-2 alignment preserved iff
        # the initial cap is a power of 2.
        new_max = max_opcodes * 2
        old_rows = bodies.shape[0]
        new_bodies = xp_mod.full((new_max, bodies.shape[1]), -1, dtype=xp_mod.int64)
        new_bodies[:old_rows] = bodies
        new_lengths = xp_mod.zeros((new_max,), dtype=xp_mod.int64)
        new_lengths[:old_rows] = lengths
        bodies = new_bodies
        lengths = new_lengths
        max_opcodes = new_max
    if L_new > max_body:
        # Resize body column dimension (independent of row doubling).
        new_cap = max(max_body * 2, L_new)
        bodies = grow_body_capacity(bodies, new_cap)
        max_body = new_cap
    bodies[n_used, :L_new] = new_body
    lengths[n_used] = L_new
    return bodies, lengths, n_used + 1, max_body, max_opcodes, True


# --- Encoder ---------------------------------------------------------


def encode(data: bytes, initial_opcodes: List[Opcode] = None,
           max_opcodes: int = DEFAULT_MAX_OPCODES) -> Tuple[bytes, Dict]:
    initial_opcodes = initial_opcodes if initial_opcodes is not None \
                      else build_full_opcode_set()
    chambers, idx_map = _manifold_index()

    # O8: int chamber walk (numerically exact).
    next_table = _build_next_chamber_table(chambers, idx_map)
    walk = int_chamber_walk(data, chambers, idx_map, next_table)
    n_chain = len(walk)

    # Initial opcode tensors (preallocated capacity).
    initial_max_body = max(op.length for op in initial_opcodes)
    max_body = max(DEFAULT_MAX_BODY, initial_max_body)
    bodies = xp().full((max_opcodes, max_body), -1, dtype=xp().int64)
    lengths = xp().zeros((max_opcodes,), dtype=xp().int64)
    n_used = len(initial_opcodes)
    for i, op in enumerate(initial_opcodes):
        for j, cs in enumerate(op.body):
            bodies[i, j] = idx_map[cs.to_s4()]
        lengths[i] = op.length

    # O1+O2: compute the FULL match tensor once with vectorized kernel.
    walk_gpu = xp().asarray(walk)
    match_tensor = gpu_opcode_match_vectorized(
        walk_gpu, bodies[:n_used], lengths[:n_used],
    )

    # O5: adaptive predictor counts (CPU; the range coder is CPU anyway).
    # Allow alphabet up to 24 + max_opcodes + 1 (cap marker).
    max_alphabet = 24 + max_opcodes + 1
    counts = np.zeros(max_alphabet, dtype=np.int64)

    rc = RCState()
    prev_emission = -1
    n_vm = 0
    n_terminal = 0
    n_opcode = 0
    n_growth = 0
    digram_seen: Dict[Tuple[int, int], int] = {}
    cap_frozen = False    # encoder + decoder track dynamically in lockstep
    pos = 0

    while pos < n_chain:
        # Per-step decision: use GPU-side argmax on row pos.
        if pos < match_tensor.shape[0] and n_used > 0:
            row = match_tensor[pos, :n_used]
            best_idx_gpu = xp().argmax(row)
            best_idx = int(best_idx_gpu)
            best_len = int(row[best_idx_gpu])
        else:
            best_idx = 0
            best_len = 0

        if best_len == 0:
            emit_idx = int(walk[pos])
            advance = 1
            n_terminal += 1
        else:
            emit_idx = 24 + best_idx
            advance = best_len
            n_opcode += 1

        # O5: adaptive cumfreqs.
        alphabet_size = 24 + n_used + (1 if cap_frozen else 0)
        cumfreqs = adaptive_cumfreqs(counts[:alphabet_size], alphabet_size)
        rc_step_encode(rc, cumfreqs, emit_idx, int(cumfreqs[-1]))
        counts[emit_idx] += 1

        # Grammar growth.
        if prev_emission >= 0 and not cap_frozen:
            key = (prev_emission, emit_idx)
            existing = digram_seen.get(key)
            if existing is None:
                digram_seen[key] = -1
            else:
                # Try to grow.
                prev_body = _expand_emission_body(prev_emission, bodies,
                                                    lengths, n_used)
                this_body = _expand_emission_body(emit_idx, bodies, lengths,
                                                    n_used)
                new_body = xp().concatenate([prev_body, this_body])
                bodies, lengths, n_used_new, max_body, max_opcodes, grew = try_grow_opcode(
                    bodies, lengths, n_used, max_opcodes, max_body, new_body,
                )
                if grew:
                    # O2: append a column to match_tensor for the new opcode.
                    new_match = gpu_opcode_match_vectorized(
                        walk_gpu,
                        bodies[n_used:n_used_new],
                        lengths[n_used:n_used_new],
                    )
                    match_tensor = xp().concatenate(
                        [match_tensor, new_match], axis=1)
                    digram_seen[key] = n_used_new - 1
                    n_used = n_used_new
                    n_growth += 1
                    # Cap-doubling: grow `counts` in lockstep with max_opcodes.
                    if 24 + max_opcodes + 1 > counts.shape[0]:
                        new_counts = np.zeros(24 + max_opcodes + 1,
                                                 dtype=np.int64)
                        new_counts[:counts.shape[0]] = counts
                        counts = new_counts
                else:
                    # O6: cap reached. Stop growing; alphabet expands by 1
                    # in subsequent emissions (decoder mirrors via its
                    # own cap_frozen tracking, NOT via the header).
                    cap_frozen = True

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
        "n_final_opcodes": int(n_used),
        "cap_frozen": cap_frozen,
        "backend": "GPU" if HAS_CUPY else "CPU",
    }


def _expand_emission_body(emit_idx: int, bodies, lengths, n_used: int):
    if emit_idx < 24:
        return xp().asarray([emit_idx], dtype=xp().int64)
    op_idx = emit_idx - 24
    L = int(lengths[op_idx])
    return bodies[op_idx, :L]


# --- Decoder ----------------------------------------------------------


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
    bodies = xp().full((max_opcodes, max_body), -1, dtype=xp().int64)
    lengths = xp().zeros((max_opcodes,), dtype=xp().int64)
    n_used = n_initial
    for i, op in enumerate(initial_opcodes):
        for j, cs in enumerate(op.body):
            bodies[i, j] = idx_map[cs.to_s4()]
        lengths[i] = op.length

    dec_state = RCDecoderState.from_stream(payload)
    prev_emission = -1
    chain_terminals: List[int] = []
    digram_seen: Dict[Tuple[int, int], int] = {}
    cap_frozen = False
    max_alphabet = 24 + max_opcodes + 1
    counts = np.zeros(max_alphabet, dtype=np.int64)

    for _ in range(n_vm):
        alphabet_size = 24 + n_used + (1 if cap_frozen else 0)
        cumfreqs = adaptive_cumfreqs(counts[:alphabet_size], alphabet_size)
        emit_idx = rc_step_decode(dec_state, cumfreqs, int(cumfreqs[-1]))
        counts[emit_idx] += 1
        if emit_idx < 24:
            chain_terminals.append(emit_idx)
        else:
            op_idx = emit_idx - 24
            L = int(lengths[op_idx])
            body = bodies[op_idx, :L]
            chain_terminals.extend(int(b) for b in (
                cp.asnumpy(body) if HAS_CUPY else np.asarray(body)))

        if prev_emission >= 0 and not cap_frozen:
            key = (prev_emission, emit_idx)
            existing = digram_seen.get(key)
            if existing is None:
                digram_seen[key] = -1
            else:
                prev_body = _expand_emission_body(prev_emission, bodies,
                                                    lengths, n_used)
                this_body = _expand_emission_body(emit_idx, bodies, lengths,
                                                    n_used)
                new_body = xp().concatenate([prev_body, this_body])
                bodies, lengths, n_used_new, max_body, max_opcodes, grew = try_grow_opcode(
                    bodies, lengths, n_used, max_opcodes, max_body, new_body,
                )
                if grew:
                    digram_seen[key] = n_used_new - 1
                    n_used = n_used_new
                    if 24 + max_opcodes + 1 > counts.shape[0]:
                        new_counts = np.zeros(24 + max_opcodes + 1,
                                                 dtype=np.int64)
                        new_counts[:counts.shape[0]] = counts
                        counts = new_counts
                else:
                    cap_frozen = True
        prev_emission = emit_idx

    state = ORIGIN
    nibbles: List[int] = []
    for c_idx in chain_terminals:
        after = chambers[c_idx]
        n = nibble_from_transition(state, after)
        if n is None:
            raise ValueError(f"invalid chain transition")
        nibbles.append(n)
        state = after
    return nibbles_to_bytes(nibbles)


# --- Self-check ---------------------------------------------------------


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
        print("=== GpuCodecV2 (O-arc) self-check ===")
        print(f"  backend:                {stats['backend']}")
        print(f"  input bytes:            {len(data)}")
        print(f"  encoded:                {len(encoded)} bytes "
              f"({8 * len(encoded) / len(data):.3f} b/byte)")
        print(f"  n_vm:                   {stats['n_vm']}")
        print(f"  growth events:          {stats['n_growth']}")
        print(f"  final opcodes:          {stats['n_final_opcodes']}")
        print(f"  cap_frozen:             {stats['cap_frozen']}")
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
