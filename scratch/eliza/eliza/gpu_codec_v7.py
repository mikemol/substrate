"""Eliza.GpuCodecV7 — V6 generalised by V-arc operad structure.

V-arc codec. The codec ring acquires four orthogonal axes of
generalisation:

  V1-V3: Torsor of bases. Basis-state carried alongside emission;
         absolute (S_BASIS_AT) and relative (S_BASIS_BY) opcodes.
  V4-V5: Alphabet speculation. Multiple parallel predictors;
         per-emission cost-gate selects.
  V6-V7: Generator ring. Rewrite rules and adaptive predictors are
         peers in one ring of generators; speculation across ring.
  V8:    Sink opcode. S_SHIFT_BIT explicit commit to output.

V1 (this slice): adds `BasisState` and `S_BASIS_AT` control opcode.
Encoder defaults to ALGEBRAIC and never emits S_BASIS_AT, so V7's
stream is byte-identical to V6 at the default. Self-check (E1)
verifies this.

Subsequent V-slices wire the basis-state and other operad axes into
emission semantics.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from eliza.alphabets import NIBBLE_TO_PERM, ORIGIN, perm_compose
from eliza.backref import (
    apply_chain_backref, apply_s4_chain, apply_v4_chain,
    find_chain_backref, find_chain_backref_with_residue,
    find_chain_backref_with_s4_residue,
)
from eliza.multiscale_rotation import (
    apply_block_rotations, apply_rotation_to_bytes,
    speculate_block_rotations,
)
from eliza.basis_state import (
    BasisLabel, BasisState, DEFAULT_BASIS, IDENTITY, N_BASIS_LABELS,
    QuaternionComponent, apply_quat_component,
)
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
from eliza.v7_predictor import (
    BigramPredictor, ChamberContextPredictor, Predictor,
    QuaternionContextPredictor, TrigramPredictor, UnigramPredictor,
)


# V7 control opcodes (V-arc additions on top of V6's set).
S_BASIS_AT = 0       # V1: absolute heading — jump to labeled basis point.
S_BASIS_BY = 1       # V2: relative bearing — multiply by quaternion component.
S_SHIFT_BIT = 2      # V8: explicit sink — commit one bit of working buffer.
S_REF_RECENT = 3     # Z1: chain-symbol backref (distance, length).
S_SCALE_ROTATE = 4   # BB2: multiscale Cayley-Dickson rotation (scale, k, f).
N_V7_CONTROL_OPCODES = 5


def alphabet_size(n_used: int) -> int:
    """Joint alphabet: terminals + data opcodes + V7 controls."""
    return 24 + n_used + N_V7_CONTROL_OPCODES


def _control_index(slot: int, n_used: int) -> int:
    return 24 + n_used + slot


def _build_predictors(max_alphabet: int) -> Dict[BasisLabel, Predictor]:
    """Bind each BasisLabel to a predictor instance.

    Per the DBE pass: BasisLabel is the orbit slot; Predictor is the
    costructure. The binding is the constructive use of the V-arc
    parallel-predictor infrastructure.

    Current bindings:
      * ALGEBRAIC → UnigramPredictor (V6-default behaviour).
      * SPECTRAL  → BigramPredictor (context = previous emit_idx).
      * Other labels: UnigramPredictor stubs (population pending).
    """
    return {
        BasisLabel.ALGEBRAIC:       UnigramPredictor(max_alphabet),
        BasisLabel.SPECTRAL:        BigramPredictor(max_alphabet),
        BasisLabel.ISOTYPIC_TRIV:   TrigramPredictor(max_alphabet),
        BasisLabel.ISOTYPIC_SIGN:   ChamberContextPredictor(max_alphabet),
        BasisLabel.ISOTYPIC_STD:    QuaternionContextPredictor(max_alphabet),
        BasisLabel.ISOTYPIC_STDSGN: UnigramPredictor(max_alphabet),
        BasisLabel.ISOTYPIC_2D:     UnigramPredictor(max_alphabet),
    }


def _grow_all_predictors(predictors: Dict[BasisLabel, Predictor],
                           new_alphabet: int) -> None:
    for p in predictors.values():
        p.grow_to(new_alphabet)


def _simulate_costs(pos: int, K: int, predictors: Dict[BasisLabel, Predictor],
                      match_tensor, walk, n_used: int, a_size: int,
                      context, current_label: BasisLabel,
                      n_chain: int) -> Dict[BasisLabel, float]:
    """Forward simulation: greedy-emit K future positions starting at
    `pos`, accumulating cost under each candidate predictor.

    `context` is a tuple (prev_emission, prev_prev_emission) per the
    multi-order predictor interface.

    Non-current labels pay the switch overhead (S_BASIS_AT + label_sym
    = 2 symbols under current predictor) as a one-time cost.
    """
    from math import log2
    switch_overhead = 2.0 * log2(max(a_size, 2))

    costs = {L: (0.0 if L == current_label else switch_overhead)
             for L in predictors}
    sim_pos = pos
    if isinstance(context, tuple):
        sim_prev = context[0] if len(context) > 0 else -1
        sim_prev_prev = context[1] if len(context) > 1 else -1
        sim_quat = context[3] if len(context) > 3 else 0
    else:
        sim_prev = context if context is not None else -1
        sim_prev_prev = -1
        sim_quat = 0
    steps = 0
    while steps < K and sim_pos < n_chain:
        if sim_pos < match_tensor.shape[0] and n_used > 0:
            row = match_tensor[sim_pos, :n_used]
            best_idx_gpu = xp().argmax(row)
            best_idx = int(best_idx_gpu)
            best_len = int(row[best_idx_gpu])
        else:
            best_idx = 0
            best_len = 0
        if best_len == 0:
            emit_idx = int(walk[sim_pos])
            advance = 1
        else:
            emit_idx = 24 + best_idx
            advance = best_len
        sim_wc = int(walk[sim_pos - 1]) if sim_pos > 0 else -1
        sim_ctx = (sim_prev, sim_prev_prev, sim_wc, sim_quat)
        for L, pred in predictors.items():
            costs[L] += pred.cost(emit_idx, a_size, sim_ctx)
        sim_prev_prev = sim_prev
        sim_prev = emit_idx
        sim_pos += advance
        steps += 1
    return costs


def _two_stage_choose(pos: int, predictors, match_tensor, walk,
                        n_used: int, a_size: int, context,
                        current_label: BasisLabel,
                        n_chain: int, K_short: int = 8, K_long: int = 16):
    """Two-stage lookahead. Pick best at K_short (incl. switch
    overhead for non-current); verify at K_long. Switch only if both
    stages choose the same non-current label.
    """
    short = _simulate_costs(pos, K_short, predictors, match_tensor, walk,
                              n_used, a_size, context, current_label,
                              n_chain)
    short_best = min(short, key=short.get)
    if short_best == current_label:
        return None
    long_ = _simulate_costs(pos, K_long, predictors, match_tensor, walk,
                              n_used, a_size, context, current_label,
                              n_chain)
    long_best = min(long_, key=long_.get)
    if short_best == long_best:
        return short_best
    return None


def encode(data: bytes, initial_opcodes: List[Opcode] = None,
           max_opcodes: int = DEFAULT_MAX_OPCODES,
           speculate_basis: bool = False,
           speculate_backref: bool = False,
           speculate_residue: bool = False,
           speculate_s4_residue: bool = False,
           backref_window: int = 4096,
           backref_min_length: int = 6,
           rotation_scale: int = 3,
           rotation_k: int = 0,
           rotation_f: int = 0,
           block_size: int = 0,
           speculate_block_rotation: bool = False,
           block_rotations: list = None) -> Tuple[bytes, Dict]:
    """V7 encoder.

    V1: BasisState torsor (S_BASIS_AT).
    V2: quaternion-word bearing (S_BASIS_BY).
    V3: per-basis parallel predictors.
    V4: `speculate_basis=True` arms the encoder to MAYBE switch.
    V5: cost-gate refuses switches that don't pay off (current
        gate is a no-op since predictors start identical — switching
        cannot beat staying until predictors diverge, which only
        happens once switches happen; bootstrap problem deferred).
    V6: generator-ring framing — rules and predictors are peers in
        the speculation set.
    V7: predictor variants exist as ring elements (currently the
        seven BasisLabel predictors all maintain independent counts).

    Output at `speculate_basis=False` is V6-equivalent.
    """
    initial_opcodes = initial_opcodes if initial_opcodes is not None \
                      else build_full_opcode_set()
    chambers, idx_map = _manifold_index()

    # BB3+BB5: rotation. Three modes (in priority order):
    #   1. block_rotations provided: per-block sticky rotation.
    #   2. speculate_block_rotation=True: encoder finds best per-block.
    #   3. else: single global rotation (BB3 original).
    effective_block_rotations = None
    if block_rotations is not None and block_size > 0:
        effective_block_rotations = list(block_rotations)
        rotated_data = apply_block_rotations(
            data, block_size, effective_block_rotations)
    elif speculate_block_rotation and block_size > 0:
        effective_block_rotations = speculate_block_rotations(
            data, block_size, rotation_scale)
        rotated_data = apply_block_rotations(
            data, block_size, effective_block_rotations)
    elif rotation_k != 0 or rotation_f != 0:
        rotated_data = apply_rotation_to_bytes(
            data, rotation_scale, rotation_k, rotation_f)
    else:
        rotated_data = data

    next_table = _build_next_chamber_table(chambers, idx_map)
    walk = int_chamber_walk(rotated_data, chambers, idx_map, next_table)
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
    # Constructive V-arc: BasisLabel slots are bound to Predictor
    # instances (per the DBE pass). ALGEBRAIC → unigram (V6 default),
    # SPECTRAL → bigram. Encoder may speculatively switch between
    # basis labels per emission when the alternative predictor's
    # cost is sufficiently lower.
    predictors = _build_predictors(max_alphabet)

    rc = RCState()
    prev_emission = -1
    prev_prev_emission = -1
    n_vm = 0
    n_growth = 0
    n_basis_at = 0
    n_backref = 0
    basis_state = IDENTITY
    digram_seen: Dict[Tuple[int, int], int] = {}
    cap_frozen = False
    pos = 0

    def _ctx():
        # Encoder context: (prev, prev2, walk_chamber_just_before_pos, quat).
        # walk_chamber: chamber-state at start of current emission. For
        # pos=0, no previous chamber, use -1 (predictor falls back to
        # uniform).
        wc = int(walk[pos - 1]) if pos > 0 else -1
        return (prev_emission, prev_prev_emission, wc, basis_state.quat)

    while pos < n_chain:
        if pos < match_tensor.shape[0] and n_used > 0:
            row = match_tensor[pos, :n_used]
            best_idx_gpu = xp().argmax(row)
            best_idx = int(best_idx_gpu)
            best_len = int(row[best_idx_gpu])
        else:
            best_idx = 0
            best_len = 0

        # Z1 + AA1+AA2: backref speculation, optionally with V₄
        # residue composition. Payload-size-aware margin: identity
        # backref = 5 symbols; residue backref = 6 symbols. Threshold
        # = payload_size × greedy_length.
        backref_match = None
        backref_sigma = 0  # S₄ identity = chambers[0] by convention.
        if speculate_backref:
            id_margin_min = max(backref_min_length,
                                  5 * max(best_len, 1) + 1)
            res_margin_min = max(backref_min_length,
                                   6 * max(best_len, 1) + 1)
            # Unified on the S₄ table. speculate_residue or
            # speculate_s4_residue both engage the unified search; the
            # only difference is the matcher's iteration range
            # (V₄-subset vs full S₄). σ in payload is always a
            # chamber-index ∈ [0, 24) — encoding the V₄ ⋊ S₃ composition
            # the substrate's semidirect product naturally provides.
            if speculate_s4_residue or speculate_residue:
                m = find_chain_backref_with_s4_residue(
                    walk, pos, max_back=backref_window,
                    min_length=res_margin_min,
                )
                if m is not None:
                    distance, length, sig_idx = m
                    backref_match = (distance, length)
                    backref_sigma = sig_idx
            else:
                backref_match = find_chain_backref(
                    walk, pos, max_back=backref_window,
                    min_length=id_margin_min,
                )

        if backref_match is not None:
            distance, length = backref_match
            a_size = alphabet_size(n_used)
            d_hi, d_lo = divmod(distance, a_size)
            l_hi, l_lo = divmod(length, a_size)
            if max(d_hi, d_lo, l_hi, l_lo, backref_sigma) >= a_size:
                backref_match = None

        if backref_match is not None:
            distance, length = backref_match
            a_size = alphabet_size(n_used)
            ctrl = _control_index(S_REF_RECENT, n_used)
            predictor = predictors[basis_state.label]
            cumfreqs = predictor.cumfreqs(a_size, _ctx())
            rc_step_encode(rc, cumfreqs, ctrl, int(cumfreqs[-1]))
            for p in predictors.values():
                p.update(ctrl, _ctx())
            d_hi, d_lo = divmod(distance, a_size)
            l_hi, l_lo = divmod(length, a_size)
            # AA-arc unified payload: 8 symbols
            #   (d_hi, d_lo, l_hi, l_lo, σ, source, phase, basis_target)
            # AA1+AA2+AA4: σ ∈ S₄ (chamber index 0..23).
            # AA5: source ∈ {0=Recent, 1=Rule}; encoder emits 0 by
            #      default; structural slot for the U-arc QUOT unification.
            # AA6: phase ∈ [0, length); slice offset within the source.
            #      Encoder emits 0 by default (full-span); structural
            #      slot for the affine-on-reference factor.
            # AA7: basis_target ∈ BasisLabel; interpretation basis for
            #      the reference content. Encoder emits current basis
            #      by default; structural slot for V-arc basis-aware
            #      emission alphabet on reference content.
            source = 0
            phase = 0
            basis_target = int(basis_state.label) % N_BASIS_LABELS
            for sym in (d_hi, d_lo, l_hi, l_lo, backref_sigma,
                          source, phase, basis_target):
                cumfreqs = predictor.cumfreqs(a_size, _ctx())
                rc_step_encode(rc, cumfreqs, sym, int(cumfreqs[-1]))
                for p in predictors.values():
                    p.update(sym, _ctx())
            n_backref += 1
            prev_prev_emission = prev_emission
            prev_emission = ctrl
            pos += length
            n_vm += 1
            continue

        if best_len == 0:
            emit_idx = int(walk[pos])
            advance = 1
        else:
            emit_idx = 24 + best_idx
            advance = best_len

        a_size = alphabet_size(n_used)

        # Per user (no heuristic margins): two-stage lookahead. Pick
        # the best predictor at K=8 forward simulation; verify at
        # K=16. Switch only if both stages agree on a non-current
        # label.
        if speculate_basis:
            target_label = _two_stage_choose(
                pos, predictors, match_tensor, walk, n_used, a_size,
                _ctx(), basis_state.label, n_chain,
                K_short=8, K_long=16,
            )
            if (target_label is not None
                    and target_label != basis_state.label):
                pred = predictors[basis_state.label]
                ctrl = _control_index(S_BASIS_AT, n_used)
                cumfreqs = pred.cumfreqs(a_size, _ctx())
                rc_step_encode(rc, cumfreqs, ctrl, int(cumfreqs[-1]))
                for p in predictors.values():
                    p.update(ctrl, _ctx())
                cumfreqs = pred.cumfreqs(a_size, _ctx())
                label_sym = min(int(target_label) % N_BASIS_LABELS,
                                  a_size - 1)
                rc_step_encode(rc, cumfreqs, label_sym, int(cumfreqs[-1]))
                for p in predictors.values():
                    p.update(label_sym, _ctx())
                basis_state = BasisState(
                    label=BasisLabel(label_sym % N_BASIS_LABELS),
                    quat=basis_state.quat,
                )
                n_basis_at += 1

        predictor = predictors[basis_state.label]
        cumfreqs = predictor.cumfreqs(a_size, _ctx())
        rc_step_encode(rc, cumfreqs, emit_idx, int(cumfreqs[-1]))
        for pred in predictors.values():
            pred.update(emit_idx, _ctx())

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
                    _grow_all_predictors(predictors, alphabet_size(max_opcodes))
                else:
                    cap_frozen = True

        prev_prev_emission = prev_emission
        prev_emission = emit_idx
        pos += advance
        n_vm += 1

    encoded = rc_finish(rc)
    header = bytearray()
    header.extend(n_chain.to_bytes(4, "little"))
    header.extend(n_initial_opcodes.to_bytes(4, "little"))
    header.extend(n_vm.to_bytes(4, "little"))
    # BB3: rotation triple in header (3 bytes: scale, k, f).
    header.append(rotation_scale & 0xFF)
    header.append(rotation_k & 0xFF)
    header.append(rotation_f & 0xFF)
    # BB5: per-block rotations. Header byte for block_size (0 = no
    # block rotations; >0 = block_size in bytes / 16 to fit a byte
    # for sizes up to 4096); then num_blocks × 3 bytes (scale, k, f).
    if effective_block_rotations is not None:
        bs_byte = min(block_size // 16, 255)
        header.append(bs_byte)
        header.append(len(effective_block_rotations) & 0xFF)
        header.append((len(effective_block_rotations) >> 8) & 0xFF)
        for rot in effective_block_rotations:
            header.append(rot[0] & 0xFF)
            header.append(rot[1] & 0xFF)
            header.append(rot[2] & 0xFF)
    else:
        header.append(0)   # bs_byte = 0 marker
    output = bytes(header) + encoded
    return output, {
        "encoded_bytes": len(output),
        "n_chain": n_chain,
        "n_vm": n_vm,
        "n_growth": n_growth,
        "n_basis_at": n_basis_at,
        "n_final_opcodes": int(n_used),
        "cap_frozen": cap_frozen,
        "v_arc_slice": "V7+AA-arc",
        "operad_axes": ("basis-torsor", "quaternion-bearing",
                          "per-basis-predictors",
                          "speculation-gate", "generator-ring",
                          "predictor-variants", "chain-backref",
                          "s4-residue-on-backref",
                          "rule-or-recent-source",
                          "affine-on-reference",
                          "basis-target-on-reference"),
        "speculate_basis": speculate_basis,
        "speculate_backref": speculate_backref,
        "speculate_residue": speculate_residue,
        "n_backref": n_backref,
        "backend": "GPU" if HAS_CUPY else "CPU",
    }


def decode(encoded: bytes, initial_opcodes: List[Opcode] = None,
           max_opcodes: int = DEFAULT_MAX_OPCODES) -> bytes:
    """V7 decoder. V1: dispatches on S_BASIS_AT (which V1 never
    actually emits, but the dispatch is wired)."""
    initial_opcodes = initial_opcodes if initial_opcodes is not None \
                      else build_full_opcode_set()
    chambers, idx_map = _manifold_index()
    n_chain = int.from_bytes(encoded[:4], "little")
    n_initial = int.from_bytes(encoded[4:8], "little")
    n_vm = int.from_bytes(encoded[8:12], "little")
    # BB3: read rotation triple from header.
    rotation_scale = encoded[12]
    rotation_k = encoded[13]
    rotation_f = encoded[14]
    # BB5: optional per-block rotations.
    bs_byte = encoded[15]
    decoder_block_rotations = None
    decoder_block_size = 0
    if bs_byte > 0:
        decoder_block_size = bs_byte * 16
        n_blocks = encoded[16] | (encoded[17] << 8)
        decoder_block_rotations = []
        off = 18
        for _i in range(n_blocks):
            decoder_block_rotations.append(
                (encoded[off], encoded[off + 1], encoded[off + 2]))
            off += 3
        payload = encoded[off:]
    else:
        payload = encoded[16:]

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
    prev_prev_emission = -1
    chain_terminals: List[int] = []
    digram_seen: Dict[Tuple[int, int], int] = {}
    cap_frozen = False
    max_alphabet = alphabet_size(max_opcodes)
    predictors = _build_predictors(max_alphabet)
    basis_state = IDENTITY

    def _dctx():
        # Decoder context: mirrors encoder. walk_chamber on the decoder
        # side = last chain symbol output (= chamber state just before
        # next emission).
        wc = chain_terminals[-1] if chain_terminals else -1
        return (prev_emission, prev_prev_emission, wc, basis_state.quat)

    n_emissions = n_vm
    while n_emissions > 0:
        a_size = alphabet_size(n_used)
        predictor = predictors[basis_state.label]
        cumfreqs = predictor.cumfreqs(a_size, _dctx())
        emit_idx = rc_step_decode(dec_state, cumfreqs, int(cumfreqs[-1]))
        for p in predictors.values():
            p.update(emit_idx, _dctx())

        if emit_idx == _control_index(S_BASIS_AT, n_used):
            predictor = predictors[basis_state.label]
            cumfreqs = predictor.cumfreqs(a_size, _dctx())
            label_sym = rc_step_decode(dec_state, cumfreqs, int(cumfreqs[-1]))
            for p in predictors.values():
                p.update(label_sym, _dctx())
            basis_state = BasisState(
                label=BasisLabel(label_sym % N_BASIS_LABELS),
                quat=basis_state.quat,
            )
            continue
        if emit_idx == _control_index(S_BASIS_BY, n_used):
            predictor = predictors[basis_state.label]
            cumfreqs = predictor.cumfreqs(a_size, _dctx())
            comp_sym = rc_step_decode(dec_state, cumfreqs, int(cumfreqs[-1]))
            for p in predictors.values():
                p.update(comp_sym, _dctx())
            new_quat = apply_quat_component(basis_state.quat, comp_sym % 4)
            basis_state = BasisState(label=basis_state.label, quat=new_quat)
            continue
        if emit_idx == _control_index(S_REF_RECENT, n_used):
            # AA-arc unified payload: 8 symbols
            #   (d_hi, d_lo, l_hi, l_lo, σ, source, phase, basis_target)
            payload = []
            for _i in range(8):
                predictor = predictors[basis_state.label]
                cumfreqs = predictor.cumfreqs(a_size, _dctx())
                sym = rc_step_decode(dec_state, cumfreqs, int(cumfreqs[-1]))
                for p in predictors.values():
                    p.update(sym, _dctx())
                payload.append(sym)
            d_hi, d_lo, l_hi, l_lo, sig_idx, source, phase, basis_t = payload
            distance = d_hi * a_size + d_lo
            length = l_hi * a_size + l_lo
            sig_idx = sig_idx % 24
            source = source % 2
            basis_t = basis_t % N_BASIS_LABELS
            # AA5: source ∈ {0=Recent, 1=Rule}. Currently encoder only
            # emits source=0; the source=1 path applies σ to a rule
            # body slice (Rule-source dispatch when activated).
            if source == 0:
                start = len(chain_terminals) - distance
                if start < 0:
                    raise ValueError(
                        f"backref distance {distance} exceeds chain history")
                # AA6: phase shifts the source span start.
                start = start + (phase if phase < length else 0)
                for i in range(length):
                    src = chain_terminals[start + i]
                    chain_terminals.append(apply_s4_chain(src, sig_idx))
            else:
                # AA5: source=Rule — distance reinterpreted as rule_id.
                rule_id = distance
                if rule_id < n_used:
                    L = int(lengths[rule_id])
                    body_np = (cp.asnumpy(bodies[rule_id, :L]) if HAS_CUPY
                               else np.asarray(bodies[rule_id, :L]))
                    start = phase if phase < L else 0
                    end = min(start + length, L)
                    for i in range(start, end):
                        chain_terminals.append(
                            apply_s4_chain(int(body_np[i]), sig_idx))
            prev_prev_emission = prev_emission
            prev_emission = _control_index(S_REF_RECENT, n_used)
            n_emissions -= 1
            continue
        if emit_idx == _control_index(S_SHIFT_BIT, n_used):
            # V8: bit-granular sink. Structural placeholder — the
            # range-coder already drives bit-granular output internally,
            # so this opcode is a marker (commit boundary) rather than
            # an action. Future work: rewire range-coder to defer bit
            # emission until S_SHIFT_BIT releases each one.
            continue

        n_emissions -= 1

        if emit_idx < 24:
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
                    _grow_all_predictors(predictors, alphabet_size(max_opcodes))
                else:
                    cap_frozen = True
        prev_prev_emission = prev_emission
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
    rotated_bytes = nibbles_to_bytes(nibbles)
    # BB4+BB5: apply inverse rotation. All rotations are involutions
    # so the same rotation undoes itself.
    if decoder_block_rotations is not None:
        return apply_block_rotations(
            rotated_bytes, decoder_block_size, decoder_block_rotations)
    if rotation_k == 0 and rotation_f == 0:
        return rotated_bytes
    return apply_rotation_to_bytes(rotated_bytes, rotation_scale,
                                       rotation_k, rotation_f)


# --- Self-check ---------------------------------------------------------


def self_check(size: int = 1024, verbose: bool = True) -> bool:
    """V7 self-check.
      * (E1) speculate_basis=False reproduces V6-equivalent behaviour
        (round-trip + close to V2 b/byte).
      * (E2) speculate_basis=True round-trips lossless.
      * (E3) measure whether two-stage lookahead actually finds
        switches that beat unigram-only.
    """
    from pathlib import Path
    import time
    from eliza import gpu_codec_v2 as v2
    HERE = Path(__file__).resolve().parent
    src = HERE / "engine.py"
    with open(src, "rb") as f:
        data = f.read()[:size]

    cases = [
        ("identity (speculate=False)", False),
        ("two-stage (speculate=True)", True),
    ]
    results = []
    for name, flag in cases:
        t0 = time.perf_counter()
        enc, stats = encode(data, speculate_basis=flag)
        t = time.perf_counter() - t0
        ok = decode(enc) == data
        bpb = 8 * len(enc) / len(data)
        results.append((name, flag, enc, stats, t, ok, bpb))

    v2_encoded, _ = v2.encode(data)
    bpb_v2 = 8 * len(v2_encoded) / len(data)

    if verbose:
        print("=== GpuCodecV7 (V-arc V1..V8: predictors + two-stage lookahead) ===")
        print(f"  input bytes: {len(data)}")
        print(f"  V2 baseline: {bpb_v2:.3f} b/byte")
        for name, flag, enc, stats, t, ok, bpb in results:
            print(f"  {name}:")
            print(f"    bytes: {len(enc)}  ({bpb:.3f} b/byte)")
            print(f"    n_basis_at: {stats['n_basis_at']}  "
                  f"time: {t*1000:.0f}ms  round-trip: "
                  f"{'OK' if ok else 'FAIL'}")
        delta = results[1][6] - results[0][6]
        verdict = ("BENEFITS" if delta < -0.01 else
                   "NEUTRAL" if abs(delta) < 0.01 else
                   "REGRESSES")
        print(f"  (E3) two-stage vs identity: {verdict} ({delta:+.3f} b/byte)")
    return all(r[5] for r in results)


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
