"""Eliza.ChainEmitter — per-window ChainSymbol emission as a Brick.

Streams (window-sized byte slices) → stream of ChainSymbols. Each
window's walk folds into a single S₄ end-state; the chain
decomposition of that state is the emitted symbol.

This Brick witnesses D⇒D: pure transformation of input data to
output data (a different alphabet — ChainSymbol instead of bytes).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Iterator, List, Tuple

from eliza.brick import BrickType, Unit, UNIT, Witnessing
from eliza.chain_symbol import ChainSymbol
from eliza.walk_carrier import walk_to_s4


def emit_chain_for_window(window: bytes) -> ChainSymbol:
    """One window → one ChainSymbol."""
    return ChainSymbol.from_s4(walk_to_s4(window).state)


def emit_chains(data: bytes, window_size: int = 256) -> Iterator[ChainSymbol]:
    """Stream of ChainSymbols, one per window. The trailing partial
    window (if len(data) is not a multiple of window_size) is included."""
    for start in range(0, len(data), window_size):
        yield emit_chain_for_window(data[start:start + window_size])


def chain_stream(data: bytes, window_size: int = 256) -> List[ChainSymbol]:
    """Materialised list of per-window chains."""
    return list(emit_chains(data, window_size))


@dataclass
class ChainEmitter:
    """Brick wrapper around `emit_chain_for_window`.

    Step signature: bytes (one window) ⇒ ChainSymbol. Caller batches
    windows.
    """
    window_size: int = 256
    name: str = "chain_emitter"
    homomorphism_tag: str = "D⇒D: per-window walk → chain decomposition"

    @property
    def brick_type(self) -> BrickType:
        return BrickType(D_in=bytes, D_out=ChainSymbol, S_in=Unit, S_out=Unit)

    @property
    def witnesses(self) -> Witnessing:
        # Pure transform: state-trivial. The Lift convention uses D⇒S
        # for S=Unit; here we want D⇒D since both edges carry data.
        # The Brick.agda enum has no native D⇒D; use D_TO_S with Unit
        # to match the Lift convention.
        return Witnessing.D_TO_S

    def step(self, window: bytes, _: Any = None) -> Tuple[ChainSymbol, Unit]:
        return emit_chain_for_window(window), UNIT

    def stats(self) -> Dict[str, Any]:
        return {"window_size": self.window_size}


# --- Self-check ---------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    from pathlib import Path
    HERE = Path(__file__).resolve().parent
    src = HERE / "engine.py"
    with open(src, "rb") as f:
        data = f.read()[:2048]

    emitter = ChainEmitter(window_size=256)
    chains: List[ChainSymbol] = []
    for start in range(0, len(data), 256):
        window = data[start:start + 256]
        c, _ = emitter.step(window)
        chains.append(c)

    # Sanity: stream length matches expected window count.
    expected = (len(data) + 255) // 256
    ok_count = len(chains) == expected

    # Distribution: how many distinct chain symbols appear?
    distinct = len(set(chains))

    # Per-rotation comparison on the same input.
    from eliza.octonion import rotate_bytes
    per_rotation_chains: List[List[ChainSymbol]] = []
    for r in range(16):
        rotated = rotate_bytes(data, r)
        per_rotation_chains.append(chain_stream(rotated))
    rotation_streams_distinct = len({tuple(s) for s in per_rotation_chains})

    if verbose:
        print("=== ChainEmitter self-check ===")
        print(f"  windows emitted: {len(chains)} (expected {expected})  "
              f"{'OK' if ok_count else 'FAIL'}")
        print(f"  distinct chain symbols across stream: {distinct} / {len(chains)}")
        print(f"  16 rotations produce {rotation_streams_distinct} distinct chain streams")
        print(f"  first 5 chains:")
        for i, c in enumerate(chains[:5]):
            print(f"    [{i}] {c}")
        print(f"\nResult: {'OK' if ok_count else 'FAIL'}")
    return ok_count


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
