"""Eliza.StackMachineCodec — codec as a stack machine over transformation flags.

Per the user's redesign:
  "All of our transformations should be flags; we don't want to say
   whether we are or are not transforming each step, we want to say
   whether we're changing what we're doing. That raises the question
   of in what order to apply the transformative steps. We need a stack
   machine that carries the transformation pipeline state, and the
   opcodes manipulate the stack."

Key idea: STICKINESS. The codec is a stack machine with a small
bounded-depth stack. Each stack entry is a tuple of transformation
flags (currently (rewrite_mode, observe_mode), extensible to other
axes). The TOP of the stack determines current behaviour. Stack
opcodes (TOGGLE_REWRITE, TOGGLE_OBSERVE, SAVE_STATE, RESTORE_STATE)
modify the stack; default emissions follow the current top.

This generalises the flip-opcode design: one flip pays per deviation,
one toggle pays once to ENTER a deviation mode and once to LEAVE. For
a run of N consecutive leave-alone positions, flip costs N opcode
emissions; toggle costs 2.

The order question is dispatched mechanically: stack-op SEQUENCE = the
order of state changes. Different orderings produce different stack
states; the encoder searches reachable states via lookahead.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from eliza.arith import RangeDecoder, RangeEncoder
from eliza.chain_symbol import ChainSymbol
from eliza.lossless_chain_codec import _CHAIN_BY_INDEX, _INDEX_BY_CHAIN
from eliza.opcode_set import Opcode, build_full_opcode_set
from eliza.adaptive_opcode_codec import _make_composite_opcode
from eliza.per_nibble_chain import (
    nibbles_to_bytes, nibble_from_transition, per_nibble_chain_stream,
)


# Stack entries: (rewrite_mode, observe_mode) tuples. rewrite_mode ∈
# {0, 1}: 1 = auto-rewrite digrams, 0 = leave-alone. observe_mode ∈
# {0, 1}: 1 = pass symbols to grammar, 0 = bypass.
StackEntry = Tuple[int, int]
INITIAL_ENTRY: StackEntry = (1, 1)   # auto-rewrite ON, observe ON


# Stack opcode IDs (positions in the joint alphabet, relative to the
# end of the opcodes section):
#   0 = TOGGLE_REWRITE  — flip top entry's rewrite bit
#   1 = TOGGLE_OBSERVE  — flip top entry's observe bit
N_STACK_OPCODES = 2


def _apply_stack_op(op: int, stack: List[StackEntry]) -> List[StackEntry]:
    """Return a NEW stack with the op applied; doesn't mutate input."""
    if not stack:
        return [INITIAL_ENTRY]
    new_stack = list(stack)
    top = new_stack[-1]
    if op == 0:    # TOGGLE_REWRITE
        new_stack[-1] = (1 - top[0], top[1])
    elif op == 1:  # TOGGLE_OBSERVE
        new_stack[-1] = (top[0], 1 - top[1])
    return new_stack


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


# --- K-step beam over (stack_op_sequence, position) -------------------


def _k_step_beam_cost(
    stream: List[ChainSymbol], start_pos: int,
    opcodes: List[Opcode], digram_index: Dict[Tuple[int, int], int],
    prev_emission: Optional[int], counts_snapshot: Dict[int, int],
    stack_state: List[StackEntry], k_steps: int,
    initial_stack_ops: List[int],
) -> float:
    """Estimate total bits for the next k_steps emissions, ASSUMING we
    first emit `initial_stack_ops` stack opcodes (each costs one
    emission), then proceed with regular emissions under the resulting
    stack state.

    Simulates the actual codec logic locally (without mutating any
    enclosing state).
    """
    from math import log2
    opcodes_local = list(opcodes)
    digram_local = dict(digram_index)
    counts_local = dict(counts_snapshot)
    stack_local = list(stack_state)
    prev_local = prev_emission
    pos = start_pos
    bits = 0.0

    n_initial = len(opcodes)
    n_stack_opcode_base = 24 + n_initial

    def alphabet_size() -> int:
        return 24 + len(opcodes_local) + N_STACK_OPCODES

    def emit_cost(emit_idx: int) -> float:
        alpha = 0.5
        a_size = alphabet_size()
        total = sum(counts_local.values()) + alpha * a_size
        p = (counts_local.get(emit_idx, 0) + alpha) / total
        return -log2(max(p, 1e-9))

    # Apply initial stack ops first (counted in cost).
    for op in initial_stack_ops:
        emit_idx = 24 + len(opcodes_local) + op
        bits += emit_cost(emit_idx)
        counts_local[emit_idx] = counts_local.get(emit_idx, 0) + 1
        stack_local = _apply_stack_op(op, stack_local)

    steps = 0
    while steps < k_steps and pos < len(stream):
        rewrite_mode, observe_mode = stack_local[-1]
        if observe_mode == 0:
            # SKIP: emit raw terminal, prev unchanged.
            emit_idx = _INDEX_BY_CHAIN[stream[pos]]
            advance = 1
            bits += emit_cost(emit_idx)
            counts_local[emit_idx] = counts_local.get(emit_idx, 0) + 1
        else:
            # OBSERVE.
            idx = _best_opcode_at(stream, pos, opcodes_local)
            if idx is None:
                emit_idx = _INDEX_BY_CHAIN[stream[pos]]
                advance = 1
            else:
                emit_idx = 24 + idx
                advance = opcodes_local[idx].length
            bits += emit_cost(emit_idx)
            counts_local[emit_idx] = counts_local.get(emit_idx, 0) + 1
            # Auto-rewrite gated by rewrite_mode.
            if prev_local is not None:
                digram = (prev_local, emit_idx)
                if rewrite_mode == 1 and digram in digram_local:
                    composite = _make_composite_opcode(
                        f"K_COMP_{len(opcodes_local) - n_initial}",
                        prev_local, emit_idx, opcodes_local,
                    )
                    opcodes_local.append(composite)
                    digram_local[digram] = 24 + (len(opcodes_local) - 1)
                else:
                    if digram not in digram_local:
                        digram_local[digram] = -1
            prev_local = emit_idx
        pos += advance
        steps += 1
    return bits


