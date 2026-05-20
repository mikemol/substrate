"""Eliza.FullSpeculationCodec — actually-try-each-path speculation.

Per the user's correction:
  "By 'speculative', I mean 'we should actually try each path and pick
   the one that works best', not 'we should make an educated guess'.
   The beam search shouldn't be searching over a smaller range than
   is being committed to."

And the BWT-emergence diagnostic:
  "Done correctly, BWT should be _emergent_ from the CD rotations."

This codec replaces the K-step beam with **full-remainder simulation**.
At each decision point, for each candidate stack-op prefix:
  * Apply the prefix to the encoder state
  * Encode the ENTIRE REMAINDER of the chain stream under that state
  * Record total bits produced
Commit only the FIRST decision (the prefix at this position) to the
real encoder; move ahead one step; repeat.

This is O(C × N²) per encoding (C candidates × N positions × N
per-simulation work). On 1KB inputs (2K chains, 4 candidates) that's
~16M operations. Slow but tractable; tests the user's hypothesis at
the architectural level.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from eliza.arith import RangeDecoder, RangeEncoder
from eliza.chain_symbol import ChainSymbol
from eliza.lossless_chain_codec import _CHAIN_BY_INDEX, _INDEX_BY_CHAIN
from eliza.opcode_set import Opcode, build_full_opcode_set
from eliza.adaptive_opcode_codec import _make_composite_opcode
from eliza.per_nibble_chain import (
    nibbles_to_bytes, nibble_from_transition, per_nibble_chain_stream,
)
from eliza.stack_machine_codec import (
    StackEntry, INITIAL_ENTRY, N_STACK_OPCODES, _apply_stack_op,
    _best_opcode_at,
)


def _simulate_full_remainder(
    stream: List[ChainSymbol], start_pos: int,
    opcodes: List[Opcode], digram_index: Dict[Tuple[int, int], int],
    prev_emission: Optional[int], counts_snapshot: Dict[int, int],
    stack_state: List[StackEntry], initial_stack_ops: List[int],
    n_initial_opcodes: int,
    early_termination_threshold: float = float("inf"),
) -> float:
    """Simulate encoding from `start_pos` to end of stream under the
    given starting state plus `initial_stack_ops`. Returns total bits.

    `early_termination_threshold`: if the running cost exceeds this,
    bail out with float('inf'). Used by callers to short-circuit
    candidates known to lose.
    """
    from math import log2
    opcodes_local = list(opcodes)
    digram_local = dict(digram_index)
    counts_local = dict(counts_snapshot)
    stack_local = list(stack_state)
    prev_local = prev_emission
    pos = start_pos
    bits = 0.0

    def alphabet_size() -> int:
        return 24 + len(opcodes_local) + N_STACK_OPCODES

    def emit_cost(emit_idx: int) -> float:
        alpha = 0.5
        a_size = alphabet_size()
        total = sum(counts_local.values()) + alpha * a_size
        p = (counts_local.get(emit_idx, 0) + alpha) / total
        return -log2(max(p, 1e-9))

    # Apply initial prefix.
    for op in initial_stack_ops:
        emit_idx = 24 + len(opcodes_local) + op
        bits += emit_cost(emit_idx)
        counts_local[emit_idx] = counts_local.get(emit_idx, 0) + 1
        stack_local = _apply_stack_op(op, stack_local)

    # Encode the full remainder under current state.
    while pos < len(stream):
        if bits >= early_termination_threshold:
            return float("inf")
        rewrite_mode, observe_mode = stack_local[-1]
        if observe_mode == 0:
            emit_idx = _INDEX_BY_CHAIN[stream[pos]]
            advance = 1
            bits += emit_cost(emit_idx)
            counts_local[emit_idx] = counts_local.get(emit_idx, 0) + 1
        else:
            idx = _best_opcode_at(stream, pos, opcodes_local)
            if idx is None:
                emit_idx = _INDEX_BY_CHAIN[stream[pos]]
                advance = 1
            else:
                emit_idx = 24 + idx
                advance = opcodes_local[idx].length
            bits += emit_cost(emit_idx)
            counts_local[emit_idx] = counts_local.get(emit_idx, 0) + 1
            if prev_local is not None:
                digram = (prev_local, emit_idx)
                if rewrite_mode == 1 and digram in digram_local:
                    composite = _make_composite_opcode(
                        f"FS_COMP_{len(opcodes_local) - n_initial_opcodes}",
                        prev_local, emit_idx, opcodes_local,
                    )
                    opcodes_local.append(composite)
                    digram_local[digram] = 24 + (len(opcodes_local) - 1)
                else:
                    if digram not in digram_local:
                        digram_local[digram] = -1
            prev_local = emit_idx
        pos += advance
    return bits


def encode(
    data: bytes, initial_opcodes: List[Opcode] = None,
    candidate_prefixes: List[List[int]] = None,
) -> Tuple[bytes, dict]:
    initial_opcodes = (initial_opcodes if initial_opcodes is not None
                        else build_full_opcode_set())
    if candidate_prefixes is None:
        candidate_prefixes = [
            [],            # no stack op
            [0],           # TOGGLE_REWRITE
            [1],           # TOGGLE_OBSERVE
        ]
    opcodes: List[Opcode] = list(initial_opcodes)
    chain_stream = per_nibble_chain_stream(data)
    enc = RangeEncoder()
    SCALE = 1024
    n_initial = len(initial_opcodes)
    counts: Dict[int, int] = {}
    digram_index: Dict[Tuple[int, int], int] = {}
    stack: List[StackEntry] = [INITIAL_ENTRY]

    def alphabet_size() -> int:
        return 24 + len(opcodes) + N_STACK_OPCODES

    def encode_emission(emit_idx: int):
        a_size = alphabet_size()
        alpha = 0.5
        cumfreqs = [0]
        for j in range(a_size):
            f = counts.get(j, 0) + alpha
            cumfreqs.append(cumfreqs[-1] + max(1, int(round(f * SCALE))))
        total = cumfreqs[-1]
        enc.encode(cumfreqs, emit_idx, total)
        counts[emit_idx] = counts.get(emit_idx, 0) + 1

    pos = 0
    prev_emission: Optional[int] = None
    n_total_emissions = 0
    n_stack_ops = 0
    n_terminal = 0
    n_opcode = 0
    n_growth = 0
    decision_log: List[List[int]] = []

    while pos < len(chain_stream):
        # Full-remainder speculation over each candidate prefix.
        best_prefix = []
        best_cost = float("inf")
        for prefix in candidate_prefixes:
            cost = _simulate_full_remainder(
                chain_stream, pos, opcodes, digram_index,
                prev_emission, counts, stack, prefix, n_initial,
                early_termination_threshold=best_cost,
            )
            if cost < best_cost:
                best_cost = cost
                best_prefix = prefix
        decision_log.append(best_prefix)

        for op in best_prefix:
            emit_idx = 24 + len(opcodes) + op
            encode_emission(emit_idx)
            stack = _apply_stack_op(op, stack)
            n_stack_ops += 1
            n_total_emissions += 1

        rewrite_mode, observe_mode = stack[-1]
        if observe_mode == 0:
            emit_idx = _INDEX_BY_CHAIN[chain_stream[pos]]
            advance = 1
            n_terminal += 1
        else:
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
        n_total_emissions += 1

        if observe_mode == 1 and prev_emission is not None:
            digram = (prev_emission, emit_idx)
            if rewrite_mode == 1 and digram in digram_index:
                composite = _make_composite_opcode(
                    f"FS_COMP_{n_growth}",
                    prev_emission, emit_idx, opcodes,
                )
                opcodes.append(composite)
                digram_index[digram] = 24 + (len(opcodes) - 1)
                n_growth += 1
            else:
                if digram not in digram_index:
                    digram_index[digram] = -1
        if observe_mode == 1:
            prev_emission = emit_idx
        pos += advance

    payload = enc.finish()
    header = bytearray()
    header.extend(len(chain_stream).to_bytes(4, "little"))
    header.extend(n_initial.to_bytes(4, "little"))
    header.extend(n_total_emissions.to_bytes(4, "little"))
    encoded = bytes(header) + payload
    return encoded, {
        "encoded_bytes": len(encoded),
        "n_input_chains": len(chain_stream),
        "n_total_emissions": n_total_emissions,
        "n_stack_ops": n_stack_ops,
        "n_terminal_emissions": n_terminal,
        "n_opcode_emissions": n_opcode,
        "n_growth": n_growth,
        "n_final_opcodes": len(opcodes),
        "decision_log_summary": {
            "no_op": sum(1 for d in decision_log if not d),
            "toggle_rewrite": sum(1 for d in decision_log if d == [0]),
            "toggle_observe": sum(1 for d in decision_log if d == [1]),
        },
    }


def decode(encoded: bytes, initial_opcodes: List[Opcode] = None) -> bytes:
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
    stack: List[StackEntry] = [INITIAL_ENTRY]
    n_growth = 0

    def decode_emission() -> int:
        a_size = 24 + len(opcodes) + N_STACK_OPCODES
        alpha = 0.5
        cumfreqs = [0]
        for j in range(a_size):
            f = counts.get(j, 0) + alpha
            cumfreqs.append(cumfreqs[-1] + max(1, int(round(f * SCALE))))
        total = cumfreqs[-1]
        return dec.decode(cumfreqs, total)

    for _ in range(n_emissions):
        emit_idx = decode_emission()
        counts[emit_idx] = counts.get(emit_idx, 0) + 1
        n_op = len(opcodes)
        if emit_idx >= 24 + n_op:
            op_idx = emit_idx - (24 + n_op)
            stack = _apply_stack_op(op_idx, stack)
            continue
        rewrite_mode, observe_mode = stack[-1]
        if emit_idx < 24:
            chain_terminals.append(_CHAIN_BY_INDEX[emit_idx])
        else:
            op = opcodes[emit_idx - 24]
            chain_terminals.extend(op.body)
        if observe_mode == 1 and prev_emission is not None:
            digram = (prev_emission, emit_idx)
            if rewrite_mode == 1 and digram in digram_index:
                composite = _make_composite_opcode(
                    f"FS_COMP_{n_growth}",
                    prev_emission, emit_idx, opcodes,
                )
                opcodes.append(composite)
                digram_index[digram] = 24 + (len(opcodes) - 1)
                n_growth += 1
            else:
                if digram not in digram_index:
                    digram_index[digram] = -1
        if observe_mode == 1:
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


def self_check(size: int = 256, verbose: bool = True) -> bool:
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
        print("=== FullSpeculationCodec self-check ===")
        print(f"  input bytes:        {len(data)}")
        print(f"  per-nibble chains:  {stats['n_input_chains']}")
        print(f"  total emissions:    {stats['n_total_emissions']}")
        print(f"    stack-op:         {stats['n_stack_ops']}")
        print(f"    terminal:         {stats['n_terminal_emissions']}")
        print(f"    opcode:           {stats['n_opcode_emissions']}")
        print(f"  growth events:      {stats['n_growth']}")
        print(f"  final opcodes:      {stats['n_final_opcodes']}")
        print(f"  decisions:          {stats['decision_log_summary']}")
        print(f"  encoded:            {len(encoded)} bytes "
              f"({8 * len(encoded) / len(data):.3f} b/byte)")
        print(f"  encode time:        {enc_time:.2f}s")
        print(f"  decode time:        {dec_time:.4f}s")
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
