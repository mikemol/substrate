"""Eliza.OpcodeVMCodec — speculative-commit / exploding-bitmap codec.

The user's design synthesised:
  * Each grammar rule IS an opcode.
  * The grammar is pre-populated with opcodes for input transformation.
  * For each position in the chain stream, SPECULATIVELY try each opcode;
    commit the one that performs best (= longest match).
  * Speculative-commit IS exploding-bitmap: a committed opcode reference
    UNFOLDS on decode to many chain symbols (the opcode's body).

This is a VM model: the encoded stream is a sequence of opcode
references; the decoder runs them sequentially, each reference
"executing" by expanding its body, which in turn unfolds into chain
symbols → nibbles → bytes.

The opcode set's coverage is the codec's vocabulary. Pre-populating
with substrate-native opcodes (V₄/Sylow-3 patterns) seeds the encoder
to recognise the substrate's W-axis structure from the start.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from eliza.arith import RangeDecoder, RangeEncoder
from eliza.chain_symbol import ChainSymbol
from eliza.lossless_chain_codec import _CHAIN_BY_INDEX, _INDEX_BY_CHAIN
from eliza.opcode_set import Opcode, build_full_opcode_set
from eliza.per_nibble_chain import (
    nibbles_to_bytes, nibble_from_transition, per_nibble_chain_stream,
)


# --- The speculative match ---------------------------------------------


def best_opcode_at(
    opcodes: List[Opcode], stream: List[ChainSymbol], pos: int,
) -> Optional[int]:
    """Return the index of the longest opcode whose body matches the
    stream at `pos`, or None if no opcode matches.

    "Longest match" = exploding-bitmap of maximum size, = the
    most-bits-saved per emitted opcode reference.
    """
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


# --- The "compiled" opcode-reference stream ---------------------------


@dataclass(frozen=True)
class OpcodeRef:
    """One emitted unit in the VM stream. Either:
      * .opcode_idx is set (and .terminal is None) — a reference to
        opcode[opcode_idx], unfolding to its body on decode
      * .terminal is set (and .opcode_idx is None) — a literal
        ChainSymbol where no opcode matched.
    """
    opcode_idx: Optional[int] = None
    terminal: Optional[ChainSymbol] = None


def compile_stream(
    chain_stream: List[ChainSymbol], opcodes: List[Opcode],
) -> List[OpcodeRef]:
    """Greedy speculative-commit: at each position, take the longest
    matching opcode; advance by the matched length. If no opcode
    matches at all, emit a literal chain symbol.

    Returns the compiled VM stream as a list of OpcodeRef.
    """
    out: List[OpcodeRef] = []
    pos = 0
    while pos < len(chain_stream):
        idx = best_opcode_at(opcodes, chain_stream, pos)
        if idx is None:
            out.append(OpcodeRef(terminal=chain_stream[pos]))
            pos += 1
        else:
            out.append(OpcodeRef(opcode_idx=idx))
            pos += opcodes[idx].length
    return out


# --- Encoder ----------------------------------------------------------


def encode(
    data: bytes, opcodes: List[Opcode] = None,
) -> Tuple[bytes, dict]:
    """Encode `data` as a stream of opcode references.

    Joint alphabet: 24 terminal chain symbols + len(opcodes) opcode refs.
    Total = 24 + |opcodes| symbols per VM step.
    """
    opcodes = opcodes if opcodes is not None else build_full_opcode_set()
    chain_stream = per_nibble_chain_stream(data)
    vm_stream = compile_stream(chain_stream, opcodes)

    n_opcodes = len(opcodes)
    JOINT_N = 24 + n_opcodes

    enc = RangeEncoder()
    SCALE = 1024

    def encode_sym_adaptive(idx: int, counts: Dict[int, int]) -> None:
        alpha = 0.5
        cumfreqs = [0]
        for j in range(JOINT_N):
            f = counts.get(j, 0) + alpha
            cumfreqs.append(cumfreqs[-1] + max(1, int(round(f * SCALE))))
        total = cumfreqs[-1]
        enc.encode(cumfreqs, idx, total)

    counts: Dict[int, int] = {}
    for ref in vm_stream:
        if ref.terminal is not None:
            idx = _INDEX_BY_CHAIN[ref.terminal]
        else:
            idx = 24 + ref.opcode_idx
        encode_sym_adaptive(idx, counts)
        counts[idx] = counts.get(idx, 0) + 1

    payload = enc.finish()

    # Header: input chain stream length (so decoder knows when to stop)
    # + n_opcodes (so decoder builds the same joint alphabet).
    header = bytearray()
    header.extend(len(chain_stream).to_bytes(4, "little"))
    header.extend(n_opcodes.to_bytes(4, "little"))
    header.extend(len(vm_stream).to_bytes(4, "little"))

    encoded = bytes(header) + payload
    return encoded, {
        "encoded_bytes": len(encoded),
        "header_bytes": len(header),
        "payload_bytes": len(payload),
        "n_input_chains": len(chain_stream),
        "n_opcodes": n_opcodes,
        "n_vm_steps": len(vm_stream),
        "compression_per_step": len(chain_stream) / len(vm_stream) if vm_stream else 0.0,
        "n_terminal_emissions": sum(1 for r in vm_stream if r.terminal is not None),
        "n_opcode_emissions": sum(1 for r in vm_stream if r.opcode_idx is not None),
    }


# --- Decoder ----------------------------------------------------------


def decode(encoded: bytes, opcodes: List[Opcode] = None) -> bytes:
    opcodes = opcodes if opcodes is not None else build_full_opcode_set()
    n_chain = int.from_bytes(encoded[:4], "little")
    n_opcodes = int.from_bytes(encoded[4:8], "little")
    n_vm = int.from_bytes(encoded[8:12], "little")
    payload = encoded[12:]
    dec = RangeDecoder(payload)

    if n_opcodes != len(opcodes):
        raise ValueError(
            f"opcode set size mismatch: encoded with {n_opcodes}, "
            f"decoder has {len(opcodes)}"
        )

    JOINT_N = 24 + n_opcodes
    SCALE = 1024

    def decode_sym_adaptive(counts: Dict[int, int]) -> int:
        alpha = 0.5
        cumfreqs = [0]
        for j in range(JOINT_N):
            f = counts.get(j, 0) + alpha
            cumfreqs.append(cumfreqs[-1] + max(1, int(round(f * SCALE))))
        total = cumfreqs[-1]
        return dec.decode(cumfreqs, total)

    counts: Dict[int, int] = {}
    chain_terminals: List[ChainSymbol] = []
    for _ in range(n_vm):
        idx = decode_sym_adaptive(counts)
        counts[idx] = counts.get(idx, 0) + 1
        if idx < 24:
            chain_terminals.append(_CHAIN_BY_INDEX[idx])
        else:
            op = opcodes[idx - 24]
            chain_terminals.extend(op.body)

    # Sanity: total terminal count == n_chain.
    if len(chain_terminals) != n_chain:
        raise ValueError(
            f"chain terminal count mismatch: got {len(chain_terminals)}, "
            f"expected {n_chain}"
        )

    # Invert per-nibble.
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

    encoded, stats = encode(data)
    decoded = decode(encoded)
    ok = decoded == data

    if verbose:
        print("=== OpcodeVMCodec self-check ===")
        print(f"  input bytes:            {len(data)}")
        print(f"  per-nibble chains:      {stats['n_input_chains']}")
        print(f"  opcode set size:        {stats['n_opcodes']}")
        print(f"  VM stream length:       {stats['n_vm_steps']}")
        print(f"    terminal emissions:   {stats['n_terminal_emissions']}")
        print(f"    opcode emissions:     {stats['n_opcode_emissions']}")
        print(f"  compression per step:   {stats['compression_per_step']:.3f} "
              f"chains/step")
        print(f"  encoded:                {len(encoded)} bytes "
              f"({8 * len(encoded) / len(data):.3f} b/byte)")
        print(f"    header:               {stats['header_bytes']} bytes")
        print(f"    payload:              {stats['payload_bytes']} bytes")
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
