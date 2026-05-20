"""Eliza.PreseededSPPFCodec — SPPF codec using pre-seeded substrate-native
opcodes as initial grammar rules.

Per the user's design: each grammar rule is an opcode. We pre-populate
ChainSequitur with substrate-native opcodes (V₄/Sylow-3/composite
generators) before observing the input. Rule-utility checking is
DISABLED — per substrate-honest discipline, every observed digram is
catalogued, not garbage-collected.

The codec output:
  * Header: n_total_rules, n_preseeded, body_length, per-rule body lengths
  * NOTE: pre-seeded rules don't need transmission of their bodies
    (the decoder shares the same opcode set), only their use marker.
  * Rule definitions (only the Sequitur-INFERRED rules' bodies)
  * Start rule body (the coefficients = input's path through the model)

This saves bits compared to the pure SPPF codec on the pre-seeded
portion of the grammar — only the INFERRED rules' bodies are sent.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from eliza.arith import RangeDecoder, RangeEncoder
from eliza.chain_symbol import ChainSymbol
from eliza.lossless_chain_codec import _CHAIN_BY_INDEX, _INDEX_BY_CHAIN
from eliza.opcode_set import Opcode, build_default_opcodes
from eliza.per_nibble_chain import (
    nibbles_to_bytes, nibble_from_transition, per_nibble_chain_stream,
)
from eliza.preseeded_chain_sequitur import PreseededChainSequitur
from eliza.sequitur import NT


def encode(data: bytes, opcodes: List[Opcode] = None) -> Tuple[bytes, dict]:
    """Encode `data` using a pre-seeded grammar.

    Both encoder and decoder share the same opcode set (passed
    explicitly or default-built). Only INFERRED rules need their bodies
    transmitted; pre-seeded rule IDs are pre-known on both sides.
    """
    opcodes = opcodes if opcodes is not None else build_default_opcodes()
    chain_stream = per_nibble_chain_stream(data)
    pcs = PreseededChainSequitur(opcodes=opcodes)
    pcs.observe_stream(chain_stream)

    all_rules = pcs.all_rules()
    body = all_rules.get(0, [])
    n_preseeded = pcs.n_preseeded()
    all_rule_ids_sorted = sorted(rid for rid in all_rules if rid != 0)
    n_total = len(all_rule_ids_sorted)
    inferred_rule_ids = [rid for rid in all_rule_ids_sorted
                         if rid > n_preseeded]
    inferred_bodies = [all_rules[rid] for rid in inferred_rule_ids]

    # Joint alphabet: 24 chain terminals + n_total NT slots. Compact IDs
    # for NT references: rule_id -> 0..n_total-1.
    compact_id = {rid: i for i, rid in enumerate(all_rule_ids_sorted)}
    JOINT_N = 24 + n_total

    def sym_to_joint_idx(sym: Any) -> int:
        if isinstance(sym, ChainSymbol):
            return _INDEX_BY_CHAIN[sym]
        return 24 + compact_id[sym.rule_id]

    # Header.
    header = bytearray()
    header.extend(n_total.to_bytes(4, "little"))
    header.extend(n_preseeded.to_bytes(4, "little"))
    header.extend(len(body).to_bytes(4, "little"))
    # Per-inferred-rule body lengths.
    for ib in inferred_bodies:
        if len(ib) > 0xFFFF:
            raise ValueError(f"inferred rule body too long ({len(ib)})")
        header.extend(len(ib).to_bytes(2, "little"))

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

    # Encode inferred rule bodies only.
    rule_counts: Dict[int, int] = {}
    for ib in inferred_bodies:
        for sym in ib:
            idx = sym_to_joint_idx(sym)
            encode_sym_adaptive(idx, rule_counts)
            rule_counts[idx] = rule_counts.get(idx, 0) + 1

    # Encode start rule body.
    body_counts: Dict[int, int] = {}
    for sym in body:
        idx = sym_to_joint_idx(sym)
        encode_sym_adaptive(idx, body_counts)
        body_counts[idx] = body_counts.get(idx, 0) + 1

    payload = enc.finish()
    encoded = bytes(header) + payload
    return encoded, {
        "encoded_bytes": len(encoded),
        "header_bytes": len(header),
        "payload_bytes": len(payload),
        "n_input_chains": len(chain_stream),
        "n_total_rules": n_total,
        "n_preseeded_rules": n_preseeded,
        "n_inferred_rules": len(inferred_rule_ids),
        "start_rule_body_length": len(body),
    }


def decode(encoded: bytes, opcodes: List[Opcode] = None) -> bytes:
    """Reconstruct via pre-seeded grammar + inferred rules + start rule body."""
    opcodes = opcodes if opcodes is not None else build_default_opcodes()
    # Decoder-side pre-seeding: build the same pre-seeded rules.
    decoder_seed = PreseededChainSequitur(opcodes=opcodes)
    preseeded_bodies = {
        rid: list(decoder_seed.underlying.rules[rid].body_iter())
        for rid in decoder_seed.rule_id_to_opcode
    }
    preseeded_rules: Dict[int, List[Any]] = {
        rid: [n.sym for n in nodes]
        for rid, nodes in preseeded_bodies.items()
    }

    n_total = int.from_bytes(encoded[:4], "little")
    n_preseeded = int.from_bytes(encoded[4:8], "little")
    body_len = int.from_bytes(encoded[8:12], "little")
    n_inferred = n_total - n_preseeded
    cursor = 12
    inferred_lengths: List[int] = []
    for _ in range(n_inferred):
        inferred_lengths.append(
            int.from_bytes(encoded[cursor:cursor + 2], "little")
        )
        cursor += 2
    payload = encoded[cursor:]
    dec = RangeDecoder(payload)

    JOINT_N = 24 + n_total
    SCALE = 1024

    def decode_sym_adaptive(counts: Dict[int, int]) -> int:
        alpha = 0.5
        cumfreqs = [0]
        for j in range(JOINT_N):
            f = counts.get(j, 0) + alpha
            cumfreqs.append(cumfreqs[-1] + max(1, int(round(f * SCALE))))
        total = cumfreqs[-1]
        return dec.decode(cumfreqs, total)

    # Decode inferred rules.
    inferred_rules: Dict[int, List[Any]] = {}
    rule_counts: Dict[int, int] = {}
    for k, body_len_k in enumerate(inferred_lengths):
        rule_id = n_preseeded + k + 1
        body = []
        for _ in range(body_len_k):
            idx = decode_sym_adaptive(rule_counts)
            if idx < 24:
                body.append(_CHAIN_BY_INDEX[idx])
            else:
                # Compact id = idx - 24. Compact IDs are assigned in
                # sorted order over all rule IDs. So compact_id k+1
                # maps to all_rule_ids_sorted[k]. The pre-seeded rules
                # come first (IDs 1..n_preseeded), then inferred.
                # In this decoder we know the rule IDs in order.
                compact = idx - 24
                # Reconstruct the rule_id from compact_id; the order
                # is: pre-seeded IDs 1..n_preseeded, then inferred
                # n_preseeded+1..n_total.
                if compact < n_preseeded:
                    rid = compact + 1
                else:
                    rid = compact + 1
                body.append(NT(rid, residue="e"))
            rule_counts[idx] = rule_counts.get(idx, 0) + 1
        inferred_rules[rule_id] = body

    # Decode start rule body.
    body_counts: Dict[int, int] = {}
    decoded_body: List[Any] = []
    for _ in range(body_len):
        idx = decode_sym_adaptive(body_counts)
        if idx < 24:
            decoded_body.append(_CHAIN_BY_INDEX[idx])
        else:
            compact = idx - 24
            rid = compact + 1
            decoded_body.append(NT(rid, residue="e"))
        body_counts[idx] = body_counts.get(idx, 0) + 1

    # Combine pre-seeded + inferred rules into one table.
    full_rules: Dict[int, List[Any]] = {}
    full_rules.update(preseeded_rules)
    full_rules.update(inferred_rules)

    # Unfold the body recursively to ChainSymbol terminals.
    def unfold(body: List[Any]) -> List[ChainSymbol]:
        out: List[ChainSymbol] = []
        stack: List[Any] = list(reversed(body))
        while stack:
            sym = stack.pop()
            if isinstance(sym, ChainSymbol):
                out.append(sym)
            else:
                sub = full_rules[sym.rule_id]
                for s in reversed(sub):
                    stack.append(s)
        return out

    chain_terminals = unfold(decoded_body)

    # Invert per-nibble to bytes.
    from eliza.alphabets import ORIGIN
    nibbles: List[int] = []
    state = ORIGIN
    for ch in chain_terminals:
        after = ch.to_s4()
        n = nibble_from_transition(state, after)
        if n is None:
            raise ValueError(
                f"invalid chain transition at #{len(nibbles)}"
            )
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
        print("=== PreseededSPPFCodec self-check ===")
        print(f"  input bytes:          {len(data)}")
        print(f"  total rules:          {stats['n_total_rules']}")
        print(f"    pre-seeded:         {stats['n_preseeded_rules']}")
        print(f"    inferred:           {stats['n_inferred_rules']}")
        print(f"  start rule body len:  {stats['start_rule_body_length']}")
        print(f"  encoded:              {len(encoded)} bytes "
              f"({8 * len(encoded) / len(data):.3f} b/byte)")
        print(f"    header:             {stats['header_bytes']} bytes")
        print(f"    payload:            {stats['payload_bytes']} bytes")
        print(f"  round-trip:           {'OK' if ok else 'FAIL'}")
        if not ok:
            diffs = sum(1 for i in range(min(len(data), len(decoded)))
                        if data[i] != decoded[i])
            print(f"    bytes differ:       {diffs} / {min(len(data), len(decoded))}")
            print(f"    decoded length:     {len(decoded)}")
        print(f"\nResult: {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
