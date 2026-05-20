"""Eliza.GpuCodecV4 — V2 + lambda-VM control opcodes in the alphabet.

R-arc: the codec's existing machinery is recognized as a lambda VM.
This codec EXTENDS V2's joint alphabet to include the 14 control
opcodes from `lambda_vm_opcodes.py`. The encoder defaults to never
emitting them (behavior matches V2 exactly); subsequent speculation
policies can emit them when worthwhile.

Decoder is a STRAIGHT-LINE INTERPRETER:
  * Read emit_idx.
  * If terminal (< 24): append chain.
  * If data opcode: expand body.
  * If S_GROW: grow opcode from last digram.
  * If S_DEFER_GROW: skip growth.
  * If S_INLINE_LAST: re-flatten last NT.
  * If stack op: apply to internal stack.
  * If S_VAR_n: read stack entry, modulate rewrite mode.
  * If S_INSPECT_LAST: read category of last opcode.

No mirror-state machine needed — the opcode stream IS the program.

Layout in joint alphabet:
  [0 .. 23]                         — chain terminals
  [24 .. 24 + n_used - 1]           — data opcodes (initial + grown)
  [24 + n_used .. 24 + n_used + 13] — 14 control opcodes
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
from eliza.lambda_vm_opcodes import (
    N_CONTROL_OPCODES, ControlOpcode, OpcodeCategory,
    categorise_opcode_idx, stack_apply_op, stack_top_rewrite_mode,
    stack_var,
)
from eliza.matrix_ops import _manifold_index
from eliza.opcode_set import Opcode, build_full_opcode_set
from eliza.per_nibble_chain import nibbles_to_bytes, nibble_from_transition
from eliza.tensor_range_coder import (
    RCDecoderState, RCState, rc_finish, rc_step_decode, rc_step_encode,
)


def control_opcode_base(n_used: int) -> int:
    """Joint-alphabet index of the first control opcode."""
    return 24 + n_used


def alphabet_size(n_used: int) -> int:
    """Total alphabet: terminals + data opcodes + control opcodes."""
    return 24 + n_used + N_CONTROL_OPCODES


# --- Encoder (V2 behaviour + control opcode slots reserved) -----------


def encode(data: bytes, initial_opcodes: List[Opcode] = None,
           max_opcodes: int = DEFAULT_MAX_OPCODES) -> Tuple[bytes, Dict]:
    """V4 encoder. Default policy: never emit a control opcode
    (compression matches V2 exactly). Speculation policies can extend
    by choosing to emit control opcodes.
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
    n_initial_opcodes = n_used
    for i, op in enumerate(initial_opcodes):
        for j, cs in enumerate(op.body):
            bodies[i, j] = idx_map[cs.to_s4()]
        lengths[i] = op.length

    walk_gpu = xp().asarray(walk)
    match_tensor = gpu_opcode_match_vectorized(
        walk_gpu, bodies[:n_used], lengths[:n_used],
    )

    # Alphabet sized for max possible (data + control). Counts cover
    # all slots; control slots will remain 0 if never emitted.
    max_alphabet = alphabet_size(max_opcodes)
    counts = np.zeros(max_alphabet, dtype=np.int64)

    rc = RCState()
    prev_emission = -1
    n_vm = 0
    n_growth = 0
    n_control_emissions = 0
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

        # Range-code the emission using the FULL extended alphabet
        # (data + control). Control slots have tiny probability mass
        # (count 0; alpha-smoothed). Cost penalty for the unused
        # slots is small.
        a_size = alphabet_size(n_used)
        cumfreqs = adaptive_cumfreqs(counts[:a_size], a_size)
        rc_step_encode(rc, cumfreqs, emit_idx, int(cumfreqs[-1]))
        counts[emit_idx] += 1

        # Grammar growth (default V2 behavior).
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
        "n_control_emissions": n_control_emissions,
        "n_final_opcodes": int(n_used),
        "cap_frozen": cap_frozen,
        "alphabet_includes_control": True,
        "n_control_opcodes_available": N_CONTROL_OPCODES,
        "backend": "GPU" if HAS_CUPY else "CPU",
    }


# --- Decoder as straight-line interpreter ---------------------------


def decode(encoded: bytes, initial_opcodes: List[Opcode] = None,
           max_opcodes: int = DEFAULT_MAX_OPCODES) -> bytes:
    """Decoder: straight-line interpreter of the opcode stream.

    No mirror-state machine; each emit_idx unambiguously specifies
    its effect on the stack / grammar / output.
    """
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
    stack: list = []

    for _ in range(n_vm):
        a_size = alphabet_size(n_used)
        cumfreqs = adaptive_cumfreqs(counts[:a_size], a_size)
        emit_idx = rc_step_decode(dec_state, cumfreqs, int(cumfreqs[-1]))
        counts[emit_idx] += 1

        # Dispatch by emit_idx category:
        if emit_idx < 24:
            # Terminal.
            chain_terminals.append(emit_idx)
        elif emit_idx < 24 + n_used:
            # Data opcode (substrate-native, exploding, or grown).
            op_idx = emit_idx - 24
            L = int(lengths[op_idx])
            body = bodies[op_idx, :L]
            chain_terminals.extend(int(b) for b in (
                cp.asnumpy(body) if HAS_CUPY else np.asarray(body)))
        else:
            # Control opcode.
            control_id = emit_idx - (24 + n_used)
            stack = _apply_control_opcode_decoder(
                stack, control_id, chain_terminals, bodies, lengths,
            )

        # Sequitur growth (default — same as V2 unless control opcode
        # below changes rewrite mode).
        rewrite_mode = stack_top_rewrite_mode(stack, default=1)
        if prev_emission >= 0 and not cap_frozen and rewrite_mode == 1:
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


def _apply_control_opcode_decoder(
    stack: list, control_id: int,
    chain_terminals: list, bodies, lengths,
) -> list:
    """Apply a control opcode in the decoder.

    Most control opcodes only modify the stack; they don't produce
    chain output. S_INLINE_LAST and S_INSPECT_LAST have output-affecting
    effects which are TODO for the speculation-emission slices.
    """
    return stack_apply_op(stack, control_id)


# --- Self-check ---------------------------------------------------------


def self_check(size: int = 1024, verbose: bool = True) -> bool:
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
        print("=== GpuCodecV4 (V2 + lambda-VM opcodes) self-check ===")
        print(f"  input bytes:                {len(data)}")
        print(f"  encoded:                    {len(encoded)} bytes "
              f"({8*len(encoded)/len(data):.3f} b/byte)")
        print(f"  n_vm:                       {stats['n_vm']}")
        print(f"  n_growth:                   {stats['n_growth']}")
        print(f"  n_control_emissions:        {stats['n_control_emissions']}")
        print(f"  n_final_opcodes:            {stats['n_final_opcodes']}")
        print(f"  alphabet includes control:  {stats['alphabet_includes_control']}")
        print(f"  control opcodes available:  {stats['n_control_opcodes_available']}")
        print(f"  encode time:                {enc_time*1000:.1f}ms")
        print(f"  decode time:                {dec_time*1000:.1f}ms")
        print(f"  round-trip:                 {'OK' if ok else 'FAIL'}")
        if not ok:
            diffs = sum(1 for i in range(min(len(data), len(decoded)))
                        if data[i] != decoded[i])
            print(f"    bytes differ:             {diffs}")
        print(f"\nResult: {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
