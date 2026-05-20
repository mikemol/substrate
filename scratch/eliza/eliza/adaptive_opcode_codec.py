"""Eliza.AdaptiveOpcodeCodec — opcode-VM codec with adaptive opcode growth.

Per the user's design: speculative-commit IS exploding-bitmap. The
codec processes the chain stream by greedily picking the longest
matching opcode at each position. As patterns repeat in the input,
NEW opcodes are added to the set (= Sequitur growing the grammar).

Adaptive growth: each time two consecutive VM emissions form a digram
that has appeared before, a new opcode is created. Both encoder and
decoder follow the same deterministic growth rule (sequitur-style),
so they stay in sync without transmitting the new opcodes.

This is the "free Markov model construction" the user pointed at:
the grammar (opcode set) grows during encoding/decoding in lockstep.
The output is JUST the opcode-reference stream; the grammar is
RECONSTRUCTIBLE from the stream by replaying the same growth rules.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from eliza.arith import RangeDecoder, RangeEncoder
from eliza.chain_symbol import ChainSymbol
from eliza.lossless_chain_codec import _CHAIN_BY_INDEX, _INDEX_BY_CHAIN
from eliza.opcode_set import Opcode, build_full_opcode_set
from eliza.per_nibble_chain import (
    nibbles_to_bytes, nibble_from_transition, per_nibble_chain_stream,
)


def _materialise_body(emission_idx: int, opcodes: List[Opcode]) -> List[ChainSymbol]:
    """Expand an emission index to its terminal-chain sequence.

    For an emission idx < 24: the terminal ChainSymbol at index idx.
    For idx >= 24: opcodes[idx - 24].body (already a tuple of terminals).
    """
    if emission_idx < 24:
        return [_CHAIN_BY_INDEX[emission_idx]]
    return list(opcodes[emission_idx - 24].body)


def _make_composite_opcode(
    name: str, prev_emission: int, this_emission: int,
    opcodes: List[Opcode],
) -> Opcode:
    """Compose two emissions into a single new opcode whose body is the
    concatenation of their materialisations."""
    body = tuple(_materialise_body(prev_emission, opcodes)
                 + _materialise_body(this_emission, opcodes))
    return Opcode(name=name, body=body, category="composite-adaptive")


def encode(
    data: bytes, initial_opcodes: List[Opcode] = None,
) -> Tuple[bytes, dict]:
    """Encode `data` via adaptive opcode-VM.

    Both encoder and decoder share the same `initial_opcodes` set.
    Adaptive opcodes grow during encoding; the decoder applies the
    same growth rule to stay in sync.
    """
    initial_opcodes = (initial_opcodes if initial_opcodes is not None
                        else build_full_opcode_set())
    opcodes: List[Opcode] = list(initial_opcodes)
    chain_stream = per_nibble_chain_stream(data)

    enc = RangeEncoder()
    SCALE = 1024
    n_initial = len(initial_opcodes)

    # Adaptive-growth digram index: (prev_emit_idx, this_emit_idx) →
    # composite opcode index (in opcodes list).
    digram_index: Dict[Tuple[int, int], int] = {}

    def best_opcode_at_pos(pos: int) -> Optional[int]:
        best_idx = None
        best_len = 0
        n = len(chain_stream)
        for i, op in enumerate(opcodes):
            L = op.length
            if L > best_len and pos + L <= n:
                if all(chain_stream[pos + j] == op.body[j] for j in range(L)):
                    best_idx = i
                    best_len = L
        return best_idx

    counts: Dict[int, int] = {}
    n_vm = 0
    n_terminal_emit = 0
    n_opcode_emit = 0
    n_growth = 0
    pos = 0
    prev_emission_idx: Optional[int] = None

    def encode_with_alphabet(emit_idx: int, alphabet_size: int) -> None:
        alpha = 0.5
        cumfreqs = [0]
        for j in range(alphabet_size):
            f = counts.get(j, 0) + alpha
            cumfreqs.append(cumfreqs[-1] + max(1, int(round(f * SCALE))))
        total = cumfreqs[-1]
        enc.encode(cumfreqs, emit_idx, total)

    while pos < len(chain_stream):
        idx = best_opcode_at_pos(pos)
        if idx is None:
            emit_idx = _INDEX_BY_CHAIN[chain_stream[pos]]
            advance = 1
            n_terminal_emit += 1
        else:
            emit_idx = 24 + idx
            advance = opcodes[idx].length
            n_opcode_emit += 1
        # Alphabet size grows as opcodes are added.
        alphabet_size = 24 + len(opcodes)
        encode_with_alphabet(emit_idx, alphabet_size)
        counts[emit_idx] = counts.get(emit_idx, 0) + 1
        n_vm += 1
        pos += advance

        # Adaptive growth: if (prev_emit_idx, emit_idx) is a known
        # digram, do nothing (next time it'll be matched as an opcode).
        # If new, register it; the NEXT time it appears, create a
        # composite opcode.
        if prev_emission_idx is not None:
            digram = (prev_emission_idx, emit_idx)
            if digram in digram_index:
                # Second occurrence: create composite opcode.
                composite_op = _make_composite_opcode(
                    f"COMP_{len(opcodes) - n_initial}",
                    prev_emission_idx, emit_idx, opcodes,
                )
                opcodes.append(composite_op)
                # Replace the digram_index entry with the composite's
                # opcode index (further occurrences of this digram will
                # match the composite opcode going forward).
                digram_index[digram] = 24 + (len(opcodes) - 1)
                n_growth += 1
            else:
                digram_index[digram] = -1  # marker: seen once
        prev_emission_idx = emit_idx

    payload = enc.finish()
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
        "n_grown_opcodes": n_growth,
        "n_vm_steps": n_vm,
        "n_terminal_emissions": n_terminal_emit,
        "n_opcode_emissions": n_opcode_emit,
        "compression_per_step": (len(chain_stream) / n_vm) if n_vm else 0.0,
    }


def decode(encoded: bytes, initial_opcodes: List[Opcode] = None) -> bytes:
    initial_opcodes = (initial_opcodes if initial_opcodes is not None
                        else build_full_opcode_set())
    n_chain = int.from_bytes(encoded[:4], "little")
    n_initial = int.from_bytes(encoded[4:8], "little")
    n_vm = int.from_bytes(encoded[8:12], "little")
    if n_initial != len(initial_opcodes):
        raise ValueError(
            f"initial opcode count mismatch: encoded {n_initial} vs "
            f"decoder {len(initial_opcodes)}"
        )

    opcodes: List[Opcode] = list(initial_opcodes)
    payload = encoded[12:]
    dec = RangeDecoder(payload)

    digram_index: Dict[Tuple[int, int], int] = {}
    SCALE = 1024
    chain_terminals: List[ChainSymbol] = []
    counts: Dict[int, int] = {}

    def decode_with_alphabet(alphabet_size: int) -> int:
        alpha = 0.5
        cumfreqs = [0]
        for j in range(alphabet_size):
            f = counts.get(j, 0) + alpha
            cumfreqs.append(cumfreqs[-1] + max(1, int(round(f * SCALE))))
        total = cumfreqs[-1]
        return dec.decode(cumfreqs, total)

    prev_emission_idx: Optional[int] = None
    for _ in range(n_vm):
        alphabet_size = 24 + len(opcodes)
        emit_idx = decode_with_alphabet(alphabet_size)
        counts[emit_idx] = counts.get(emit_idx, 0) + 1
        # Materialise.
        if emit_idx < 24:
            chain_terminals.append(_CHAIN_BY_INDEX[emit_idx])
        else:
            op = opcodes[emit_idx - 24]
            chain_terminals.extend(op.body)
        # Adaptive growth — mirror the encoder.
        if prev_emission_idx is not None:
            digram = (prev_emission_idx, emit_idx)
            if digram in digram_index:
                composite_op = _make_composite_opcode(
                    f"COMP_{len(opcodes) - n_initial}",
                    prev_emission_idx, emit_idx, opcodes,
                )
                opcodes.append(composite_op)
                digram_index[digram] = 24 + (len(opcodes) - 1)
            else:
                digram_index[digram] = -1
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
            raise ValueError(f"invalid chain transition at nibble #{len(nibbles)}")
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

    encoded, stats = encode(data)
    decoded = decode(encoded)
    ok = decoded == data

    if verbose:
        print("=== AdaptiveOpcodeCodec self-check ===")
        print(f"  input bytes:            {len(data)}")
        print(f"  per-nibble chains:      {stats['n_input_chains']}")
        print(f"  initial opcodes:        {stats['n_initial_opcodes']}")
        print(f"  final opcodes:          {stats['n_final_opcodes']}")
        print(f"  grown opcodes:          {stats['n_grown_opcodes']}")
        print(f"  VM steps:               {stats['n_vm_steps']}")
        print(f"    terminal emissions:   {stats['n_terminal_emissions']}")
        print(f"    opcode emissions:     {stats['n_opcode_emissions']}")
        print(f"  compression per step:   {stats['compression_per_step']:.3f}")
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
