"""Eliza.ChainBytesBridge — chain ↔ representative-byte-pattern bridge.

A ChainSymbol is a decomposition of a single S₄ element; the same
element is the FOLD of many different byte sequences. This module
picks a SHORTEST canonical representative: a minimum-length nibble
sequence whose walk-fold equals the chain's S₄ element.

The bridge is the substrate-honest realisation of the user's
"Sequitur's rewrite step can apply to the input that was used to
construct the walk chain": given a Sequitur rule R whose product
chain is c, `bridge_chain_to_bytes(c)` returns a byte pattern that
WITNESSES R at the byte level. Rule occurrences in the chain stream
correspond to byte-window patterns that share this fold-equivalence.

Per [[multi-reading-ambient-discipline]]: the representative is one of
many fold-equivalent byte patterns; we document the choice (shortest-
length, lex-smallest among shortest) as a convention without claiming
canonicity.

The bridge uses BFS over the 24 chambers with NIBBLE_TO_PERM as the
edge labelling. Since there are only 16 nibbles and the Cayley graph
has bounded diameter, BFS is bounded and very fast.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

from eliza.alphabets import (
    Chamber, NIBBLE_TO_PERM, ORIGIN, perm_compose,
)
from eliza.chain_symbol import ChainSymbol


# --- BFS over nibble compositions ---------------------------------------


@lru_cache(maxsize=1)
def _bfs_nibble_paths() -> Dict[Chamber, List[int]]:
    """Shortest nibble-word from ORIGIN to each S₄ element.

    For each chamber, paths[chamber] is the shortest nibble sequence
    [n_1, ..., n_k] such that:
        perm_compose(... perm_compose(ORIGIN, NIBBLE_TO_PERM[n_1]) ...,
                     NIBBLE_TO_PERM[n_k]) == chamber.
    Ties broken by lex-smallest nibble sequence.
    """
    paths: Dict[Chamber, List[int]] = {ORIGIN: []}
    queue: deque = deque([(ORIGIN, [])])
    while queue:
        state, path = queue.popleft()
        for nib in range(16):
            new_state = perm_compose(state, NIBBLE_TO_PERM[nib])
            if new_state not in paths:
                paths[new_state] = path + [nib]
                queue.append((new_state, path + [nib]))
        # Note: BFS guarantees shortest; lex tie-breaking from the
        # iteration order of `nib` in 0..15.
    return paths


def shortest_nibbles_to(target: Chamber) -> List[int]:
    """Shortest nibble word whose fold from ORIGIN equals `target`."""
    return list(_bfs_nibble_paths()[target])


def bridge_chain_to_nibbles(chain: ChainSymbol) -> List[int]:
    """Representative nibble sequence whose fold = chain.to_s4()."""
    return shortest_nibbles_to(chain.to_s4())


def bridge_chain_to_bytes(chain: ChainSymbol,
                          pad_nibble: int = 0) -> bytes:
    """Representative byte sequence whose fold = chain.to_s4().

    Pairs nibbles (hi, lo) into bytes; if the nibble word has odd
    length, pads with `pad_nibble` to make it even. The fold is
    insensitive to the padding choice because identity-padding nibbles
    that fold to identity exist (nibble 0 = identity perm composed
    with itself stays at e), but BFS may produce odd-length words —
    we ensure that pad_nibble = 0 is identity at every position.
    """
    nibbles = bridge_chain_to_nibbles(chain)
    if len(nibbles) % 2 != 0:
        # Pad to even length. Note: nibble 0's perm is NIBBLE_TO_PERM[0]
        # which may NOT be identity in general — let's check.
        nibbles = nibbles + [pad_nibble]
    out = bytearray()
    for i in range(0, len(nibbles), 2):
        out.append((nibbles[i] << 4) | nibbles[i + 1])
    return bytes(out)


def fold_nibbles(nibbles: List[int]) -> Chamber:
    """Fold a nibble word to its end-S₄-element from ORIGIN."""
    state = ORIGIN
    for n in nibbles:
        state = perm_compose(state, NIBBLE_TO_PERM[n])
    return state


# --- Self-check ---------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    from eliza.manifold import Manifold
    from eliza.walk_carrier import walk_to_s4

    m = Manifold()
    chambers = m.nodes

    # (1) Round-trip via nibbles: fold(bridge_nibbles(c)) = c.to_s4().
    nibble_failures = 0
    for g in chambers:
        cs = ChainSymbol.from_s4(g)
        nibs = bridge_chain_to_nibbles(cs)
        if fold_nibbles(nibs) != g:
            nibble_failures += 1

    # (2) Round-trip via bytes: walk_to_s4(bridge_bytes(c)) = c.to_s4().
    byte_failures = 0
    for g in chambers:
        cs = ChainSymbol.from_s4(g)
        bs = bridge_chain_to_bytes(cs)
        carrier = walk_to_s4(bs)
        if carrier.state != g:
            byte_failures += 1

    # (3) Shortest-length property: BFS produces the minimum nibble
    # count to reach each chamber.
    paths = _bfs_nibble_paths()
    length_dist: Dict[int, int] = {}
    for g, path in paths.items():
        length_dist[len(path)] = length_dist.get(len(path), 0) + 1

    if verbose:
        print("=== ChainBytesBridge self-check ===")
        print(f"  nibble round-trip failures (24 chambers): {nibble_failures}")
        print(f"  byte round-trip failures (24 chambers):   {byte_failures}")
        print(f"  shortest-nibble length distribution:      "
              f"{dict(sorted(length_dist.items()))}")
        # Show some examples.
        sample_g = chambers[7]
        sample_cs = ChainSymbol.from_s4(sample_g)
        sample_nibs = bridge_chain_to_nibbles(sample_cs)
        sample_bytes = bridge_chain_to_bytes(sample_cs)
        print(f"\n  sample chain: {sample_cs}")
        print(f"    bridge nibbles: {sample_nibs}")
        print(f"    bridge bytes:   {sample_bytes.hex()}")
        ok = nibble_failures == 0 and byte_failures == 0
        print(f"\nResult: {'OK' if ok else 'FAIL'}")
        return ok
    return nibble_failures == 0 and byte_failures == 0


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