# --- Encoder ------------------------------------------------------------


def encode(
    data: bytes, initial_opcodes: List[Opcode] = None,
    k_steps: int = 4,
) -> Tuple[bytes, dict]:
    initial_opcodes = (initial_opcodes if initial_opcodes is not None
                        else build_full_opcode_set())
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
    toggle_history = {"rewrite": 0, "observe": 0}

    # Candidate stack-op prefixes to try at each position:
    candidate_prefixes = [
        [],            # no stack op (default-sticky)
        [0],           # TOGGLE_REWRITE
        [1],           # TOGGLE_OBSERVE
        [0, 1],        # TOGGLE both
    ]

    while pos < len(chain_stream):
        # Evaluate K-step cost for each candidate prefix.
        best_prefix = []
        best_cost = float("inf")
        for prefix in candidate_prefixes:
            cost = _k_step_beam_cost(
                chain_stream, pos, opcodes, digram_index,
                prev_emission, counts, stack, k_steps, prefix,
            )
            if cost < best_cost:
                best_cost = cost
                best_prefix = prefix

        # Apply the chosen prefix.
        for op in best_prefix:
            emit_idx = 24 + len(opcodes) + op
            encode_emission(emit_idx)
            stack = _apply_stack_op(op, stack)
            n_stack_ops += 1
            n_total_emissions += 1
            if op == 0:
                toggle_history["rewrite"] += 1
            else:
                toggle_history["observe"] += 1

        # Regular emission under current stack-top mode.
        rewrite_mode, observe_mode = stack[-1]
        if observe_mode == 0:
            # SKIP path.
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

        # Auto-rewrite gated by mode.
        if observe_mode == 1 and prev_emission is not None:
            digram = (prev_emission, emit_idx)
            if rewrite_mode == 1 and digram in digram_index:
                composite = _make_composite_opcode(
                    f"SM_COMP_{n_growth}",
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
        # if SKIP, prev_emission unchanged
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
        "n_growth": n_growth,
        "n_terminal_emissions": n_terminal,
        "n_opcode_emissions": n_opcode,
        "n_final_opcodes": len(opcodes),
        "toggle_rewrite_count": toggle_history["rewrite"],
        "toggle_observe_count": toggle_history["observe"],
        "k_steps": k_steps,
    }


# --- Decoder ------------------------------------------------------------


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

    def alphabet_size() -> int:
        return 24 + len(opcodes) + N_STACK_OPCODES

    def decode_emission() -> int:
        a_size = alphabet_size()
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
        n_opcodes = len(opcodes)
        # Layout: [0..23] terminals, [24..24+n_opcodes-1] opcodes,
        # [24+n_opcodes..24+n_opcodes+1] stack ops.
        if emit_idx >= 24 + n_opcodes:
            # Stack op.
            op_idx = emit_idx - (24 + n_opcodes)
            stack = _apply_stack_op(op_idx, stack)
            continue
        # Regular emission.
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
                    f"SM_COMP_{n_growth}",
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
        # if SKIP, prev_emission unchanged

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
        print("=== StackMachineCodec self-check ===")
        print(f"  input bytes:           {len(data)}")
        print(f"  per-nibble chains:     {stats['n_input_chains']}")
        print(f"  k_steps lookahead:     {stats['k_steps']}")
        print(f"  total emissions:       {stats['n_total_emissions']}")
        print(f"    stack-op emissions:  {stats['n_stack_ops']}")
        print(f"    terminal:            {stats['n_terminal_emissions']}")
        print(f"    opcode:              {stats['n_opcode_emissions']}")
        print(f"  toggle counts:         rewrite={stats['toggle_rewrite_count']} "
              f"observe={stats['toggle_observe_count']}")
        print(f"  growth events:         {stats['n_growth']}")
        print(f"  final opcodes:         {stats['n_final_opcodes']}")
        print(f"  encoded:               {len(encoded)} bytes "
              f"({8 * len(encoded) / len(data):.3f} b/byte)")
        print(f"  round-trip:            {'OK' if ok else 'FAIL'}")
        if not ok:
            diffs = sum(1 for i in range(min(len(data), len(decoded)))
                        if data[i] != decoded[i])
            print(f"    bytes differ:        {diffs}")
            print(f"    decoded length:      {len(decoded)}")
        print(f"\nResult: {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
