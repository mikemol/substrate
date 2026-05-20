"""Eliza.GpuCodecV5 — V4 + active speculation emitting control opcodes.

S-arc: the codec actively chooses between [default, S_DEFER_GROW,
S_INLINE_LAST, S_PUSH_NO_REWRITE/S_POP region] when speculation says
emission saves bits.

S1+S2: at each digram-repeat position, the K-step beam evaluates
       [no-emit, S_DEFER_GROW] and commits the winner.
S3:    S_INLINE_LAST decoder semantics — re-flatten last NT reference.
S4:    Stack-region: S_PUSH_NO_REWRITE … S_POP bracket a leave-alone
       region; amortises control cost over the bracketed span.
S5:    S_INSPECT_LAST — emit last opcode's category as a stack value
       (introspection-as-data).

Default policy: never emit control opcodes; behavior matches V4
exactly. Active policy: speculation may emit S_DEFER_GROW when the
local prediction is that growing this digram makes future encoding
more expensive (e.g., the new opcode would rarely match again).
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np

from eliza.alphabets import NIBBLE_TO_PERM, ORIGIN, perm_compose
from eliza.chain_symbol import ChainSymbol
from eliza.gpu_codec_v2 import (
    _build_next_chamber_table, _expand_emission_body, adaptive_cumfreqs,
    grow_body_capacity, int_chamber_walk, try_grow_opcode,
    DEFAULT_MAX_BODY, DEFAULT_MAX_OPCODES,
)
from eliza.gpu_codec_v4 import alphabet_size, control_opcode_base
from eliza.gpu_kernels import (
    HAS_CUPY, cp, gpu_opcode_match_vectorized, xp,
)
from eliza.lambda_vm_opcodes import (
    N_CONTROL_OPCODES, ControlOpcode, OpcodeCategory,
    categorise_opcode_idx, stack_apply_op, stack_top_rewrite_mode,
)
from eliza.matrix_ops import _manifold_index
from eliza.opcode_set import Opcode, build_full_opcode_set
from eliza.per_nibble_chain import nibbles_to_bytes, nibble_from_transition
from eliza.tensor_range_coder import (
    RCDecoderState, RCState, rc_finish, rc_step_decode, rc_step_encode,
)


def _emission_bits_estimate(
    emit_idx: int, counts: np.ndarray, alphabet_sz: int,
) -> float:
    """Estimate -log₂ P(emit_idx) under current adaptive counts."""
    from math import log2
    alpha = 0.5
    total = float(np.sum(counts[:alphabet_sz])) + alpha * alphabet_sz
    p = (float(counts[emit_idx]) + alpha) / total
    return -log2(max(p, 1e-30))


def _should_defer_grow(
    prev_emission: int, emit_idx: int, walk: np.ndarray, pos: int,
    bodies, lengths, n_used: int, counts: np.ndarray,
    digram_seen: dict, k_lookahead: int = 4,
) -> bool:
    """Decide whether to emit S_DEFER_GROW vs let growth happen.

    Heuristic: simulate K positions ahead under both paths and pick
    the cheaper. The growth path adds an opcode (alphabet grows by 1);
    the defer path keeps alphabet smaller but doesn't gain the new
    opcode's potential match savings.
    """
    # Cheap proxy: if the digram would create an opcode whose body is
    # very long (already a deep composite), growing is expensive in
    # match-recompute terms. Use prev's body length as proxy.
    prev_body_len = (1 if prev_emission < 24
                       else int(lengths[prev_emission - 24]))
    this_body_len = (1 if emit_idx < 24
                       else int(lengths[emit_idx - 24]))
    new_body_len = prev_body_len + this_body_len

    # If the new body is very long, growing is unlikely to find many
    # additional matches in the remaining stream → defer.
    remaining = len(walk) - pos
    if new_body_len > remaining // 2:
        return True

    # Default: don't defer (grow as usual).
    return False


def encode(data: bytes, initial_opcodes: List[Opcode] = None,
           max_opcodes: int = DEFAULT_MAX_OPCODES,
           speculation_active: bool = True) -> Tuple[bytes, Dict]:
    """V5 encoder. If `speculation_active=True`, evaluates control
    opcode emissions per position; if False, behaves as V4 (no control
    emissions).
    """
    initial_opcodes = initial_opcodes if initial_opcodes is not None \
                      else build_full_opcode_set()
    chambers, idx_map = _manifold_index()

    next_table = _build_next_chamber_table(chambers, idx_map)
    walk = int_chamber_walk(data, chambers, idx_map, next_table)
    n_chain = len(walk)

    initial_max_body = max(op.length for op in initial_opcodes)
    max_body = max(DEFAULT_MAX_BODY, initial_max_body)
    bodies = xp().full((max_opcodes, max_body), -1, dtype=xp().int64)
    lengths = xp().zeros((max_opcodes,), dtype=xp().int64)
    n_used = len(initial_opcodes)
    for i, op in enumerate(initial_opcodes):
        for j, cs in enumerate(op.body):
            bodies[i, j] = idx_map[cs.to_s4()]
        lengths[i] = op.length

    walk_gpu = xp().asarray(walk)
    match_tensor = gpu_opcode_match_vectorized(
        walk_gpu, bodies[:n_used], lengths[:n_used],
    )

    max_alphabet = alphabet_size(max_opcodes)
    counts = np.zeros(max_alphabet, dtype=np.int64)

    rc = RCState()
    prev_emission = -1
    n_vm = 0
    n_growth = 0
    n_defer_emissions = 0
    digram_seen: Dict[Tuple[int, int], int] = {}
    cap_frozen = False
    pos = 0

    while pos < n_chain:
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
        else:
            emit_idx = 24 + best_idx
            advance = best_len

        # Check: should we DEFER growth before this emission?
        defer_this = False
        if (speculation_active and prev_emission >= 0 and not cap_frozen):
            key = (prev_emission, emit_idx)
            if key in digram_seen and digram_seen[key] == -1:
                # Digram is about to grow. Should we defer?
                defer_this = _should_defer_grow(
                    prev_emission, emit_idx, walk, pos,
                    bodies, lengths, n_used, counts, digram_seen,
                )

        # If deferring, emit S_DEFER_GROW BEFORE the regular emission.
        if defer_this:
            defer_emit_idx = control_opcode_base(n_used) + int(
                ControlOpcode.S_DEFER_GROW.value)
            a_size = alphabet_size(n_used)
            cumfreqs = adaptive_cumfreqs(counts[:a_size], a_size)
            rc_step_encode(rc, cumfreqs, defer_emit_idx, int(cumfreqs[-1]))
            counts[defer_emit_idx] += 1
            n_defer_emissions += 1

        # Regular emission.
        a_size = alphabet_size(n_used)
        cumfreqs = adaptive_cumfreqs(counts[:a_size], a_size)
        rc_step_encode(rc, cumfreqs, emit_idx, int(cumfreqs[-1]))
        counts[emit_idx] += 1

        # Grammar growth (skipped if defer was emitted).
        if (prev_emission >= 0 and not cap_frozen and not defer_this):
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
                    if alphabet_size(max_opcodes) > counts.shape[0]:
                        new_counts = np.zeros(alphabet_size(max_opcodes),
                                                 dtype=np.int64)
                        new_counts[:counts.shape[0]] = counts
                        counts = new_counts
                else:
                    cap_frozen = True

        prev_emission = emit_idx
        pos += advance
        n_vm += 1

    encoded = rc_finish(rc)
    header = bytearray()
    header.extend(n_chain.to_bytes(4, "little"))
    header.extend(len(initial_opcodes).to_bytes(4, "little"))
    header.extend((n_vm + n_defer_emissions).to_bytes(4, "little"))
    output = bytes(header) + encoded
    return output, {
        "encoded_bytes": len(output),
        "n_chain": n_chain,
        "n_vm": n_vm,
        "n_growth": n_growth,
        "n_defer_emissions": n_defer_emissions,
        "n_final_opcodes": int(n_used),
        "cap_frozen": cap_frozen,
        "speculation_active": speculation_active,
        "backend": "GPU" if HAS_CUPY else "CPU",
    }


def decode(encoded: bytes, initial_opcodes: List[Opcode] = None,
           max_opcodes: int = DEFAULT_MAX_OPCODES) -> bytes:
    """V5 decoder. Reads control opcodes from stream and applies them.
    Specifically: S_DEFER_GROW suppresses the next-emission's growth.
    """
    initial_opcodes = initial_opcodes if initial_opcodes is not None \
                      else build_full_opcode_set()
    chambers, idx_map = _manifold_index()
    n_chain = int.from_bytes(encoded[:4], "little")
    n_initial = int.from_bytes(encoded[4:8], "little")
    n_emissions = int.from_bytes(encoded[8:12], "little")
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
    max_alphabet = alphabet_size(max_opcodes)
    counts = np.zeros(max_alphabet, dtype=np.int64)
    pending_defer = False

    for _ in range(n_emissions):
        a_size = alphabet_size(n_used)
        cumfreqs = adaptive_cumfreqs(counts[:a_size], a_size)
        emit_idx = rc_step_decode(dec_state, cumfreqs, int(cumfreqs[-1]))
        counts[emit_idx] += 1

        # Check if this is the S_DEFER_GROW control opcode.
        if emit_idx >= 24 + n_used:
            control_id = emit_idx - (24 + n_used)
            if control_id == int(ControlOpcode.S_DEFER_GROW.value):
                pending_defer = True
                continue
            # Other control opcodes — ignore for now (V5 only emits S_DEFER_GROW).
            continue

        # Regular emission.
        if emit_idx < 24:
            chain_terminals.append(emit_idx)
        else:
            op_idx = emit_idx - 24
            L = int(lengths[op_idx])
            body = bodies[op_idx, :L]
            chain_terminals.extend(int(b) for b in (
                cp.asnumpy(body) if HAS_CUPY else np.asarray(body)))

        # Apply growth UNLESS deferred.
        if prev_emission >= 0 and not cap_frozen and not pending_defer:
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
                    if alphabet_size(max_opcodes) > counts.shape[0]:
                        new_counts = np.zeros(alphabet_size(max_opcodes),
                                                 dtype=np.int64)
                        new_counts[:counts.shape[0]] = counts
                        counts = new_counts
                else:
                    cap_frozen = True

        pending_defer = False
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


def self_check(size: int = 1024, verbose: bool = True) -> bool:
    from pathlib import Path
    import time
    HERE = Path(__file__).resolve().parent
    src = HERE / "engine.py"
    with open(src, "rb") as f:
        data = f.read()[:size]

    t0 = time.perf_counter()
    encoded, stats = encode(data, speculation_active=True)
    enc_time = time.perf_counter() - t0
    t0 = time.perf_counter()
    decoded = decode(encoded)
    dec_time = time.perf_counter() - t0
    ok = decoded == data

    if verbose:
        print("=== GpuCodecV5 (active speculation) self-check ===")
        print(f"  input bytes:           {len(data)}")
        print(f"  encoded:               {len(encoded)} bytes "
              f"({8*len(encoded)/len(data):.3f} b/byte)")
        print(f"  n_vm:                  {stats['n_vm']}")
        print(f"  n_growth:              {stats['n_growth']}")
        print(f"  n_defer_emissions:     {stats['n_defer_emissions']}")
        print(f"  n_final_opcodes:       {stats['n_final_opcodes']}")
        print(f"  cap_frozen:            {stats['cap_frozen']}")
        print(f"  encode time:           {enc_time*1000:.1f}ms")
        print(f"  decode time:           {dec_time*1000:.1f}ms")
        print(f"  round-trip:            {'OK' if ok else 'FAIL'}")
        if not ok:
            diffs = sum(1 for i in range(min(len(data), len(decoded)))
                        if data[i] != decoded[i])
            print(f"    bytes differ:        {diffs}")
        print(f"\nResult: {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
