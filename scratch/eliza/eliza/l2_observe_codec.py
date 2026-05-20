"""Eliza.L2ObserveCodec — Level-2 codec: passing to sequitur is an opcode.

Per the user's tetrative-axis directive:
  "If [L1] works well, we can make _passing to sequitur_ an opcode."

L2 makes "OBSERVE this symbol in the grammar machinery" vs "SKIP this
symbol (bypass grammar)" a per-position speculative-commit. The L2
flag is 1 bit per VM step:

  * OBSERVE = the symbol participates in grammar (digrams form, opcodes
              may grow via L1 rule)
  * SKIP    = the symbol is emitted as a raw terminal; the grammar's
              "previous symbol" memory bypasses it

For brevity this codec assumes L1's automatic rewriting (no L1 flag).
The full tetrative codec (L0+L1+L2) is left as a follow-on slice; the
goal here is to measure the L2 trade-off in isolation.

Like L1, L2 adds a control bit per position; the question is whether
the savings from selectively skipping noisy positions outweigh the
control-bit overhead.
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


# L2 heuristic for OBSERVE vs SKIP: SKIP when the symbol's chain hasn't
# repeated in the recent window AND its terminal cost is small. Coarse
# but cheap; explicit speculation would multiply runtime.


def _should_skip(
    chain: ChainSymbol, recent: List[ChainSymbol], skip_history: List[int],
) -> bool:
    """Heuristic: SKIP if (a) chain is unique in `recent` (no repetition
    suggesting future grammar value) AND (b) the L2 flag's encoding
    cost is dominated by the savings of bypassing grammar.

    Simplistic: SKIP if `chain` doesn't appear in the last 16 positions.
    """
    return chain not in recent[-16:]


def encode(
    data: bytes, initial_opcodes: List[Opcode] = None,
) -> Tuple[bytes, dict]:
    initial_opcodes = (initial_opcodes if initial_opcodes is not None
                        else build_full_opcode_set())
    opcodes: List[Opcode] = list(initial_opcodes)
    chain_stream = per_nibble_chain_stream(data)

    enc = RangeEncoder()
    SCALE = 1024
    n_initial = len(initial_opcodes)

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
    observe_counts = [0, 0]  # [skip, observe]
    digram_index: Dict[Tuple[int, int], int] = {}
    recent: List[ChainSymbol] = []
    skip_history: List[int] = []
    pos = 0
    prev_observed_emission: Optional[int] = None
    n_terminal = 0
    n_opcode = 0
    n_skipped = 0
    n_observed = 0
    n_growth = 0

    def encode_emission(emit_idx: int, alphabet_size: int):
        alpha = 0.5
        cumfreqs = [0]
        for j in range(alphabet_size):
            f = counts.get(j, 0) + alpha
            cumfreqs.append(cumfreqs[-1] + max(1, int(round(f * SCALE))))
        total = cumfreqs[-1]
        enc.encode(cumfreqs, emit_idx, total)

    def encode_observe_flag(flag: int):
        alpha = 0.5
        c0 = observe_counts[0] + alpha
        c1 = observe_counts[1] + alpha
        f0 = max(1, int(round(c0 * SCALE)))
        f1 = max(1, int(round(c1 * SCALE)))
        cumfreqs = [0, f0, f0 + f1]
        enc.encode(cumfreqs, flag, cumfreqs[-1])

    while pos < len(chain_stream):
        chain = chain_stream[pos]
        skip = _should_skip(chain, recent, skip_history)
        if skip:
            # SKIP path: emit raw terminal, do not feed to grammar.
            emit_idx = _INDEX_BY_CHAIN[chain]
            alphabet_size = 24 + len(opcodes)
            encode_emission(emit_idx, alphabet_size)
            counts[emit_idx] = counts.get(emit_idx, 0) + 1
            encode_observe_flag(0)
            observe_counts[0] += 1
            n_skipped += 1
            n_terminal += 1
            pos += 1
            recent.append(chain)
            # prev_observed_emission unchanged.
        else:
            # OBSERVE path: speculative opcode-VM with adaptive growth.
            idx = best_opcode_at_pos(pos)
            if idx is None:
                emit_idx = _INDEX_BY_CHAIN[chain]
                advance = 1
                n_terminal += 1
            else:
                emit_idx = 24 + idx
                advance = opcodes[idx].length
                n_opcode += 1
            alphabet_size = 24 + len(opcodes)
            encode_emission(emit_idx, alphabet_size)
            counts[emit_idx] = counts.get(emit_idx, 0) + 1
            encode_observe_flag(1)
            observe_counts[1] += 1
            n_observed += 1
            # Adaptive growth on observed digrams only.
            if prev_observed_emission is not None:
                digram = (prev_observed_emission, emit_idx)
                if digram in digram_index:
                    composite = _make_composite_opcode(
                        f"L2_COMP_{n_growth}",
                        prev_observed_emission, emit_idx, opcodes,
                    )
                    opcodes.append(composite)
                    digram_index[digram] = 24 + (len(opcodes) - 1)
                    n_growth += 1
                else:
                    digram_index[digram] = -1
            prev_observed_emission = emit_idx
            pos += advance
            for j in range(advance):
                if pos - advance + j < len(chain_stream):
                    recent.append(chain_stream[pos - advance + j])

    payload = enc.finish()
    n_vm = n_terminal + n_opcode
    header = bytearray()
    header.extend(len(chain_stream).to_bytes(4, "little"))
    header.extend(n_initial.to_bytes(4, "little"))
    header.extend(n_vm.to_bytes(4, "little"))
    encoded = bytes(header) + payload
    return encoded, {
        "encoded_bytes": len(encoded),
        "n_input_chains": len(chain_stream),
        "n_initial_opcodes": n_initial,
        "n_final_opcodes": len(opcodes),
        "n_vm_steps": n_vm,
        "n_observed": n_observed,
        "n_skipped": n_skipped,
        "n_growth": n_growth,
        "n_terminal_emissions": n_terminal,
        "n_opcode_emissions": n_opcode,
    }


def decode(encoded: bytes, initial_opcodes: List[Opcode] = None) -> bytes:
    initial_opcodes = (initial_opcodes if initial_opcodes is not None
                        else build_full_opcode_set())
    n_chain = int.from_bytes(encoded[:4], "little")
    n_initial = int.from_bytes(encoded[4:8], "little")
    n_vm = int.from_bytes(encoded[8:12], "little")
    opcodes: List[Opcode] = list(initial_opcodes)
    payload = encoded[12:]
    dec = RangeDecoder(payload)

    SCALE = 1024
    counts: Dict[int, int] = {}
    observe_counts = [0, 0]
    digram_index: Dict[Tuple[int, int], int] = {}
    chain_terminals: List[ChainSymbol] = []
    prev_observed_emission: Optional[int] = None
    n_growth = 0

    def decode_emission(alphabet_size: int) -> int:
        alpha = 0.5
        cumfreqs = [0]
        for j in range(alphabet_size):
            f = counts.get(j, 0) + alpha
            cumfreqs.append(cumfreqs[-1] + max(1, int(round(f * SCALE))))
        total = cumfreqs[-1]
        return dec.decode(cumfreqs, total)

    def decode_observe_flag() -> int:
        alpha = 0.5
        c0 = observe_counts[0] + alpha
        c1 = observe_counts[1] + alpha
        f0 = max(1, int(round(c0 * SCALE)))
        f1 = max(1, int(round(c1 * SCALE)))
        cumfreqs = [0, f0, f0 + f1]
        return dec.decode(cumfreqs, cumfreqs[-1])

    for _ in range(n_vm):
        alphabet_size = 24 + len(opcodes)
        emit_idx = decode_emission(alphabet_size)
        counts[emit_idx] = counts.get(emit_idx, 0) + 1
        flag = decode_observe_flag()
        observe_counts[flag] += 1
        if emit_idx < 24:
            chain_terminals.append(_CHAIN_BY_INDEX[emit_idx])
        else:
            op = opcodes[emit_idx - 24]
            chain_terminals.extend(op.body)
        if flag == 1:    # OBSERVE
            if prev_observed_emission is not None:
                digram = (prev_observed_emission, emit_idx)
                if digram in digram_index:
                    composite = _make_composite_opcode(
                        f"L2_COMP_{n_growth}",
                        prev_observed_emission, emit_idx, opcodes,
                    )
                    opcodes.append(composite)
                    digram_index[digram] = 24 + (len(opcodes) - 1)
                    n_growth += 1
                else:
                    digram_index[digram] = -1
            prev_observed_emission = emit_idx
        # SKIP: prev_observed_emission unchanged.

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
        print("=== L2ObserveCodec self-check ===")
        print(f"  input bytes:        {len(data)}")
        print(f"  per-nibble chains:  {stats['n_input_chains']}")
        print(f"  observe / skip:     {stats['n_observed']} / {stats['n_skipped']}")
        print(f"  initial opcodes:    {stats['n_initial_opcodes']}")
        print(f"  final opcodes:      {stats['n_final_opcodes']}")
        print(f"  rewrites grown:     {stats['n_growth']}")
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
