"""Eliza.L1FlipCodec — L1 redesigned with flip-opcode + K-step beam.

Per the user's correction:
  "Being a flag, though, I'd wager that what you want is actually an
   opcode for 'flip this flag'. And then speculating fully a few
   opcodes out."

Two changes from the previous L1 design:

  1. FLIP is NOT a per-emission flag. It's a SPECIAL command-word
     slot in the joint alphabet that only appears when the encoder
     decides to deviate from the L0 default (= automatic rewrite). The
     flip-opcode appears BEFORE the regular emission whose default
     should be flipped. Cost per default emission: ZERO bits (no flag
     overhead). Cost per flip: one opcode-emission, amortised by
     adaptive arithmetic coding to ~log₂(joint_alphabet) bits when
     flips are rare.

  2. K-step lookahead: cost-estimator simulates K complete VM
     emissions on each candidate path (FLIP vs NO-FLIP), counts total
     bits, picks the cheaper. Captures the user's "downstream structure
     matters" — a leave-alone here may give cleaner input downstream.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from eliza.arith import RangeDecoder, RangeEncoder
from eliza.chain_symbol import ChainSymbol
from eliza.lossless_chain_codec import _CHAIN_BY_INDEX, _INDEX_BY_CHAIN
from eliza.opcode_set import Opcode, build_full_opcode_set
from eliza.adaptive_opcode_codec import _make_composite_opcode
from eliza.per_nibble_chain import (
    nibbles_to_bytes, nibble_from_transition, per_nibble_chain_stream,
)


# The joint alphabet layout for L1-flip:
#   [0..23]         — 24 chain terminals
#   [24..24+N-1]    — N opcodes (initial + grown)
#   [24+N]          — FLIP command (single slot, fixed index relative
#                      to alphabet end; the alphabet grows as opcodes
#                      grow, but FLIP is always the LAST index)
#
# At any moment: alphabet_size = 24 + n_opcodes + 1


def _best_opcode_at(stream: List[ChainSymbol], pos: int,
                     opcodes: List[Opcode]) -> Optional[int]:
    best_idx = None
    best_len = 0
    n = len(stream)
    for i, op in enumerate(opcodes):
        L = op.length
        if L > best_len and pos + L <= n:
            if all(stream[pos + j] == op.body[j] for j in range(L)):
                best_idx = i
                best_len = L
    return best_idx


def _k_step_cost(
    stream: List[ChainSymbol], start_pos: int,
    opcodes: List[Opcode], digram_index: Dict[Tuple[int, int], int],
    prev_emission: Optional[int], counts_snapshot: Dict[int, int],
    k_steps: int, do_initial_flip: bool,
) -> float:
    """Estimate total bits for the next k_steps VM emissions starting
    at `start_pos`, with the option to flip the first emission's
    rewrite decision.

    Uses the ACTUAL adaptive codec logic (longest-match opcode + auto-
    rewrite digrams), so the cost estimate matches what the encoder
    would actually produce. Snapshot counters not mutated.
    """
    from math import log2
    # Local copies so we don't mutate the encoder state.
    opcodes_local = list(opcodes)
    digram_local = dict(digram_index)
    counts_local = dict(counts_snapshot)
    prev_local = prev_emission
    pos = start_pos
    bits = 0.0
    steps = 0
    auto_rewrite = not do_initial_flip   # the first step flips the default

    while steps < k_steps and pos < len(stream):
        idx = _best_opcode_at(stream, pos, opcodes_local)
        if idx is None:
            emit_idx = _INDEX_BY_CHAIN[stream[pos]]
            advance = 1
        else:
            emit_idx = 24 + idx
            advance = opcodes_local[idx].length
        # Cost: -log2(p) where p ≈ adaptive arithmetic-coding prob.
        alphabet_size = 24 + len(opcodes_local) + 1   # +1 FLIP slot
        alpha = 0.5
        total_count = sum(counts_local.values()) + alpha * alphabet_size
        p = (counts_local.get(emit_idx, 0) + alpha) / total_count
        bits += -log2(max(p, 1e-9))
        counts_local[emit_idx] = counts_local.get(emit_idx, 0) + 1
        # Apply (possibly-flipped) auto-rewrite.
        if prev_local is not None:
            digram = (prev_local, emit_idx)
            if auto_rewrite:
                if digram in digram_local:
                    composite = _make_composite_opcode(
                        f"K_COMP_{len(opcodes_local) - len(opcodes)}",
                        prev_local, emit_idx, opcodes_local,
                    )
                    opcodes_local.append(composite)
                    digram_local[digram] = 24 + (len(opcodes_local) - 1)
                else:
                    digram_local[digram] = -1
            # If not auto-rewrite, we still register the digram for
            # future detection but skip composite creation this step.
            else:
                if digram not in digram_local:
                    digram_local[digram] = -1
        prev_local = emit_idx
        pos += advance
        steps += 1
        # After the first step, default behaviour resumes.
        auto_rewrite = True
    return bits


# --- L1-flip encoder ---------------------------------------------------


def encode(
    data: bytes, initial_opcodes: List[Opcode] = None,
    k_steps: int = 4,
) -> Tuple[bytes, dict]:
    """Encode `data` via L0 opcode-VM + L1 sparse flip-opcode."""
    initial_opcodes = (initial_opcodes if initial_opcodes is not None
                        else build_full_opcode_set())
    opcodes: List[Opcode] = list(initial_opcodes)
    chain_stream = per_nibble_chain_stream(data)

    enc = RangeEncoder()
    SCALE = 1024
    n_initial = len(initial_opcodes)
    counts: Dict[int, int] = {}
    digram_index: Dict[Tuple[int, int], int] = {}

    def encode_emission(emit_idx: int):
        alphabet_size = 24 + len(opcodes) + 1   # FLIP slot
        alpha = 0.5
        cumfreqs = [0]
        for j in range(alphabet_size):
            f = counts.get(j, 0) + alpha
            cumfreqs.append(cumfreqs[-1] + max(1, int(round(f * SCALE))))
        total = cumfreqs[-1]
        enc.encode(cumfreqs, emit_idx, total)
        counts[emit_idx] = counts.get(emit_idx, 0) + 1

    def flip_idx() -> int:
        # The FLIP slot is always the last index in the joint alphabet.
        return 24 + len(opcodes)

    pos = 0
    prev_emission: Optional[int] = None
    n_flip = 0
    n_total_steps = 0
    n_terminal = 0
    n_opcode = 0
    n_growth = 0

    while pos < len(chain_stream):
        # K-step beam: try (no-flip) vs (flip-the-default-for-this-step).
        cost_no_flip = _k_step_cost(
            chain_stream, pos, opcodes, digram_index,
            prev_emission, counts, k_steps, do_initial_flip=False,
        )
        cost_flip = _k_step_cost(
            chain_stream, pos, opcodes, digram_index,
            prev_emission, counts, k_steps, do_initial_flip=True,
        )
        # The flip path also pays the flip-opcode emission cost.
        from math import log2
        alphabet_size = 24 + len(opcodes) + 1
        alpha = 0.5
        total_count = sum(counts.values()) + alpha * alphabet_size
        p_flip = (counts.get(flip_idx(), 0) + alpha) / total_count
        flip_bit_cost = -log2(max(p_flip, 1e-9))
        do_flip = (cost_flip + flip_bit_cost) < cost_no_flip

        if do_flip:
            encode_emission(flip_idx())
            n_flip += 1

        # Emit the regular VM step (with auto_rewrite flipped iff do_flip).
        idx = _best_opcode_at(chain_stream, pos, opcodes)
        if idx is None:
            emit_idx = _INDEX_BY_CHAIN[chain_stream[pos]]
            advance = 1
            n_terminal += 1
        else:
            emit_idx = 24 + idx
            advance = opcodes[idx].length
            n_opcode += 1
        encode_emission(emit_idx)
        n_total_steps += 1

        # Apply auto-rewrite (flipped iff do_flip).
        if prev_emission is not None:
            digram = (prev_emission, emit_idx)
            if do_flip:
                # leave-alone: do not grow opcode set this step
                if digram not in digram_index:
                    digram_index[digram] = -1
            else:
                if digram in digram_index:
                    composite = _make_composite_opcode(
                        f"L1F_COMP_{n_growth}", prev_emission, emit_idx, opcodes,
                    )
                    opcodes.append(composite)
                    digram_index[digram] = 24 + (len(opcodes) - 1)
                    n_growth += 1
                else:
                    digram_index[digram] = -1
        prev_emission = emit_idx
        pos += advance

    payload = enc.finish()
    header = bytearray()
    header.extend(len(chain_stream).to_bytes(4, "little"))
    header.extend(n_initial.to_bytes(4, "little"))
    # n_emissions includes flip-opcode emissions.
    n_emissions = n_total_steps + n_flip
    header.extend(n_emissions.to_bytes(4, "little"))
    encoded = bytes(header) + payload
    return encoded, {
        "encoded_bytes": len(encoded),
        "header_bytes": len(header),
        "payload_bytes": len(payload),
        "n_input_chains": len(chain_stream),
        "n_initial_opcodes": n_initial,
        "n_final_opcodes": len(opcodes),
        "n_total_emissions": n_emissions,
        "n_vm_steps": n_total_steps,
        "n_flip_emissions": n_flip,
        "n_growth": n_growth,
        "n_terminal_emissions": n_terminal,
        "n_opcode_emissions": n_opcode,
        "flip_rate": n_flip / max(n_total_steps, 1),
        "k_steps": k_steps,
    }


# --- L1-flip decoder ---------------------------------------------------


def decode(encoded: bytes, initial_opcodes: List[Opcode] = None) -> bytes:
    initial_opcodes = (initial_opcodes if initial_opcodes is not None
                        else build_full_opcode_set())
    n_chain = int.from_bytes(encoded[:4], "little")
    n_initial = int.from_bytes(encoded[4:8], "little")
    n_emissions = int.from_bytes(encoded[8:12], "little")
    opcodes: List[Opcode] = list(initial_opcodes)
    payload = encoded[12:]
    dec = RangeDecoder(payload)

    SCALE = 1024
    counts: Dict[int, int] = {}
    digram_index: Dict[Tuple[int, int], int] = {}
    chain_terminals: List[ChainSymbol] = []
    prev_emission: Optional[int] = None
    pending_flip = False
    n_growth = 0

    def decode_emission() -> int:
        alphabet_size = 24 + len(opcodes) + 1
        alpha = 0.5
        cumfreqs = [0]
        for j in range(alphabet_size):
            f = counts.get(j, 0) + alpha
            cumfreqs.append(cumfreqs[-1] + max(1, int(round(f * SCALE))))
        total = cumfreqs[-1]
        return dec.decode(cumfreqs, total)

    for _ in range(n_emissions):
        emit_idx = decode_emission()
        counts[emit_idx] = counts.get(emit_idx, 0) + 1
        flip_index = 24 + len(opcodes)
        # Note: the FLIP slot index DEPENDS on the current opcode count.
        # We must check BEFORE any growth happens. The encoder mirrors.
        if emit_idx == flip_index:
            pending_flip = True
            continue
        # Regular emission.
        if emit_idx < 24:
            chain_terminals.append(_CHAIN_BY_INDEX[emit_idx])
        else:
            op = opcodes[emit_idx - 24]
            chain_terminals.extend(op.body)
        do_flip = pending_flip
        pending_flip = False
        # Mirror auto-rewrite (flipped iff do_flip).
        if prev_emission is not None:
            digram = (prev_emission, emit_idx)
            if do_flip:
                if digram not in digram_index:
                    digram_index[digram] = -1
            else:
                if digram in digram_index:
                    composite = _make_composite_opcode(
                        f"L1F_COMP_{n_growth}", prev_emission, emit_idx, opcodes,
                    )
                    opcodes.append(composite)
                    digram_index[digram] = 24 + (len(opcodes) - 1)
                    n_growth += 1
                else:
                    digram_index[digram] = -1
        prev_emission = emit_idx

    if len(chain_terminals) != n_chain:
        raise ValueError(
            f"terminal count mismatch: got {len(chain_terminals)}, "
            f"expected {n_chain}"
        )

    from eliza.alphabets import ORIGIN
    nibbles: List[int] = []
    state = ORIGIN
    for ch in chain_terminals:
        after = ch.to_s4()
        n = nibble_from_transition(state, after)
        if n is None:
            raise ValueError(f"invalid chain transition at #{len(nibbles)}")
        nibbles.append(n)
        state = after
    return nibbles_to_bytes(nibbles)


# --- Self-check ---------------------------------------------------------


def self_check(size: int = 1024, k_steps: int = 4,
               verbose: bool = True) -> bool:
    from pathlib import Path
    HERE = Path(__file__).resolve().parent
    src = HERE / "engine.py"
    with open(src, "rb") as f:
        data = f.read()[:size]

    encoded, stats = encode(data, k_steps=k_steps)
    decoded = decode(encoded)
    ok = decoded == data

    if verbose:
        print("=== L1FlipCodec self-check ===")
        print(f"  input bytes:            {len(data)}")
        print(f"  per-nibble chains:      {stats['n_input_chains']}")
        print(f"  k_steps lookahead:      {stats['k_steps']}")
        print(f"  VM steps:               {stats['n_vm_steps']}")
        print(f"  flip emissions:         {stats['n_flip_emissions']} "
              f"(rate {100*stats['flip_rate']:.1f}%)")
        print(f"  growth events:          {stats['n_growth']}")
        print(f"  final opcodes:          {stats['n_final_opcodes']}")
        print(f"  encoded:                {len(encoded)} bytes "
              f"({8 * len(encoded) / len(data):.3f} b/byte)")
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
