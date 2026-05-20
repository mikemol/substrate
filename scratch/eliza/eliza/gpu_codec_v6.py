"""Eliza.GpuCodecV6 — V5 generalised over the action algebra A.

U-arc codec. Each emission carries a `RuleAction ∈ A`; at U1 the
action is always identity, so V6's stream output is byte-identical
to V5. Each subsequent U-arc slice enables one factor of A:

  U1: identity action only (== V5).
  U2: + start_phase     (phase-only AffineProjection).
  U3: + length_mask     (full AffineProjection — LZ77 emergence).
  U4: + f2_patch k=1    (single-bit F₂Patch).
  U5: + f2_patch k≤K    (sparse F₂Patch).
  U6: + span_coupling   (stripe overlap_mask).
  U7: + full F₂ mask    (full SpanCoupling, H-rung non-commutative).
  U8: integrated speculation across all factors.

Stream format. V6 extends the joint alphabet with control opcodes
that signal action-tagged emissions:

  S_PHASE      (U2): next opcode emission has start_phase > 0.
  S_LENGTH     (U3): next emission has length_mask >= 0.
  S_PATCH1     (U4): next emission has 1-bit F₂Patch.
  S_PATCHK     (U5): next emission has multi-bit F₂Patch.
  S_SPAN       (U6/U7): next emission is a bifilar span.

At each slice the encoder may opt into emitting the control opcode
when speculation says it saves bits; otherwise it stays at identity.
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


# V6 control opcodes (joint-alphabet slots after data opcodes).
# Each slice enables one slot; encoder may opt in to emit.
S_PHASE = 0           # U2: per-emission phase tag (legacy inline)
S_AFFINE = 1          # U3: per-emission affine tag (legacy inline)
S_FLIP_PATCH1 = 2     # U4: flip-paradigm toggle for k=1 F₂Patch mode
N_V6_CONTROL_OPCODES = 3


def alphabet_size(n_used: int) -> int:
    """Joint alphabet: terminals + data opcodes + V6 controls."""
    return 24 + n_used + N_V6_CONTROL_OPCODES


def _control_index(slot: int, n_used: int) -> int:
    return 24 + n_used + slot


# Phase-search heuristic constant. The phase emission costs roughly
# 2 control-symbol-worth of bits (S_PHASE + phase int); require the
# phase-tagged match to win by at least PHASE_MARGIN extra chain
# steps to break even.
PHASE_MARGIN = 2


def _try_phase_match(walk, pos: int, bodies, lengths, n_used: int,
                       best_idx: int, best_len: int):
    """U2 phase-search: scan rules for phase>0 matches that beat the
    current greedy by ≥ PHASE_MARGIN chain steps.

    Returns (phase, opcode_idx, match_len) for the winning phase>0
    match, or None if no phase>0 emission beats greedy.

    Implementation: iterate over all rules and check phase ∈ [1, body_len-1].
    Naive but vectorisable later (matricised in U8).
    """
    xp_mod = xp()
    walk_np = (cp.asnumpy(walk) if HAS_CUPY else np.asarray(walk))
    n_chain = walk_np.shape[0]
    target_len = best_len + PHASE_MARGIN

    best_phase = 0
    best_phase_idx = best_idx
    best_phase_len = best_len

    for op_idx in range(n_used):
        L = int(lengths[op_idx])
        if L <= 1:
            continue
        body_np = (cp.asnumpy(bodies[op_idx, :L]) if HAS_CUPY
                   else np.asarray(bodies[op_idx, :L]))
        for phase in range(1, L):
            seg_len = L - phase
            if seg_len <= best_phase_len:
                continue
            if pos + seg_len > n_chain:
                continue
            # Compare body[phase:L] against walk[pos:pos+seg_len].
            if np.array_equal(body_np[phase:L], walk_np[pos:pos + seg_len]):
                if seg_len >= target_len and seg_len > best_phase_len:
                    best_phase = phase
                    best_phase_idx = op_idx
                    best_phase_len = seg_len

    if best_phase == 0:
        return None
    return (best_phase, best_phase_idx, best_phase_len)


def _choose_emission(
    pos: int, match_tensor, n_used: int, walk, bodies, lengths,
    speculate_phase: bool = True,
) -> Tuple[int, int, RuleAction, int]:
    """Choose (emit_idx, advance, action, secondary_phase_int).

    Returns:
        emit_idx: joint-alphabet symbol (terminal / data opcode /
                  S_PHASE control).
        advance: number of chain steps to advance.
        action: RuleAction; identity unless phase>0 chosen.
        secondary_phase_int: integer phase to emit AFTER S_PHASE
                             control + opcode_idx (only valid when
                             emit_idx is the S_PHASE control).
    """
    if pos < match_tensor.shape[0] and n_used > 0:
        row = match_tensor[pos, :n_used]
        best_idx_gpu = xp().argmax(row)
        best_idx = int(best_idx_gpu)
        best_len = int(row[best_idx_gpu])
    else:
        best_idx = 0
        best_len = 0

    if speculate_phase and best_len >= 1 and n_used > 0:
        phase_result = _try_phase_match(
            walk, pos, bodies, lengths, n_used, best_idx, best_len,
        )
        if phase_result is not None:
            phase, phase_idx, phase_len = phase_result
            return (_control_index(S_PHASE, n_used), phase_len,
                    RuleAction(start_phase=phase), (phase << 16) | phase_idx)

    if best_len == 0:
        return int(walk[pos]), 1, IDENTITY, -1

    return 24 + best_idx, best_len, IDENTITY, -1


def _emit_phase_tagged(rc, counts, a_size, opcode_idx, phase):
    """Emit (opcode_idx, phase) AFTER the S_PHASE control symbol has
    been emitted. opcode_idx is in 0..n_used-1; phase is in 1..body_len-1.

    Encoded as two adaptive-cumfreq symbols in the same joint alphabet.
    Decoder mirrors.
    """
    cumfreqs = adaptive_cumfreqs(counts[:a_size], a_size)
    rc_step_encode(rc, cumfreqs, 24 + opcode_idx, int(cumfreqs[-1]))
    counts[24 + opcode_idx] += 1
    cumfreqs = adaptive_cumfreqs(counts[:a_size], a_size)
    rc_step_encode(rc, cumfreqs, min(phase, a_size - 1), int(cumfreqs[-1]))
    counts[min(phase, a_size - 1)] += 1


def _decode_phase_tagged(dec_state, counts, a_size):
    """Inverse of `_emit_phase_tagged`. Returns (opcode_idx, phase)."""
    cumfreqs = adaptive_cumfreqs(counts[:a_size], a_size)
    opc_sym = rc_step_decode(dec_state, cumfreqs, int(cumfreqs[-1]))
    counts[opc_sym] += 1
    cumfreqs = adaptive_cumfreqs(counts[:a_size], a_size)
    phase = rc_step_decode(dec_state, cumfreqs, int(cumfreqs[-1]))
    counts[phase] += 1
    return opc_sym - 24, phase


def _try_patch1_match(walk, pos: int, bodies, lengths, n_used: int,
                        best_len: int, margin: int = 1):
    """U4 single-bit F₂Patch search: find a rule whose body differs
    from `walk[pos:pos+L]` in exactly one chain-symbol position.

    Returns (opcode_idx, length, patch_idx, replacement) if a k=1
    near-match's effective length exceeds best_len + margin; else None.

    Under flip-paradigm, the per-emission cost in patch-mode is 3
    symbols (opcode + patch_idx + replacement); the flip-in/flip-out
    are amortised across the run. So the per-emission margin is
    just `margin = 1` (one extra symbol-worth of beneficence).
    """
    walk_np = (cp.asnumpy(walk) if HAS_CUPY else np.asarray(walk))
    n_chain = walk_np.shape[0]
    best_op = -1
    best_len_seen = 0
    best_idx = -1
    best_repl = -1
    for op_idx in range(n_used):
        L = int(lengths[op_idx])
        if L <= 1:
            continue
        target_len = min(L, n_chain - pos)
        if target_len <= best_len_seen:
            continue
        body_np = (cp.asnumpy(bodies[op_idx, :target_len]) if HAS_CUPY
                   else np.asarray(bodies[op_idx, :target_len]))
        diffs = np.flatnonzero(body_np != walk_np[pos:pos + target_len])
        if diffs.size == 1:
            idx = int(diffs[0])
            repl = int(walk_np[pos + idx])
            if target_len > best_len_seen:
                best_op = op_idx
                best_len_seen = target_len
                best_idx = idx
                best_repl = repl
    if best_op < 0 or best_len_seen < best_len + margin:
        return None
    return (best_op, best_len_seen, best_idx, best_repl)


def _try_affine_match(walk, pos: int, bodies, lengths, n_used: int,
                        best_len: int, margin: int = 3):
    """U3 affine-search: scan (rule, phase, length) for the longest
    `body[phase:phase+length]` matching `walk[pos:pos+length]`.

    Returns (opcode_idx, phase, length) if the match length exceeds
    `best_len + margin` (margin = cost of S_AFFINE + opc + phase +
    length symbols ≈ 3); else None.

    Subsumes the U2 phase-only case (length = body_len - phase).
    Naive O(n_used × max_body²); matricised in U8.
    """
    walk_np = (cp.asnumpy(walk) if HAS_CUPY else np.asarray(walk))
    n_chain = walk_np.shape[0]
    best_op = -1
    best_phase = 0
    best_length = 0
    for op_idx in range(n_used):
        L = int(lengths[op_idx])
        if L <= 1:
            continue
        body_np = (cp.asnumpy(bodies[op_idx, :L]) if HAS_CUPY
                   else np.asarray(bodies[op_idx, :L]))
        for phase in range(0, L):
            max_len = min(L - phase, n_chain - pos)
            if max_len <= best_length:
                continue
            k = 0
            while k < max_len and body_np[phase + k] == walk_np[pos + k]:
                k += 1
            if k > best_length:
                best_op = op_idx
                best_phase = phase
                best_length = k
    if best_op < 0 or best_length < best_len + margin:
        return None
    return (best_op, best_phase, best_length)


def _scan_patch1_run(walk, pos: int, bodies, lengths, n_used: int,
                       horizon: int = 8):
    """Look ahead up to `horizon` positions: at each, check whether a
    k=1 patch-match exists with effective_len > 0.

    Returns list of patch1 results [(opc, length, idx, repl), ...] —
    indexed by position offset; entries are None when no k=1 match.

    Used by the U4 flip-paradigm encoder to decide whether the
    upcoming run is patch-friendly enough to flip into patch-mode.
    """
    out = []
    walk_np = (cp.asnumpy(walk) if HAS_CUPY else np.asarray(walk))
    n_chain = walk_np.shape[0]
    p = pos
    while p < min(pos + horizon, n_chain) and len(out) < horizon:
        out.append(_try_patch1_match(walk, p, bodies, lengths, n_used, 0))
        # Advance optimistically; the encoder's main loop will use
        # actual advance after committing to greedy or patch.
        p += 1
    return out


def encode(data: bytes, initial_opcodes: List[Opcode] = None,
           max_opcodes: int = DEFAULT_MAX_OPCODES,
           speculate_phase: bool = False,
           speculate_affine: bool = False,
           speculate_patch1: bool = False) -> Tuple[bytes, Dict]:
    """V6 encoder. U-arc speculation flags (each defaults off so V6 ==
    V5 byte-identical at speculation_off):
      * speculate_phase  — per-emission phase tag (U2, legacy inline).
      * speculate_affine — per-emission affine tag (U3, legacy inline).
      * speculate_patch1 — flip-paradigm k=1 patch-mode (U4).
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

    max_alphabet = alphabet_size(max_opcodes)
    counts = np.zeros(max_alphabet, dtype=np.int64)

    rc = RCState()
    prev_emission = -1
    n_vm = 0
    n_growth = 0
    n_phase_emissions = 0
    n_affine_emissions = 0
    n_patch1_emissions = 0
    n_flip_patch1 = 0
    patch_mode = False     # U4 flip state: are we in patch-tagged mode?
    digram_seen: Dict[Tuple[int, int], int] = {}
    cap_frozen = False
    pos = 0

    while pos < n_chain:
        # U4 flip-paradigm: at each position decide whether to flip
        # in / out of patch-mode based on lookahead.
        if speculate_patch1 and n_used > 0:
            ahead = _scan_patch1_run(walk, pos, bodies, lengths, n_used,
                                       horizon=4)
            run_count = sum(1 for x in ahead if x is not None)
            if not patch_mode and run_count >= 2:
                # Flip IN to patch-mode.
                a_size = alphabet_size(n_used)
                cumfreqs = adaptive_cumfreqs(counts[:a_size], a_size)
                ctrl = _control_index(S_FLIP_PATCH1, n_used)
                rc_step_encode(rc, cumfreqs, ctrl, int(cumfreqs[-1]))
                counts[ctrl] += 1
                patch_mode = True
                n_flip_patch1 += 1
            elif patch_mode and run_count == 0:
                # Flip OUT of patch-mode.
                a_size = alphabet_size(n_used)
                cumfreqs = adaptive_cumfreqs(counts[:a_size], a_size)
                ctrl = _control_index(S_FLIP_PATCH1, n_used)
                rc_step_encode(rc, cumfreqs, ctrl, int(cumfreqs[-1]))
                counts[ctrl] += 1
                patch_mode = False
                n_flip_patch1 += 1

        if patch_mode:
            patch = _try_patch1_match(walk, pos, bodies, lengths, n_used, 0)
            if patch is None:
                # Forced flip out — no patch match here.
                a_size = alphabet_size(n_used)
                cumfreqs = adaptive_cumfreqs(counts[:a_size], a_size)
                ctrl = _control_index(S_FLIP_PATCH1, n_used)
                rc_step_encode(rc, cumfreqs, ctrl, int(cumfreqs[-1]))
                counts[ctrl] += 1
                patch_mode = False
                n_flip_patch1 += 1
            else:
                opc, length, patch_idx, repl = patch
                a_size = alphabet_size(n_used)
                for sym in (24 + opc, patch_idx, repl):
                    cumfreqs = adaptive_cumfreqs(counts[:a_size], a_size)
                    s = min(sym, a_size - 1)
                    rc_step_encode(rc, cumfreqs, s, int(cumfreqs[-1]))
                    counts[s] += 1
                n_patch1_emissions += 1
                effective_emit = 24 + opc
                pos += length
                n_vm += 1
                prev_emission = effective_emit
                continue
        # U3 affine-search runs first (subsumes U2's phase-only).
        if speculate_affine and n_used > 0:
            # Determine current greedy best_len at pos.
            if pos < match_tensor.shape[0]:
                row = match_tensor[pos, :n_used]
                best_len_now = int(row[xp().argmax(row)])
            else:
                best_len_now = 0
            affine = _try_affine_match(
                walk, pos, bodies, lengths, n_used, best_len_now,
            )
        else:
            affine = None

        if affine is not None:
            opc_idx, phase, length = affine
            a_size = alphabet_size(n_used)
            cumfreqs = adaptive_cumfreqs(counts[:a_size], a_size)
            ctrl_idx = _control_index(S_AFFINE, n_used)
            rc_step_encode(rc, cumfreqs, ctrl_idx, int(cumfreqs[-1]))
            counts[ctrl_idx] += 1
            # Emit (opcode, phase, length).
            for sym in (24 + opc_idx, phase, length):
                cumfreqs = adaptive_cumfreqs(counts[:a_size], a_size)
                sym_clamped = min(sym, a_size - 1)
                rc_step_encode(rc, cumfreqs, sym_clamped, int(cumfreqs[-1]))
                counts[sym_clamped] += 1
            n_affine_emissions += 1
            effective_emit = 24 + opc_idx
            advance = length
            pos += advance
            n_vm += 1
            prev_emission = effective_emit
            continue

        emit_idx, advance, action, phase_payload = _choose_emission(
            pos, match_tensor, n_used, walk, bodies, lengths,
            speculate_phase=speculate_phase,
        )

        a_size = alphabet_size(n_used)
        cumfreqs = adaptive_cumfreqs(counts[:a_size], a_size)
        rc_step_encode(rc, cumfreqs, emit_idx, int(cumfreqs[-1]))
        counts[emit_idx] += 1

        if emit_idx == _control_index(S_PHASE, n_used):
            phase = phase_payload >> 16
            opc_idx = phase_payload & 0xFFFF
            _emit_phase_tagged(rc, counts, a_size, opc_idx, phase)
            n_phase_emissions += 1
            effective_emit = 24 + opc_idx
        else:
            effective_emit = emit_idx

        if prev_emission >= 0 and not cap_frozen:
            key = (prev_emission, effective_emit)
            existing = digram_seen.get(key)
            if existing is None:
                digram_seen[key] = -1
            else:
                prev_body = _expand_emission_body(prev_emission, bodies,
                                                    lengths, n_used)
                this_body = _expand_emission_body(effective_emit, bodies,
                                                    lengths, n_used)
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

        prev_emission = effective_emit
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
        "n_phase_emissions": n_phase_emissions,
        "n_affine_emissions": n_affine_emissions,
        "n_patch1_emissions": n_patch1_emissions,
        "n_flip_patch1": n_flip_patch1,
        "n_final_opcodes": int(n_used),
        "cap_frozen": cap_frozen,
        "u_arc_slice": "U4",
        "action_algebra_factors": ("V4-residue", "start_phase", "length_mask",
                                     "f2_patch[k=1]"),
        "backend": "GPU" if HAS_CUPY else "CPU",
    }


