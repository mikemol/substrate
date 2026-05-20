"""Eliza.ChainSequitur — Sequitur inferring grammar over ChainSymbols.

Each Sequitur rule produced by this layer corresponds to a chain
SEQUENCE; the rule LIFTS to a single ChainSymbol via product. That
lifted symbol is the next-level atom for recursive inference (see
`multilevel_chain_sequitur.py`).

Per [[homology-cohomology-recursion]]:
  observed  = per-window ChainSymbols (homology, level 0)
  catalogued = ChainSequitur rules over those (cohomology, level 0)
  lifted    = each rule's product chain (next-level homology)

The substrate's self-similarity: the lifted symbols inhabit the
same alphabet (ChainSymbol) as the level-0 observations, so the
inference machinery is the SAME at every level.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List

from eliza.chain_symbol import ChainSymbol, product as chain_product
from eliza.sequitur import Sequitur


@dataclass
class RuleLift:
    """The level-up information attached to a ChainSequitur rule.

    Sequitur stores the rule body as a sequence of terminals + non-
    terminals. Once the rule's RHS contains only ChainSymbols (after
    chasing any nested non-terminals to their terminal closure),
    `chain_product` collapses it into one lifted ChainSymbol.
    """
    rule_id: int
    body: List[Any]                # raw Sequitur RHS (may contain NTs)
    terminal_closure: List[ChainSymbol]
    lifted: ChainSymbol


@dataclass
class ChainSequitur:
    """A Sequitur instance whose terminals are ChainSymbols.

    Wraps the existing Sequitur class — the wrapper does not change
    Sequitur internals; it simply restricts terminals and exposes
    the per-rule lift.
    """
    underlying: Sequitur = field(default_factory=Sequitur)
    name: str = "chain_sequitur"

    def observe(self, symbol: ChainSymbol) -> None:
        self.underlying.observe(symbol)

    def observe_stream(self, symbols: Iterable[ChainSymbol]) -> None:
        for s in symbols:
            self.observe(s)

    def n_rules(self) -> int:
        return self.underlying.n_rules()

    def all_rules(self) -> Dict[int, List[Any]]:
        return self.underlying.all_rules()

    def top_rule(self) -> List[Any]:
        return self.underlying.top_rule()

    # --- The lift: rule → ChainSymbol -----------------------------------

    def _terminal_closure(self, body: List[Any]) -> List[ChainSymbol]:
        """Recursively expand non-terminals in `body` to a flat list of
        ChainSymbol terminals."""
        all_rules = self.all_rules()
        out: List[ChainSymbol] = []
        for elem in body:
            if isinstance(elem, ChainSymbol):
                out.append(elem)
            else:
                # Sequitur stores non-terminals as `NT` instances; look
                # up rule body and recurse.
                rule_id = getattr(elem, "rule_id", None)
                if rule_id is None or rule_id not in all_rules:
                    raise ValueError(f"unexpected RHS element {elem!r}")
                out.extend(self._terminal_closure(all_rules[rule_id]))
        return out

    def lift(self, rule_id: int) -> RuleLift:
        """Look up the rule and produce its RuleLift."""
        all_rules = self.all_rules()
        if rule_id not in all_rules:
            raise KeyError(rule_id)
        body = all_rules[rule_id]
        closure = self._terminal_closure(body)
        lifted = chain_product(closure)
        return RuleLift(rule_id=rule_id, body=body,
                        terminal_closure=closure, lifted=lifted)

    def all_lifts(self) -> Dict[int, RuleLift]:
        return {rid: self.lift(rid) for rid in self.all_rules()}

    def stats(self) -> Dict[str, Any]:
        return {
            "n_rules": self.n_rules(),
            "n_nt_refs": self.underlying.n_nt_refs(),
        }


# --- Self-check ---------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    from pathlib import Path
    from eliza.chain_emitter import chain_stream

    HERE = Path(__file__).resolve().parent
    src = HERE / "engine.py"
    with open(src, "rb") as f:
        data = f.read()[:8192]

    chains = chain_stream(data, window_size=256)
    cs = ChainSequitur()
    cs.observe_stream(chains)

    n_rules = cs.n_rules()
    lifts = cs.all_lifts()

    # Verify each rule's lifted symbol equals the product of its
    # terminal closure (= recompute and compare).
    consistency_failures = 0
    for rid, lift in lifts.items():
        recomputed = chain_product(lift.terminal_closure)
        if recomputed != lift.lifted:
            consistency_failures += 1

    # Verify lifts are themselves ChainSymbols (round-trip via S₄).
    type_failures = 0
    for lift in lifts.values():
        if not isinstance(lift.lifted, ChainSymbol):
            type_failures += 1

    if verbose:
        print("=== ChainSequitur self-check ===")
        print(f"  windows observed:        {len(chains)}")
        print(f"  rules inferred:          {n_rules}")
        print(f"  lift consistency:        {consistency_failures} failures")
        print(f"  lift type-correctness:   {type_failures} failures")
        print(f"\n  sample lifts (up to 5):")
        for rid, lift in list(lifts.items())[:5]:
            print(f"    R{rid}: |body|={len(lift.body)}, "
                  f"|terminal_closure|={len(lift.terminal_closure)}, "
                  f"lift={lift.lifted}")
        ok = consistency_failures == 0 and type_failures == 0
        print(f"\nResult: {'OK' if ok else 'FAIL'}")
        return ok
    return consistency_failures == 0 and type_failures == 0


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
