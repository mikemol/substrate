"""Eliza.L1RewriteCodec — Level-1 codec: rewrite is an opcode.

Per the user's tetrative axis directive:
  "We can make sequitur's rewrite step not sequitur-internal, but an opcode."

L0 (existing AdaptiveOpcodeCodec): each emission picks the longest-
matching opcode at the current position. Rewriting (= creating new
composite opcodes from repeated digrams) happens AUTOMATICALLY behind
the scenes.

L1 (this codec): the rewrite decision is EXPLICIT. Each emission
carries a 1-bit flag:
  * REWRITE = compose (prev_emission, this_emission) into a new opcode
              that is added to the opcode set for subsequent matching
  * NO_REWRITE = emit normally, no opcode added

The encoder speculatively tries both flag values, looking ahead K
positions to estimate cost; commits the cheaper. Decoder replays the
flags to keep the opcode set in lockstep with the encoder.

This exposes the grammar's growth step as a per-emission speculation
target — the codec now CHOOSES when to grow the grammar, rather than
growing automatically on every repeated digram.
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


# --- L1 cost estimator (lookahead-based) -------------------------------


def _estimate_path_cost(
    chain_stream: List[ChainSymbol],
    start_pos: int,
    initial_opcodes: List[Opcode],
    horizon: int,
) -> Tuple[float, int]:
    """Greedy lookahead: from `start_pos`, run the L0 encoder with the
    given `initial_opcodes` for up to `horizon` chain symbols.
    Returns (estimated_bits, chains_consumed).

    Estimated bits uses uniform-per-emission cost log₂(24 + |opcodes|).
    Not adaptive; intended for COMPARISON between paths only — the
    relative cost (path A vs B) is what matters, not the absolute.
    """
    from math import log2
    opcodes = list(initial_opcodes)
    pos = start_pos
    bits = 0.0
    end = min(start_pos + horizon, len(chain_stream))
    n_emissions = 0
    while pos < end:
        # Find longest opcode match.
        best_len = 0
        for op in opcodes:
            L = op.length
            if L > best_len and pos + L <= len(chain_stream):
                if all(chain_stream[pos + j] == op.body[j] for j in range(L)):
                    best_len = L
        if best_len == 0:
            best_len = 1
        bits += log2(24 + len(opcodes))
        n_emissions += 1
        pos += best_len
    return bits, pos - start_pos


# --- L1 encoder --------------------------------------------------------


def encode(
    data: bytes, initial_opcodes: List[Opcode] = None,
    lookahead: int = 8,
) -> Tuple[bytes, dict]:
    """Encode `data` via L0 opcode-VM + L1 explicit rewrite decision.

    `lookahead` is the number of subsequent chain symbols to consider
    when deciding REWRITE vs NO_REWRITE. Larger = more accurate but
    slower.
    """
    initial_opcodes = (initial_opcodes if initial_opcodes is not None
                        else build_full_opcode_set())
    opcodes: List[Opcode] = list(initial_opcodes)
    chain_stream = per_nibble_chain_stream(data)

    enc = RangeEncoder()
    SCALE = 1024
    n_initial = len(initial_opcodes)

    def best_opcode_at_pos(pos: int, ops: List[Opcode]) -> Optional[int]:
        best_idx = None
        best_len = 0
        n = len(chain_stream)
        for i, op in enumerate(ops):
            L = op.length
            if L > best_len and pos + L <= n:
                if all(chain_stream[pos + j] == op.body[j] for j in range(L)):
                    best_idx = i
                    best_len = L
        return best_idx

    counts: Dict[int, int] = {}
    rewrite_counts = [0, 0]   # [no_rewrite, rewrite]
    pos = 0
    prev_emission_idx: Optional[int] = None
    n_terminal = 0
    n_opcode = 0
    n_rewrites_committed = 0
    n_rewrites_skipped = 0

    def encode_emission(emit_idx: int, alphabet_size: int):
        alpha = 0.5
        cumfreqs = [0]
        for j in range(alphabet_size):
            f = counts.get(j, 0) + alpha
            cumfreqs.append(cumfreqs[-1] + max(1, int(round(f * SCALE))))
        total = cumfreqs[-1]
        enc.encode(cumfreqs, emit_idx, total)

    def encode_rewrite_flag(flag: int):
        alpha = 0.5
        c0 = rewrite_counts[0] + alpha
        c1 = rewrite_counts[1] + alpha
        f0 = max(1, int(round(c0 * SCALE)))
        f1 = max(1, int(round(c1 * SCALE)))
        cumfreqs = [0, f0, f0 + f1]
        enc.encode(cumfreqs, flag, cumfreqs[-1])

    while pos < len(chain_stream):
        idx = best_opcode_at_pos(pos, opcodes)
        if idx is None:
            emit_idx = _INDEX_BY_CHAIN[chain_stream[pos]]
            advance = 1
            n_terminal += 1
        else:
            emit_idx = 24 + idx
            advance = opcodes[idx].length
            n_opcode += 1

        # Encode emission.
        alphabet_size = 24 + len(opcodes)
        encode_emission(emit_idx, alphabet_size)
        counts[emit_idx] = counts.get(emit_idx, 0) + 1

        # L1 speculative-commit: should we ALSO rewrite (prev, this)
        # into a new composite opcode?
        flag = 0   # default: NO_REWRITE
        if prev_emission_idx is not None:
            new_pos = pos + advance
            # Path A: don't rewrite. Opcode set unchanged.
            cost_no_rewrite, _ = _estimate_path_cost(
                chain_stream, new_pos, opcodes, lookahead,
            )
            # Path B: rewrite. Composite opcode added.
            composite = _make_composite_opcode(
                f"L1_COMP_{n_rewrites_committed}",
                prev_emission_idx, emit_idx, opcodes,
            )
            opcodes_with = opcodes + [composite]
            cost_with_rewrite, _ = _estimate_path_cost(
                chain_stream, new_pos, opcodes_with, lookahead,
            )
            # Add the rewrite-flag bit cost.
            from math import log2
            total_rw = sum(rewrite_counts) + 1.0
            p_rewrite = (rewrite_counts[1] + 0.5) / total_rw
            flag_bit_rewrite = -log2(max(p_rewrite, 1e-9))
            flag_bit_no = -log2(max(1.0 - p_rewrite, 1e-9))
            if cost_with_rewrite + flag_bit_rewrite < cost_no_rewrite + flag_bit_no:
                flag = 1
                opcodes.append(composite)
                n_rewrites_committed += 1
            else:
                n_rewrites_skipped += 1
        encode_rewrite_flag(flag)
        rewrite_counts[flag] += 1
        prev_emission_idx = emit_idx
        pos += advance

    payload = enc.finish()
    n_vm = n_terminal + n_opcode
    header = bytearray()
    header.extend(len(chain_stream).to_bytes(4, "little"))
    header.extend(n_initial.to_bytes(4, "little"))
    header.extend(n_vm.to_bytes(4, "little"))
    encoded = bytes(header) + payload
    return encoded, {
        "encoded_bytes": len(encoded),
        "header_bytes": len(header),
        "payload_bytes": len(payload),
        "n_input_chains": len(chain_stream),
        "n_initial_opcodes": n_initial,
        "n_final_opcodes": len(opcodes),
        "n_rewrites_committed": n_rewrites_committed,
        "n_rewrites_skipped": n_rewrites_skipped,
        "n_vm_steps": n_vm,
        "n_terminal_emissions": n_terminal,
        "n_opcode_emissions": n_opcode,
        "lookahead": lookahead,
    }


# --- L1 decoder --------------------------------------------------------


def decode(encoded: bytes, initial_opcodes: List[Opcode] = None) -> bytes:
    initial_opcodes = (initial_opcodes if initial_opcodes is not None
                        else build_full_opcode_set())
    n_chain = int.from_bytes(encoded[:4], "little")
    n_initial = int.from_bytes(encoded[4:8], "little")
    n_vm = int.from_bytes(encoded[8:12], "little")
    if n_initial != len(initial_opcodes):
        raise ValueError(
            f"initial opcode count mismatch: {n_initial} vs {len(initial_opcodes)}"
        )
    opcodes: List[Opcode] = list(initial_opcodes)
    payload = encoded[12:]
    dec = RangeDecoder(payload)

    SCALE = 1024
    counts: Dict[int, int] = {}
    rewrite_counts = [0, 0]
    chain_terminals: List[ChainSymbol] = []
    prev_emission_idx: Optional[int] = None

    def decode_emission(alphabet_size: int) -> int:
        alpha = 0.5
        cumfreqs = [0]
        for j in range(alphabet_size):
            f = counts.get(j, 0) + alpha
            cumfreqs.append(cumfreqs[-1] + max(1, int(round(f * SCALE))))
        total = cumfreqs[-1]
        return dec.decode(cumfreqs, total)

    def decode_rewrite_flag() -> int:
        alpha = 0.5
        c0 = rewrite_counts[0] + alpha
        c1 = rewrite_counts[1] + alpha
        f0 = max(1, int(round(c0 * SCALE)))
        f1 = max(1, int(round(c1 * SCALE)))
        cumfreqs = [0, f0, f0 + f1]
        return dec.decode(cumfreqs, cumfreqs[-1])

    for _ in range(n_vm):
        alphabet_size = 24 + len(opcodes)
        emit_idx = decode_emission(alphabet_size)
        counts[emit_idx] = counts.get(emit_idx, 0) + 1
        if emit_idx < 24:
            chain_terminals.append(_CHAIN_BY_INDEX[emit_idx])
        else:
            op = opcodes[emit_idx - 24]
            chain_terminals.extend(op.body)
        flag = decode_rewrite_flag()
        rewrite_counts[flag] += 1
        if flag == 1 and prev_emission_idx is not None:
            composite = _make_composite_opcode(
                f"L1_COMP_{len(opcodes) - n_initial}",
                prev_emission_idx, emit_idx, opcodes,
            )
            opcodes.append(composite)
        prev_emission_idx = emit_idx

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


def self_check(size: int = 2048, verbose: bool = True) -> bool:
    from pathlib import Path
    HERE = Path(__file__).resolve().parent
    src = HERE / "engine.py"
    with open(src, "rb") as f:
        data = f.read()[:size]

    encoded, stats = encode(data, lookahead=4)
    decoded = decode(encoded)
    ok = decoded == data

    if verbose:
        print("=== L1RewriteCodec self-check ===")
        print(f"  input bytes:            {len(data)}")
        print(f"  per-nibble chains:      {stats['n_input_chains']}")
        print(f"  initial opcodes:        {stats['n_initial_opcodes']}")
        print(f"  final opcodes:          {stats['n_final_opcodes']}")
        print(f"  rewrites committed:     {stats['n_rewrites_committed']}")
        print(f"  rewrites skipped:       {stats['n_rewrites_skipped']}  "
              f"(L1 said no)")
        print(f"  VM steps:               {stats['n_vm_steps']}")
        print(f"  encoded:                {len(encoded)} bytes "
              f"({8 * len(encoded) / len(data):.3f} b/byte)")
        print(f"  round-trip:             {'OK' if ok else 'FAIL'}")
        if not ok:
            diffs = sum(1 for i in range(min(len(data), len(decoded)))
                        if data[i] != decoded[i])
            print(f"    bytes differ:         {diffs}")
        print(f"\nResult: {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
