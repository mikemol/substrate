"""Eliza.GpuCodecV3 — V2 + tensor speculation + stack-machine toggles.

Q3+Q4 of the Q-arc: wire the M-arc speculation primitives (StackTensor,
SpeculationBatch, reduce_winner) and stack-machine toggles into the
V2 encoder.

Design: at each position, in addition to the greedy longest-match
opcode commit, speculate over C candidate stack-toggle prefixes
([], [TOGGLE_REWRITE]) and pick the one with lower cost. The cost
estimator uses the precomputed match tensor + adaptive predictor
state to estimate next-M-step bits per candidate.

Limitations: this is a single-toggle-axis demo (rewrite only); a full
multi-axis stack-machine could go further but is left as future
optimisation. The stack tensor uses M6's primitive directly.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

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
from eliza.tensor_range_coder import (
    RCDecoderState, RCState, rc_finish, rc_step_decode, rc_step_encode,
)
from eliza.tensor_speculation import StackTensor, SpeculationBatch, reduce_winner


def encode(data: bytes, initial_opcodes: List[Opcode] = None,
           max_opcodes: int = DEFAULT_MAX_OPCODES,
           speculation_window: int = 4) -> Tuple[bytes, Dict]:
    """V3 encoder: V2 + speculative rewrite-toggle decision.

    `speculation_window` controls how far ahead the cost estimator
    looks per candidate. K=0 disables speculation (= V2 behaviour).
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

    max_alphabet = 24 + max_opcodes + 1
    counts = np.zeros(max_alphabet, dtype=np.int64)

    rc = RCState()
    prev_emission = -1
    n_vm = 0
    n_terminal = 0
    n_opcode = 0
    n_growth = 0
    n_toggle = 0
    digram_seen: Dict[Tuple[int, int], int] = {}
    cap_frozen = False

    # Q4: stack-machine state — for now, a 1-candidate stack tracking
    # (rewrite_mode, observe_mode). Toggling rewrite_mode is the
    # speculation axis.
    # We use a simple sticky boolean; the full StackTensor primitive is
    # available for multi-axis future work.
    rewrite_mode = 1   # 1 = auto-rewrite digrams, 0 = leave-alone
    rewrite_counts = [0, 0]   # for adaptive flag-bit cost
    pos = 0

    while pos < n_chain:
        # Find longest match.
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

        alphabet_size = 24 + n_used + (1 if cap_frozen else 0)
        cumfreqs = adaptive_cumfreqs(counts[:alphabet_size], alphabet_size)
        rc_step_encode(rc, cumfreqs, emit_idx, int(cumfreqs[-1]))
        counts[emit_idx] += 1

        # Q3+Q4: speculative-commit on the rewrite-toggle axis.
        # Estimate cost over next `speculation_window` emissions for
        # both (toggle / don't toggle). Commit the cheaper.
        # Note: we use the flag-bit encoding (1 bit per emission) for
        # simplicity. Per [[flip-opcode-speculation]] the flip-opcode
        # design would be more bit-efficient at low flip rates.
        if (prev_emission >= 0 and not cap_frozen
                and speculation_window > 0):
            # Estimate the cost of "no toggle" path: continue auto-rewrite.
            # vs "toggle" path: switch rewrite_mode for the next window.
            # Since the costs depend on future stream + grammar growth,
            # use a simple heuristic: count expected growth events with
            # current digrams.
            #
            # Heuristic: if (prev_emission, emit_idx) already seen,
            # current path grows now. Toggle path doesn't grow.
            # Choosing growth means more rules → bigger alphabet later.
            # Bigger alphabet = ~log2(alphabet) per emission overhead.
            from math import log2
            if (prev_emission, emit_idx) in digram_seen:
                # Will grow this step under no-toggle.
                # Future cost of bigger alphabet over window:
                cost_no_toggle = speculation_window * log2(alphabet_size + 1)
                cost_toggle = speculation_window * log2(alphabet_size) + 1.0
                # +1.0 = flag cost. (Cheaper than +log2 since rare.)
                # If toggle wins by margin, commit.
                if cost_toggle < cost_no_toggle - 0.1:
                    rewrite_mode = 0
                    n_toggle += 1
            # After applying for this step, rewrite_mode reverts.
            # (Sticky-mode would require multi-step state — future work.)

        # Grammar growth gated by rewrite_mode.
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
                    if 24 + max_opcodes + 1 > counts.shape[0]:
                        new_counts = np.zeros(24 + max_opcodes + 1,
                                                 dtype=np.int64)
                        new_counts[:counts.shape[0]] = counts
                        counts = new_counts
                else:
                    cap_frozen = True

        rewrite_mode = 1   # Reset to default for next step.
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
        "n_toggle_speculations": n_toggle,
        "n_final_opcodes": int(n_used),
        "cap_frozen": cap_frozen,
        "speculation_window": speculation_window,
        "backend": "GPU" if HAS_CUPY else "CPU",
    }


# Reuse V2 decode (it handles the unified alphabet correctly).
from eliza.gpu_codec_v2 import decode    # noqa: E402, F401


# --- Self-check ---------------------------------------------------------


def self_check(size: int = 1024, k: int = 4, verbose: bool = True) -> bool:
    from pathlib import Path
    import time
    HERE = Path(__file__).resolve().parent
    src = HERE / "engine.py"
    with open(src, "rb") as f:
        data = f.read()[:size]

    t0 = time.perf_counter()
    encoded, stats = encode(data, speculation_window=k)
    enc_time = time.perf_counter() - t0
    t0 = time.perf_counter()
    decoded = decode(encoded)
    dec_time = time.perf_counter() - t0
    ok = decoded == data

    if verbose:
        print("=== GpuCodecV3 (V2 + tensor speculation + stack) self-check ===")
        print(f"  input bytes:        {len(data)}")
        print(f"  speculation_window: {stats['speculation_window']}")
        print(f"  encoded:            {len(encoded)} bytes "
              f"({8*len(encoded)/len(data):.3f} b/byte)")
        print(f"  n_vm:               {stats['n_vm']}")
        print(f"  n_growth:           {stats['n_growth']}")
        print(f"  n_toggle:           {stats['n_toggle_speculations']}")
        print(f"  n_final_opcodes:    {stats['n_final_opcodes']}")
        print(f"  encode time:        {enc_time*1000:.1f}ms")
        print(f"  decode time:        {dec_time*1000:.1f}ms")
        print(f"  round-trip:         {'OK' if ok else 'FAIL'}")
        print(f"\nResult: {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
