"""Eliza.PreseededChainSequitur — Sequitur with substrate-native opcodes
as pre-populated rules.

Per the user's design: each grammar rule is an opcode. Pre-populating
the grammar with substrate-native opcodes (V₄ generators, Sylow-3
generators, common compositions) gives Sequitur a structural starter
kit; input observations match against these opcodes first, and new
opcodes (= rules) emerge for input-specific patterns.

The pre-seeded rules occupy low rule_id slots; Sequitur creates new
rules starting at the first unused id. Decoder's MUST share the same
opcode set so rule_ids align.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from eliza.chain_symbol import ChainSymbol
from eliza.opcode_set import Opcode, build_default_opcodes
from eliza.sequitur import NT, Node, Rule, Sequitur


@dataclass
class PreseededChainSequitur:
    """Sequitur with pre-injected rules for substrate-native opcodes.

    The pre-injected rules occupy rule_ids [1..n_opcodes]. Sequitur's
    `_next_id` is set past these so new rules start at n_opcodes + 1.

    Each opcode of length 2 is straightforwardly representable as a
    Sequitur rule. Longer-body opcodes (exploding bitmaps) are NOT
    pre-injected here — they're handled by a separate pattern-matching
    layer (G7).
    """
    opcodes: List[Opcode] = field(default_factory=build_default_opcodes)
    underlying: Sequitur = field(init=False)
    opcode_to_rule_id: Dict[str, int] = field(default_factory=dict)
    rule_id_to_opcode: Dict[int, Opcode] = field(default_factory=dict)

    def __post_init__(self):
        self.underlying = Sequitur()
        # Mark pre-seeded rule IDs as PROTECTED so Sequitur's
        # _maybe_inline_underused doesn't garbage-collect them when
        # their use count is below the usual threshold (≥ 2).
        self.underlying.protected_rule_ids = set()
        # Skip opcodes whose body isn't exactly 2 — Sequitur algorithm
        # creates 2-symbol rules by digram detection.
        rule_id = self.underlying._next_id  # = 1 for fresh Sequitur
        for op in self.opcodes:
            if op.length != 2:
                continue
            # Create a Sequitur Rule with the opcode's body.
            r = Rule(rule_id)
            self.underlying.rules[rule_id] = r
            n1 = Node(sym=op.body[0], rule_id=rule_id)
            n2 = Node(sym=op.body[1], rule_id=rule_id)
            self.underlying._insert_before(r.guard, n1)
            self.underlying._insert_before(r.guard, n2)
            # Register the digram so future occurrences trigger replacement.
            digram = (op.body[0], op.body[1])
            self.underlying.digrams[digram] = n1
            self.opcode_to_rule_id[op.name] = rule_id
            self.rule_id_to_opcode[rule_id] = op
            self.underlying.protected_rule_ids.add(rule_id)
            rule_id += 1
        self.underlying._next_id = rule_id

    def observe(self, sym: ChainSymbol) -> None:
        self.underlying.observe(sym)

    def observe_stream(self, stream) -> None:
        for s in stream:
            self.observe(s)

    def n_rules(self) -> int:
        return self.underlying.n_rules()

    def n_preseeded(self) -> int:
        return len(self.rule_id_to_opcode)

    def n_inferred(self) -> int:
        return self.n_rules() - self.n_preseeded()

    def all_rules(self) -> Dict[int, List[Any]]:
        return self.underlying.all_rules()

    def rule_uses(self) -> Dict[int, int]:
        return {rid: self.underlying.rule_uses(rid)
                for rid in self.underlying.rules}


# --- Self-check ---------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    from pathlib import Path
    from eliza.chain_emitter import chain_stream
    from eliza.per_nibble_chain import per_nibble_chain_stream

    HERE = Path(__file__).resolve().parent
    src = HERE / "engine.py"
    with open(src, "rb") as f:
        data = f.read()[:4096]

    # (1) Seed with default opcodes.
    pcs = PreseededChainSequitur()
    n_seeded = pcs.n_preseeded()

    # (2) Observe a per-nibble chain stream.
    chains = per_nibble_chain_stream(data)
    pcs.observe_stream(chains)

    total_rules = pcs.n_rules()
    inferred = pcs.n_inferred()

    # (3) Use counts — how often do the pre-seeded opcodes get used?
    uses = pcs.rule_uses()
    preseed_uses = {rid: uses.get(rid, 0)
                    for rid in pcs.rule_id_to_opcode}
    most_used_preseed = sorted(preseed_uses.items(),
                                key=lambda kv: kv[1], reverse=True)

    if verbose:
        print("=== PreseededChainSequitur self-check ===")
        print(f"  input bytes:          {len(data)}")
        print(f"  per-nibble chains:    {len(chains)}")
        print(f"  pre-seeded rules:     {n_seeded}")
        print(f"  total rules after:    {total_rules}")
        print(f"  Sequitur-inferred:    {inferred}")
        print(f"\n  pre-seeded opcode uses (most used first):")
        for rid, n in most_used_preseed:
            op = pcs.rule_id_to_opcode[rid]
            print(f"    R{rid:>3} ({op.name:>22}): {n} uses")

    return True


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
