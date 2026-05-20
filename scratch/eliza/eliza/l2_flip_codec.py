"""Eliza.L2FlipCodec — L2 redesigned with flip-opcode + K-step beam.

Same redesign pattern as L1-flip applied to the L2 axis (passing-to-
sequitur is an opcode):

  * Default: OBSERVE (= the L0 adaptive opcode-VM applies normally).
  * Flip: SKIP (= emit the chain symbol as raw terminal; the grammar
    machinery's view of "previous symbol" bypasses this position).
  * The SKIP flag is a special command-word in the joint alphabet,
    emitted only when speculation says SKIP beats OBSERVE.

K-step beam: simulate K full VM emissions on each branch (OBSERVE vs
SKIP at this position), pick the cheaper.

SKIP changes the grammar's view: digrams form across SKIPped symbols
rather than including them. This may produce a CLEANER grammar
downstream (per the user's "leave-alone makes the next level able to
work with more structured input").
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


def _best_opcode_at(stream, pos, opcodes):
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


def _k_step_cost_skip(
    stream, start_pos, opcodes, digram_index, prev_emission, counts_snapshot,
    k_steps, do_initial_skip,
):
    """Estimate cost for K-step lookahead with optional SKIP of first step."""
    from math import log2
    opcodes_local = list(opcodes)
    digram_local = dict(digram_index)
    counts_local = dict(counts_snapshot)
    prev_local = prev_emission
    pos = start_pos
    bits = 0.0
    steps = 0
    skip_this = do_initial_skip

    while steps < k_steps and pos < len(stream):
        if skip_this:
            # SKIP: emit raw terminal; prev_local UNCHANGED.
            emit_idx = _INDEX_BY_CHAIN[stream[pos]]
            advance = 1
            alphabet_size = 24 + len(opcodes_local) + 1
            alpha = 0.5
            total_count = sum(counts_local.values()) + alpha * alphabet_size
            p = (counts_local.get(emit_idx, 0) + alpha) / total_count
            bits += -log2(max(p, 1e-9))
            counts_local[emit_idx] = counts_local.get(emit_idx, 0) + 1
            # prev_local unchanged (this position bypassed grammar).
        else:
            # OBSERVE: regular adaptive step.
            idx = _best_opcode_at(stream, pos, opcodes_local)
            if idx is None:
                emit_idx = _INDEX_BY_CHAIN[stream[pos]]
                advance = 1
            else:
                emit_idx = 24 + idx
                advance = opcodes_local[idx].length
            alphabet_size = 24 + len(opcodes_local) + 1
            alpha = 0.5
            total_count = sum(counts_local.values()) + alpha * alphabet_size
            p = (counts_local.get(emit_idx, 0) + alpha) / total_count
            bits += -log2(max(p, 1e-9))
            counts_local[emit_idx] = counts_local.get(emit_idx, 0) + 1
            if prev_local is not None:
                digram = (prev_local, emit_idx)
                if digram in digram_local:
                    composite = _make_composite_opcode(
                        f"K_COMP_{len(opcodes_local) - len(opcodes)}",
                        prev_local, emit_idx, opcodes_local,
                    )
                    opcodes_local.append(composite)
                    digram_local[digram] = 24 + (len(opcodes_local) - 1)
                else:
                    digram_local[digram] = -1
            prev_local = emit_idx
        pos += advance
        steps += 1
        skip_this = False   # only first step has the choice
    return bits


# --- L2-flip encoder ---------------------------------------------------


def encode(data: bytes, initial_opcodes=None, k_steps: int = 4):
    initial_opcodes = (initial_opcodes if initial_opcodes is not None
                        else build_full_opcode_set())
    opcodes = list(initial_opcodes)
    chain_stream = per_nibble_chain_stream(data)
    enc = RangeEncoder()
    SCALE = 1024
    n_initial = len(initial_opcodes)
    counts: Dict[int, int] = {}
    digram_index: Dict[Tuple[int, int], int] = {}

    def encode_emission(emit_idx: int):
        alphabet_size = 24 + len(opcodes) + 1
        alpha = 0.5
        cumfreqs = [0]
        for j in range(alphabet_size):
            f = counts.get(j, 0) + alpha
            cumfreqs.append(cumfreqs[-1] + max(1, int(round(f * SCALE))))
        total = cumfreqs[-1]
        enc.encode(cumfreqs, emit_idx, total)
        counts[emit_idx] = counts.get(emit_idx, 0) + 1

    def skip_idx() -> int:
        return 24 + len(opcodes)

    pos = 0
    prev_emission: Optional[int] = None
    n_skip = 0
    n_total_steps = 0
    n_growth = 0
    n_terminal = 0
    n_opcode = 0

    from math import log2

    while pos < len(chain_stream):
        cost_observe = _k_step_cost_skip(
            chain_stream, pos, opcodes, digram_index, prev_emission,
            counts, k_steps, do_initial_skip=False,
        )
        cost_skip = _k_step_cost_skip(
            chain_stream, pos, opcodes, digram_index, prev_emission,
            counts, k_steps, do_initial_skip=True,
        )
        alphabet_size = 24 + len(opcodes) + 1
        alpha = 0.5
        total_count = sum(counts.values()) + alpha * alphabet_size
        p_skip = (counts.get(skip_idx(), 0) + alpha) / total_count
        skip_bit_cost = -log2(max(p_skip, 1e-9))
        do_skip = (cost_skip + skip_bit_cost) < cost_observe

        if do_skip:
            encode_emission(skip_idx())
            n_skip += 1
            # SKIP path: emit raw terminal; prev_emission UNCHANGED.
            emit_idx = _INDEX_BY_CHAIN[chain_stream[pos]]
            advance = 1
            encode_emission(emit_idx)
            n_total_steps += 1
            n_terminal += 1
            # prev_emission unchanged
            pos += advance
        else:
            # OBSERVE: regular adaptive step.
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
            if prev_emission is not None:
                digram = (prev_emission, emit_idx)
                if digram in digram_index:
                    composite = _make_composite_opcode(
                        f"L2F_COMP_{n_growth}",
                        prev_emission, emit_idx, opcodes,
                    )
                    opcodes.append(composite)
                    digram_index[digram] = 24 + (len(opcodes) - 1)
                    n_growth += 1
                else:
                    digram_index[digram] = -1
            prev_emission = emit_idx
            pos += advance

    payload = enc.finish()
    n_emissions = n_total_steps + n_skip
    header = bytearray()
    header.extend(len(chain_stream).to_bytes(4, "little"))
    header.extend(n_initial.to_bytes(4, "little"))
    header.extend(n_emissions.to_bytes(4, "little"))
    encoded = bytes(header) + payload
    return encoded, {
        "encoded_bytes": len(encoded),
        "n_input_chains": len(chain_stream),
        "n_total_emissions": n_emissions,
        "n_vm_steps": n_total_steps,
        "n_skip_emissions": n_skip,
        "n_terminal_emissions": n_terminal,
        "n_opcode_emissions": n_opcode,
        "n_growth": n_growth,
        "n_final_opcodes": len(opcodes),
        "k_steps": k_steps,
    }


# --- L2-flip decoder ---------------------------------------------------


def decode(encoded: bytes, initial_opcodes=None) -> bytes:
    initial_opcodes = (initial_opcodes if initial_opcodes is not None
                        else build_full_opcode_set())
    n_chain = int.from_bytes(encoded[:4], "little")
    n_initial = int.from_bytes(encoded[4:8], "little")
    n_emissions = int.from_bytes(encoded[8:12], "little")
    opcodes = list(initial_opcodes)
    payload = encoded[12:]
    dec = RangeDecoder(payload)

    SCALE = 1024
    counts: Dict[int, int] = {}
    digram_index: Dict[Tuple[int, int], int] = {}
    chain_terminals: List[ChainSymbol] = []
    prev_emission: Optional[int] = None
    pending_skip = False
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
        skip_index = 24 + len(opcodes)
        if emit_idx == skip_index:
            pending_skip = True
            continue
        # Regular emission.
        if emit_idx < 24:
            chain_terminals.append(_CHAIN_BY_INDEX[emit_idx])
        else:
            op = opcodes[emit_idx - 24]
            chain_terminals.extend(op.body)
        if pending_skip:
            pending_skip = False
            # SKIP: prev_emission unchanged.
        else:
            if prev_emission is not None:
                digram = (prev_emission, emit_idx)
                if digram in digram_index:
                    composite = _make_composite_opcode(
                        f"L2F_COMP_{n_growth}",
                        prev_emission, emit_idx, opcodes,
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


def self_check(size: int = 1024, k_steps: int = 4, verbose: bool = True) -> bool:
    from pathlib import Path
    HERE = Path(__file__).resolve().parent
    src = HERE / "engine.py"
    with open(src, "rb") as f:
        data = f.read()[:size]

    encoded, stats = encode(data, k_steps=k_steps)
    decoded = decode(encoded)
    ok = decoded == data

    if verbose:
        print("=== L2FlipCodec self-check ===")
        print(f"  input bytes:        {len(data)}")
        print(f"  per-nibble chains:  {stats['n_input_chains']}")
        print(f"  k_steps lookahead:  {stats['k_steps']}")
        print(f"  VM steps:           {stats['n_vm_steps']}")
        print(f"  skip emissions:     {stats['n_skip_emissions']} "
              f"(rate {100*stats['n_skip_emissions']/max(stats['n_vm_steps'],1):.1f}%)")
        print(f"  growth events:      {stats['n_growth']}")
        print(f"  final opcodes:      {stats['n_final_opcodes']}")
        print(f"  encoded:            {len(encoded)} bytes "
              f"({8 * len(encoded) / len(data):.3f} b/byte)")
        print(f"  round-trip:         {'OK' if ok else 'FAIL'}")
        if not ok:
            diffs = sum(1 for i in range(min(len(data), len(decoded)))
                        if data[i] != decoded[i])
            print(f"    bytes differ:     {diffs}")
            print(f"    decoded length:   {len(decoded)}")
        print(f"\nResult: {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
