"""Eliza.GpuCodecV6 — V5 generalised over the action algebra A.

U-arc codec. Each emission carries a `RuleAction ∈ A`; at U1 the
action is always identity, so V6's stream output is byte-identical
to V5. Later U-arc slices enable non-identity actions:

  U2: + start_phase     (phase-only AffineProjection)
  U3: + length_mask     (full AffineProjection — LZ77 emergence)
  U4: + f2_patch k=1    (single-bit F₂Patch)
  U5: + f2_patch k≤K    (sparse F₂Patch)
  U6: + span_coupling   (stripe overlap_mask)
  U7: + full F₂ mask    (full SpanCoupling, H-rung non-commutative)
  U8: integrated speculation across all factors.

At each slice the encoder selectively emits non-identity actions
only when the speculation cost estimate says it pays. With every
slice having (E1)-identity-reproduces-V5 in its self-check, V6 is
a strictly monotonic refinement.

The stream format extends V5's joint alphabet by adding a single
control opcode S_RULE_ACTION that, when emitted, signals "next emission
carries action data encoded inline." U1 never emits S_RULE_ACTION,
so the format is byte-compatible with V5 at U1.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from eliza.alphabets import NIBBLE_TO_PERM, ORIGIN, perm_compose
from eliza.chain_symbol import ChainSymbol
from eliza.gpu_codec_v2 import (
    _build_next_chamber_table, _expand_emission_body, adaptive_cumfreqs,
    grow_body_capacity, int_chamber_walk, try_grow_opcode,
    DEFAULT_MAX_BODY, DEFAULT_MAX_OPCODES,
)
from eliza.gpu_kernels import (
    HAS_CUPY, cp, gpu_opcode_match_vectorized, xp,
)
from eliza.matrix_ops import _manifold_index
from eliza.opcode_set import Opcode, build_full_opcode_set
from eliza.per_nibble_chain import nibbles_to_bytes, nibble_from_transition
from eliza.rule_action import IDENTITY, RuleAction, apply_to_body
from eliza.tensor_range_coder import (
    RCDecoderState, RCState, rc_finish, rc_step_decode, rc_step_encode,
)


# V6 introduces one new control slot (S_RULE_ACTION) but never emits
# it at U1 — so the alphabet/stream is V5-byte-compatible. The slot
# becomes live starting at U2.
N_V6_CONTROL_OPCODES = 0   # U1: no new control opcodes emitted yet.


def alphabet_size(n_used: int) -> int:
    """Joint alphabet: terminals + data opcodes + V6 controls."""
    return 24 + n_used + N_V6_CONTROL_OPCODES


def _choose_emission(
    pos: int, match_tensor, n_used: int, walk,
) -> Tuple[int, int, RuleAction]:
    """Choose (emit_idx, advance, action) for the current position.

    U1: action is always IDENTITY. Best-match greedy logic identical
    to V5. Later slices enrich this with speculation over non-trivial
    actions.
    """
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

    return emit_idx, advance, IDENTITY


def encode(data: bytes, initial_opcodes: List[Opcode] = None,
           max_opcodes: int = DEFAULT_MAX_OPCODES) -> Tuple[bytes, Dict]:
    """V6 encoder. U1: identity action only — output equals V5 exactly."""
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
    n_initial_opcodes = n_used
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
    n_nontrivial_actions = 0  # U1: always 0
    digram_seen: Dict[Tuple[int, int], int] = {}
    cap_frozen = False
    pos = 0

    while pos < n_chain:
        emit_idx, advance, action = _choose_emission(
            pos, match_tensor, n_used, walk,
        )

        # U1 invariant: action is identity. Later slices relax this
        # and emit S_RULE_ACTION + action payload when worthwhile.
        if not action.is_identity():
            n_nontrivial_actions += 1
            raise NotImplementedError(
                "U1 emits identity actions only; later U-arc slices "
                "will introduce action-emission control opcodes."
            )

        a_size = alphabet_size(n_used)
        cumfreqs = adaptive_cumfreqs(counts[:a_size], a_size)
        rc_step_encode(rc, cumfreqs, emit_idx, int(cumfreqs[-1]))
        counts[emit_idx] += 1

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
    header.extend(n_initial_opcodes.to_bytes(4, "little"))
    header.extend(n_vm.to_bytes(4, "little"))
    output = bytes(header) + encoded
    return output, {
        "encoded_bytes": len(output),
        "n_chain": n_chain,
        "n_vm": n_vm,
        "n_growth": n_growth,
        "n_nontrivial_actions": n_nontrivial_actions,
        "n_final_opcodes": int(n_used),
        "cap_frozen": cap_frozen,
        "u_arc_slice": "U1",
        "action_algebra_factors": ("V4-residue@identity-only",),
        "backend": "GPU" if HAS_CUPY else "CPU",
    }


def decode(encoded: bytes, initial_opcodes: List[Opcode] = None,
           max_opcodes: int = DEFAULT_MAX_OPCODES) -> bytes:
    """V6 decoder. U1: no action-payload reads — straight V5 semantics."""
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
    max_alphabet = alphabet_size(max_opcodes)
    counts = np.zeros(max_alphabet, dtype=np.int64)

    for _ in range(n_vm):
        a_size = alphabet_size(n_used)
        cumfreqs = adaptive_cumfreqs(counts[:a_size], a_size)
        emit_idx = rc_step_decode(dec_state, cumfreqs, int(cumfreqs[-1]))
        counts[emit_idx] += 1

        # U1: emit_idx is purely terminal-or-data-opcode; no action
        # payload to read. Identity application of identity is identity.
        action = IDENTITY

        if emit_idx < 24:
            chain_terminals.append(emit_idx)
        else:
            op_idx = emit_idx - 24
            L = int(lengths[op_idx])
            body = bodies[op_idx, :L]
            transformed = apply_to_body(body, action)   # identity at U1
            chain_terminals.extend(int(b) for b in (
                cp.asnumpy(transformed) if HAS_CUPY else np.asarray(transformed)))

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
                    if alphabet_size(max_opcodes) > counts.shape[0]:
                        new_counts = np.zeros(alphabet_size(max_opcodes),
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


def self_check(size: int = 1024, verbose: bool = True) -> bool:
    """Round-trip + (E1) byte-identity vs V5 at identity-only action."""
    from pathlib import Path
    import time
    from eliza import gpu_codec_v2 as v2
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
    ok_roundtrip = decoded == data

    # (E1): V6 stream at identity-only action equals V2/V5 stream.
    v2_encoded, _ = v2.encode(data)
    ok_identity = encoded == v2_encoded

    if verbose:
        print("=== GpuCodecV6 (U-arc U1: identity-only) self-check ===")
        print(f"  input bytes:                {len(data)}")
        print(f"  encoded:                    {len(encoded)} bytes "
              f"({8*len(encoded)/len(data):.3f} b/byte)")
        print(f"  n_vm:                       {stats['n_vm']}")
        print(f"  n_growth:                   {stats['n_growth']}")
        print(f"  n_nontrivial_actions:       {stats['n_nontrivial_actions']}")
        print(f"  u_arc_slice:                {stats['u_arc_slice']}")
        print(f"  action_algebra:             {stats['action_algebra_factors']}")
        print(f"  encode time:                {enc_time*1000:.1f}ms")
        print(f"  decode time:                {dec_time*1000:.1f}ms")
        print(f"  round-trip:                 {'OK' if ok_roundtrip else 'FAIL'}")
        print(f"  V6==V2 at identity (E1):    {'OK' if ok_identity else 'FAIL'}")
        if not ok_identity:
            print(f"    V6 len={len(encoded)}, V2 len={len(v2_encoded)}")
        print(f"\nResult: {'OK' if ok_roundtrip and ok_identity else 'FAIL'}")
    return ok_roundtrip and ok_identity


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
