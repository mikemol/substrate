"""Eliza.MultiLevelChainSequitur — recursive grammar inference over
ChainSymbols.

Level 0:  observe per-window ChainSymbols → ChainSequitur → rules.
Level 1:  each rule lifts to one ChainSymbol (its terminal-closure
          product). Rewrite the level-0 stream by replacing each rule
          OCCURRENCE with its lifted symbol. The rewritten stream is
          level-1 input → ChainSequitur over those.
Level 2+: repeat ad libitum.

This implements the user's "Sequitur's rewrite step can apply to the
input that was used to construct the walk chain" directive: rules at
each level rewrite the input at that level, and the lift carries the
chain content to the next level. Same alphabet at every level
(ChainSymbol), so the recursion is endogenous.

Per [[homology-cohomology-recursion]]: each pass alternates
observation (homology) ↔ cataloguing (cohomology). The product chain
is the homology↔cohomology bridge — the rule (cohomology) lifts to a
chain symbol (next-level homology).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from eliza.chain_sequitur import ChainSequitur, RuleLift
from eliza.chain_symbol import ChainSymbol


@dataclass
class Level:
    """One layer of the recursive grammar."""
    index: int                              # 0, 1, 2, ...
    input_stream: List[ChainSymbol]         # what this level observed
    sequitur: ChainSequitur
    lifts: Dict[int, RuleLift] = field(default_factory=dict)

    def n_rules(self) -> int:
        return self.sequitur.n_rules()

    def stats(self) -> Dict[str, Any]:
        return {
            "level": self.index,
            "input_length": len(self.input_stream),
            "n_rules": self.n_rules(),
            "distinct_symbols": len(set(self.input_stream)),
        }


def _rewrite_with_lifts(
    stream: List[ChainSymbol], lifts: Dict[int, RuleLift],
    skip_top_rule_id: int = 0,
) -> List[ChainSymbol]:
    """Greedy non-overlapping rewrite: find each rule's terminal-closure
    pattern in `stream` and replace occurrences with the lifted symbol.

    The greedy strategy: try LONGER rules first (longer closure = more
    informative). For each pattern, scan left-to-right and replace
    every non-overlapping occurrence.

    `skip_top_rule_id` excludes Sequitur's start rule (R0) from the
    rewrite pool: R0's body IS the whole stream, so rewriting against
    it would collapse the stream to one element — uninformative for
    recursive inference.

    This produces the level-i+1 input from level-i observations.
    """
    # Sort lifts by terminal-closure length, longest first; exclude
    # the start rule.
    candidate_lifts = [l for rid, l in lifts.items() if rid != skip_top_rule_id]
    sorted_lifts = sorted(
        candidate_lifts,
        key=lambda l: len(l.terminal_closure),
        reverse=True,
    )
    result = list(stream)
    for lift in sorted_lifts:
        pattern = lift.terminal_closure
        if not pattern:
            continue
        # Scan and replace non-overlapping occurrences.
        new_result: List[ChainSymbol] = []
        i = 0
        plen = len(pattern)
        while i < len(result):
            if (i + plen <= len(result)
                    and result[i:i + plen] == pattern):
                new_result.append(lift.lifted)
                i += plen
            else:
                new_result.append(result[i])
                i += 1
        result = new_result
    return result


@dataclass
class MultiLevelChainSequitur:
    """Recursive grammar: each level rewrites the stream with its rules
    and feeds the result to the next level.

    `levels` is the list of completed layers; `max_levels` caps the
    recursion depth. Recursion terminates early if a level produces
    no new rules or if the stream stops changing.
    """
    levels: List[Level] = field(default_factory=list)
    max_levels: int = 5

    @classmethod
    def from_stream(cls, stream: List[ChainSymbol],
                    max_levels: int = 5) -> "MultiLevelChainSequitur":
        m = cls(max_levels=max_levels)
        m.run(stream)
        return m

    def run(self, stream: List[ChainSymbol]) -> None:
        current = list(stream)
        for i in range(self.max_levels):
            seq = ChainSequitur()
            seq.observe_stream(current)
            lifts = seq.all_lifts()
            level = Level(
                index=i,
                input_stream=list(current),
                sequitur=seq,
                lifts=lifts,
            )
            self.levels.append(level)
            # Termination conditions.
            if not lifts:
                break
            rewritten = _rewrite_with_lifts(current, lifts)
            if rewritten == current:
                break
            current = rewritten

    def all_stats(self) -> List[Dict[str, Any]]:
        return [lv.stats() for lv in self.levels]

    def lifts_per_level(self) -> Dict[int, Dict[int, RuleLift]]:
        return {lv.index: lv.lifts for lv in self.levels}


# --- Self-check ---------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    from pathlib import Path
    from eliza.chain_emitter import chain_stream

    HERE = Path(__file__).resolve().parent
    src = HERE / "engine.py"
    with open(src, "rb") as f:
        data = f.read()
    while len(data) < 65536:
        data = data + data
    data = data[:65536]

    stream = chain_stream(data, window_size=256)
    ml = MultiLevelChainSequitur.from_stream(stream, max_levels=5)

    # Verify: each level's stream is non-longer than the previous (after
    # at least one rule applied) — the rewrite contracts.
    contraction_ok = True
    for prev, cur in zip(ml.levels, ml.levels[1:]):
        if len(cur.input_stream) > len(prev.input_stream):
            contraction_ok = False

    # Verify: each level's lifts are well-formed ChainSymbols.
    type_failures = 0
    for lv in ml.levels:
        for lift in lv.lifts.values():
            if not isinstance(lift.lifted, ChainSymbol):
                type_failures += 1

    if verbose:
        print("=== MultiLevelChainSequitur self-check ===")
        for s in ml.all_stats():
            print(f"  L{s['level']}: input_len={s['input_length']:>5}, "
                  f"distinct={s['distinct_symbols']:>3}, "
                  f"n_rules={s['n_rules']}")
        print(f"\n  contraction (level i+1 ≤ level i): "
              f"{'OK' if contraction_ok else 'FAIL'}")
        print(f"  lift type-correctness: {type_failures} failures")
        ok = contraction_ok and type_failures == 0
        print(f"\nResult: {'OK' if ok else 'FAIL'}")
        return ok
    return contraction_ok and type_failures == 0


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