def decode(encoded: bytes, initial_opcodes: List[Opcode] = None,
           max_opcodes: int = DEFAULT_MAX_OPCODES) -> bytes:
    """V6 decoder. Reads S_PHASE control and applies start_phase."""
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
    patch_mode = False    # U4 decoder flip state

    n_emissions = n_vm
    while n_emissions > 0:
        a_size = alphabet_size(n_used)
        cumfreqs = adaptive_cumfreqs(counts[:a_size], a_size)
        emit_idx = rc_step_decode(dec_state, cumfreqs, int(cumfreqs[-1]))
        counts[emit_idx] += 1

        # Flip-paradigm control: S_FLIP_PATCH1 toggles patch_mode and
        # consumes no emission slot. Decoder loops without decrementing.
        if emit_idx == _control_index(S_FLIP_PATCH1, n_used):
            patch_mode = not patch_mode
            continue

        if patch_mode:
            # Read (opc_sym, patch_idx, replacement) AFTER the symbol
            # already read serves AS opc_sym. So emit_idx == opc_sym.
            opc_idx = emit_idx - 24
            cumfreqs = adaptive_cumfreqs(counts[:a_size], a_size)
            patch_idx = rc_step_decode(dec_state, cumfreqs, int(cumfreqs[-1]))
            counts[patch_idx] += 1
            cumfreqs = adaptive_cumfreqs(counts[:a_size], a_size)
            repl = rc_step_decode(dec_state, cumfreqs, int(cumfreqs[-1]))
            counts[repl] += 1
            L = int(lengths[opc_idx])
            body_np = (cp.asnumpy(bodies[opc_idx, :L]) if HAS_CUPY
                       else np.asarray(bodies[opc_idx, :L])).copy()
            if 0 <= patch_idx < L:
                body_np[patch_idx] = repl
            chain_terminals.extend(int(b) for b in body_np)
            effective_emit = 24 + opc_idx
            n_emissions -= 1
            prev_emission = effective_emit
            continue

        n_emissions -= 1
        if emit_idx == _control_index(S_AFFINE, n_used):
            # U3: read (opcode, phase, length).
            triplet = []
            for _i in range(3):
                cumfreqs = adaptive_cumfreqs(counts[:a_size], a_size)
                sym = rc_step_decode(dec_state, cumfreqs, int(cumfreqs[-1]))
                counts[sym] += 1
                triplet.append(sym)
            opc_sym, phase, length = triplet
            opc_idx = opc_sym - 24
            body = bodies[opc_idx, phase:phase + length]
            chain_terminals.extend(int(b) for b in (
                cp.asnumpy(body) if HAS_CUPY else np.asarray(body)))
            effective_emit = 24 + opc_idx
        elif emit_idx == _control_index(S_PHASE, n_used):
            opc_idx, phase = _decode_phase_tagged(dec_state, counts, a_size)
            L = int(lengths[opc_idx])
            body = bodies[opc_idx, phase:L]
            chain_terminals.extend(int(b) for b in (
                cp.asnumpy(body) if HAS_CUPY else np.asarray(body)))
            effective_emit = 24 + opc_idx
        elif emit_idx < 24:
            chain_terminals.append(emit_idx)
            effective_emit = emit_idx
        else:
            op_idx = emit_idx - 24
            L = int(lengths[op_idx])
            body = bodies[op_idx, :L]
            chain_terminals.extend(int(b) for b in (
                cp.asnumpy(body) if HAS_CUPY else np.asarray(body)))
            effective_emit = emit_idx

        if prev_emission >= 0 and not cap_frozen:
            key = (prev_emission, effective_emit)
            existing = digram_seen.get(key)
            if existing is None:
                digram_seen[key] = -1
            else:
                prev_body = _expand_emission_body(prev_emission, bodies,
                                                    lengths, n_used)
                this_body = _expand_emission_body(effective_emit, bodies,
                                                    lengths, n_used)
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
        prev_emission = effective_emit

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
    """Round-trip on engine.py text + (E3) per-factor measurement."""
    from pathlib import Path
    import time
    HERE = Path(__file__).resolve().parent
    src = HERE / "engine.py"
    with open(src, "rb") as f:
        data = f.read()[:size]

    cases = [
        ("identity (U1)", dict(speculate_phase=False, speculate_affine=False,
                                speculate_patch1=False)),
        ("+ phase (U2)",   dict(speculate_phase=True,  speculate_affine=False,
                                speculate_patch1=False)),
        ("+ affine (U3)",  dict(speculate_phase=False, speculate_affine=True,
                                speculate_patch1=False)),
        ("+ patch1 (U4)",  dict(speculate_phase=False, speculate_affine=False,
                                speculate_patch1=True)),
    ]
    results = []
    for name, kw in cases:
        t0 = time.perf_counter()
        enc, stats = encode(data, **kw)
        t = time.perf_counter() - t0
        ok = decode(enc) == data
        bpb = 8 * len(enc) / size
        results.append((name, enc, stats, t, ok, bpb))

    if verbose:
        print("=== GpuCodecV6 (U-arc U3: + length_mask) ===")
        print(f"  input bytes: {len(data)}")
        for name, enc, stats, t, ok, bpb in results:
            print(f"  {name}:")
            print(f"    bytes: {len(enc)}  ({bpb:.3f} b/byte)  "
                  f"phase={stats.get('n_phase_emissions',0)} "
                  f"affine={stats.get('n_affine_emissions',0)} "
                  f"patch1={stats.get('n_patch1_emissions',0)} "
                  f"flips={stats.get('n_flip_patch1',0)}")
            print(f"    time: {t*1000:.0f}ms   round-trip: "
                  f"{'OK' if ok else 'FAIL'}")
        bpb_id = results[0][5]
        for name, _, _, _, _, bpb in results[1:]:
            delta = bpb - bpb_id
            verdict = ("BENEFITS" if delta < -0.01 else
                       "NEUTRAL" if abs(delta) < 0.01 else
                       "REGRESSES")
            print(f"  (E3) {name} vs identity: {verdict} ({delta:+.3f} b/byte)")
    return all(r[4] for r in results)


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
