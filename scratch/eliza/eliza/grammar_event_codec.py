"""Eliza.GrammarEventCodec — SPPF-as-Free-Markov-Model lossless codec.

Per the user's framing: the SPPF we assemble during ChainSequitur
processing IS the free Markov model. We ship two things:

  (1) The SPPF/grammar definition: rule-creation events (rule_id,
      body_a, body_b). This is the algebraic structure.
  (2) The "coefficients": the start rule body (R0 after extraction) —
      the input's specific path through the model, expressed as a
      sequence in the joint alphabet [chain-terminals ∪ NT-refs].

Decoder: replay rule events → reconstruct grammar; decode start rule
body; UNFOLD via grammar → chain terminal stream; invert per-nibble
(via nibble_from_transition) → byte stream.

LOSSLESS reconstruction. Per [[homology-cohomology-recursion]]: the
grammar is the cohomology (catalogued structure); the coefficients
are the homology (observed traversal); together they reconstruct
the input.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from eliza.arith import RangeDecoder, RangeEncoder
from eliza.chain_symbol import ChainSymbol
from eliza.chain_trigram import ChainTrigramPredictor
from eliza.lossless_chain_codec import _CHAIN_BY_INDEX, _INDEX_BY_CHAIN
from eliza.per_nibble_chain import (
    nibbles_to_bytes, nibble_from_transition, per_nibble_chain_stream,
)
from eliza.sequitur import NT, Sequitur


# --- Encoder ----------------------------------------------------------


@dataclass
class _EncoderResult:
    rule_events: List[List[Any]]          # body symbols per rule, in id order
    start_rule_body: List[Any]            # symbols in R0 (chain terminals or NTs)
    rules: Dict[int, List[Any]]           # full rule table
    rule_id_order: List[int]              # rule IDs in encoding order


def _build_grammar(chain_stream: List[ChainSymbol]) -> _EncoderResult:
    """Run Sequitur over the chain stream; recover the final rule table
    and the start rule body. Rules in ascending id order are the SPPF
    nodes in the order Sequitur created them.

    Sequitur's utility check inlines under-used rules, so final bodies
    may have length > 2. We store body lengths explicitly.
    """
    seq = Sequitur()
    for sym in chain_stream:
        seq.observe(sym)
    rules = seq.all_rules()
    start_rule_body = rules.get(0, [])
    rule_id_order = sorted(rid for rid in rules if rid != 0)
    rule_events: List[List[Any]] = [list(rules[rid]) for rid in rule_id_order]
    return _EncoderResult(rule_events=rule_events,
                          start_rule_body=start_rule_body,
                          rules=rules,
                          rule_id_order=rule_id_order)


def encode(data: bytes) -> Tuple[bytes, dict]:
    """Encode bytes as: header + rule definitions + start rule body.

    Header layout:
      * 4 bytes: n_rules
      * 4 bytes: start_rule_body_length
      * 2 bytes × n_rules: rule body lengths (uint16)
    """
    chain_stream = per_nibble_chain_stream(data)
    result = _build_grammar(chain_stream)
    n_rules = len(result.rule_events)
    body = result.start_rule_body
    JOINT_N = 24 + n_rules

    # Compact mapping from original rule_id to [0..n_rules-1].
    compact_id = {rid: i for i, rid in enumerate(result.rule_id_order)}

    def sym_to_joint_idx(sym: Any) -> int:
        if isinstance(sym, ChainSymbol):
            return _INDEX_BY_CHAIN[sym]
        return 24 + compact_id[sym.rule_id]

    # Header.
    header = bytearray()
    header.extend(n_rules.to_bytes(4, "little"))
    header.extend(len(body).to_bytes(4, "little"))
    for rule_body in result.rule_events:
        if len(rule_body) > 0xFFFF:
            raise ValueError(f"rule body too long ({len(rule_body)}) for uint16")
        header.extend(len(rule_body).to_bytes(2, "little"))

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

    # Rule definitions: variable-length bodies, fixed joint alphabet.
    # Adaptive predictor over the joint alphabet, persistent across rules.
    rule_counts: Dict[int, int] = {}
    for rule_body in result.rule_events:
        for sym in rule_body:
            idx = sym_to_joint_idx(sym)
            encode_sym_adaptive(idx, rule_counts)
            rule_counts[idx] = rule_counts.get(idx, 0) + 1

    # Start rule body: separate adaptive predictor.
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
        "n_rules": n_rules,
        "start_rule_body_length": len(body),
        "joint_alphabet_size": JOINT_N,
        "total_rule_body_symbols": sum(len(r) for r in result.rule_events),
    }


# --- Decoder ----------------------------------------------------------


def _unfold_to_chains(body: List[Any], rules: Dict[int, List[Any]]
                      ) -> List[ChainSymbol]:
    """Expand `body` (sequence of [terminals ∪ NTs]) through `rules`
    into a flat sequence of ChainSymbol terminals."""
    out: List[ChainSymbol] = []
    stack: List[Any] = list(reversed(body))
    while stack:
        sym = stack.pop()
        if isinstance(sym, ChainSymbol):
            out.append(sym)
        else:
            # NT — expand by pushing its body in reverse.
            sub = rules[sym.rule_id]
            for s in reversed(sub):
                stack.append(s)
    return out


def decode(encoded: bytes) -> bytes:
    """Replay rule events + decode start rule body; unfold; invert to bytes."""
    n_rules = int.from_bytes(encoded[:4], "little")
    body_len = int.from_bytes(encoded[4:8], "little")
    rule_lengths: List[int] = []
    cursor = 8
    for _ in range(n_rules):
        rule_lengths.append(int.from_bytes(encoded[cursor:cursor + 2], "little"))
        cursor += 2
    payload = encoded[cursor:]
    dec = RangeDecoder(payload)

    JOINT_N = 24 + n_rules
    SCALE = 1024

    def decode_sym_adaptive(counts: Dict[int, int]) -> int:
        alpha = 0.5
        cumfreqs = [0]
        for j in range(JOINT_N):
            f = counts.get(j, 0) + alpha
            cumfreqs.append(cumfreqs[-1] + max(1, int(round(f * SCALE))))
        total = cumfreqs[-1]
        return dec.decode(cumfreqs, total)

    # (1) Decode rule definitions. Compact rule IDs are [0..n_rules-1];
    # we represent the decoded grammar with rule_id = compact_id + 1
    # so NT references match the encoder's `compact_id`.
    rules: Dict[int, List[Any]] = {}
    rule_counts: Dict[int, int] = {}
    for k in range(n_rules):
        rule_id = k + 1
        body = []
        for _ in range(rule_lengths[k]):
            idx = decode_sym_adaptive(rule_counts)
            if idx < 24:
                body.append(_CHAIN_BY_INDEX[idx])
            else:
                ref_rid = idx - 24 + 1
                body.append(NT(ref_rid, residue="e"))
            rule_counts[idx] = rule_counts.get(idx, 0) + 1
        rules[rule_id] = body

    # (2) Decode start rule body.
    body_counts: Dict[int, int] = {}
    decoded_body: List[Any] = []
    for _ in range(body_len):
        idx = decode_sym_adaptive(body_counts)
        if idx < 24:
            decoded_body.append(_CHAIN_BY_INDEX[idx])
        else:
            ref_rid = idx - 24 + 1
            decoded_body.append(NT(ref_rid, residue="e"))
        body_counts[idx] = body_counts.get(idx, 0) + 1

    # (3) Unfold to chain terminals.
    chain_terminals = _unfold_to_chains(decoded_body, rules)

    # (4) Invert per-nibble to bytes.
    from eliza.alphabets import ORIGIN
    nibbles: List[int] = []
    state = ORIGIN
    for ch in chain_terminals:
        after = ch.to_s4()
        n = nibble_from_transition(state, after)
        if n is None:
            raise ValueError(
                f"chain stream invalid at nibble #{len(nibbles)}: "
                f"transition ({state}, {after}) has no producing nibble"
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
        print("=== GrammarEventCodec (SPPF + coefficients) self-check ===")
        print(f"  input bytes:          {len(data)}")
        print(f"  per-nibble chains:    {stats['n_input_chains']}")
        print(f"  grammar rules (SPPF): {stats['n_rules']}")
        print(f"  start-rule body len:  {stats['start_rule_body_length']}")
        print(f"  joint alphabet size:  {stats['joint_alphabet_size']}")
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
