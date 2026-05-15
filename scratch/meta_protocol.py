"""
meta_protocol.py — declarative protocol for witnessed-pair operations.

Each operation declares (source, sink, witness). The framework mechanically
derives:
  - pair (unordered)        — which 2 axes interact
  - pairing (α, β, or γ)    — which V_4 structure applies
  - chirality (even/odd)    — sign of the S_4 permutation
  - v4_orbit_key            — pairing × chirality (one of 6 fundamental patterns)
  - inverse signature       — swap source↔sink (flips chirality)
  - v4-twin signatures      — apply V_4 swaps

This is the natural basis for the architecture (M34). The (held, enabled)
classification from M22-M31 was an awkward projection of this structure.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional, Tuple
from collections import defaultdict


# ============================================================
# Algebraic constants
# ============================================================

AXES = ('D', 'C', 'S', 'W')
AXIS_INDEX = {a: i for i, a in enumerate(AXES)}

PAIRINGS = {
    'α': (frozenset({'D', 'C'}), frozenset({'S', 'W'})),
    'β': (frozenset({'D', 'S'}), frozenset({'C', 'W'})),
    'γ': (frozenset({'D', 'W'}), frozenset({'C', 'S'})),
}

V4_SWAPS = {
    'e': {'D': 'D', 'C': 'C', 'S': 'S', 'W': 'W'},
    'α': {'D': 'C', 'C': 'D', 'S': 'W', 'W': 'S'},
    'β': {'D': 'S', 'S': 'D', 'C': 'W', 'W': 'C'},
    'γ': {'D': 'W', 'W': 'D', 'C': 'S', 'S': 'C'},
}


# ============================================================
# Derived structure
# ============================================================

def opposite_pair(source: str, sink: str) -> Tuple[frozenset, str]:
    """Find the V_4-opposite pair and which pairing puts {source, sink} together."""
    pair = frozenset({source, sink})
    for name, (p1, p2) in PAIRINGS.items():
        if pair == p1:
            return p2, name
        if pair == p2:
            return p1, name
    raise ValueError(f"Pair {pair} not in any V_4 pairing")


def sign_of_permutation(perm) -> int:
    """Sign of a permutation: 0 (even) or 1 (odd) by inversion count."""
    inversions = sum(
        1 for i in range(len(perm)) for j in range(i + 1, len(perm))
        if perm[i] > perm[j]
    )
    return inversions % 2


def chirality_of(source: str, sink: str, witness: str) -> str:
    """Chirality = sign of the S_4 permutation [source, sink, witness, fourth]."""
    fourth = next(a for a in AXES if a not in {source, sink, witness})
    perm = [AXIS_INDEX[a] for a in [source, sink, witness, fourth]]
    return 'even' if sign_of_permutation(perm) == 0 else 'odd'


def validate_signature(source: str, sink: str, witness: str) -> None:
    """Raise ValueError if (source, sink, witness) is not a valid signature."""
    if not all(a in AXES for a in (source, sink, witness)):
        raise ValueError(f"All of source, sink, witness must be in {AXES}")
    if len({source, sink, witness}) != 3:
        raise ValueError(
            f"source={source}, sink={sink}, witness={witness} must be distinct"
        )
    opp, _ = opposite_pair(source, sink)
    if witness not in opp:
        raise ValueError(
            f"witness {witness} must be in the opposite pair {set(opp)} "
            f"of {{source, sink}} = {{{source}, {sink}}}"
        )


# ============================================================
# The protocol: WitnessedOp
# ============================================================

@dataclass
class WitnessedOp:
    """A declarative operation with axis-engagement metadata.

    The (source, sink, witness) triple is the natural basis (M34).
    All derived properties (pair, pairing, chirality, etc.) are mechanical.
    """
    name: str
    source: str
    sink: str
    witness: str
    fn: Callable = field(repr=False)
    description: str = ""

    def __post_init__(self):
        validate_signature(self.source, self.sink, self.witness)

    # --- Derived structural properties ---

    @property
    def pair(self) -> frozenset:
        return frozenset({self.source, self.sink})

    @property
    def pairing(self) -> str:
        _, name = opposite_pair(self.source, self.sink)
        return name

    @property
    def chirality(self) -> str:
        return chirality_of(self.source, self.sink, self.witness)

    @property
    def v4_orbit_key(self) -> Tuple[str, str]:
        """The V_4-orbit is (pairing, chirality) — one of 6 fundamental patterns."""
        return (self.pairing, self.chirality)

    @property
    def signature(self) -> Tuple[str, str, str]:
        return (self.source, self.sink, self.witness)

    # --- Group action ---

    def invert_signature(self) -> Tuple[str, str, str]:
        """Inverse swaps source↔sink. The witness stays. Chirality flips."""
        return (self.sink, self.source, self.witness)

    def v4_rotate_signature(self, swap_name: str) -> Tuple[str, str, str]:
        """Apply a V_4 swap to (source, sink, witness) componentwise."""
        if swap_name not in V4_SWAPS:
            raise ValueError(f"Unknown swap: {swap_name}")
        swap = V4_SWAPS[swap_name]
        return (swap[self.source], swap[self.sink], swap[self.witness])

    # --- Execution ---

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


# ============================================================
# Registry
# ============================================================

class OperationRegistry:
    """Registry indexed by both name and (source, sink, witness) signature."""

    def __init__(self):
        self._by_name: dict = {}
        self._by_signature: dict = {}  # signature -> list of ops

    def register(self, op: WitnessedOp) -> None:
        if op.name in self._by_name:
            raise ValueError(f"Operation {op.name} already registered")
        self._by_name[op.name] = op
        sig = op.signature
        if sig not in self._by_signature:
            self._by_signature[sig] = []
        self._by_signature[sig].append(op)

    def get(self, name: str) -> Optional[WitnessedOp]:
        return self._by_name.get(name)

    def at_signature(self, source: str, sink: str, witness: str):
        """All ops with the given signature."""
        return list(self._by_signature.get((source, sink, witness), []))

    def find_inverse(self, op: WitnessedOp):
        """Find registered operations with the inverse signature."""
        return self.at_signature(*op.invert_signature())

    def find_v4_twins(self, op: WitnessedOp):
        """Find V_4-twin operations for each non-identity swap."""
        twins = {}
        for swap_name in ('α', 'β', 'γ'):
            twin_sig = op.v4_rotate_signature(swap_name)
            if twin_sig == op.signature:
                continue  # self-fixed under this swap
            found = self.at_signature(*twin_sig)
            if found:
                twins[swap_name] = found
        return twins

    def operations_in_orbit(self, pairing: str, chirality: str):
        """All ops in a given (pairing, chirality) V_4-orbit."""
        return [
            op for op in self._by_name.values()
            if op.pairing == pairing and op.chirality == chirality
        ]

    def coverage_report(self) -> dict:
        """For each of the 6 V_4-orbits, count populated operations."""
        report = {}
        for pairing in ('α', 'β', 'γ'):
            for chirality in ('even', 'odd'):
                report[(pairing, chirality)] = len(
                    self.operations_in_orbit(pairing, chirality)
                )
        return report

    def all(self):
        return list(self._by_name.values())

    def __len__(self):
        return len(self._by_name)


# ============================================================
# The 6 fundamental patterns — semantic names
# ============================================================

PATTERN_NAMES = {
    ('α', 'even'): 'apply / reduce (state witnesses)',
    ('α', 'odd'):  'memoized apply (workspace witnesses)',
    ('β', 'even'): 'workspace-receipted state change',
    ('β', 'odd'):  'compute-validated state change',
    ('γ', 'even'): 'compute-validated store',
    ('γ', 'odd'):  'logged store (state witnesses)',
}


def pattern_name(pairing: str, chirality: str) -> str:
    return PATTERN_NAMES.get((pairing, chirality), 'unnamed')


if __name__ == "__main__":
    # Quick sanity check
    print("Meta-protocol sanity check:")
    print()
    for pairing in ('α', 'β', 'γ'):
        for chirality in ('even', 'odd'):
            print(f"  ({pairing}, {chirality}): {PATTERN_NAMES[(pairing, chirality)]}")
    print()
    print("Constructing test WitnessedOp:")
    op = WitnessedOp(
        name='test_apply',
        source='D', sink='C', witness='S',
        fn=lambda x: x,
        description='test',
    )
    print(f"  name: {op.name}")
    print(f"  pair: {set(op.pair)}")
    print(f"  pairing: {op.pairing}")
    print(f"  chirality: {op.chirality}")
    print(f"  v4_orbit_key: {op.v4_orbit_key}")
    print(f"  inverse signature: {op.invert_signature()}")
    print(f"  α-swap signature: {op.v4_rotate_signature('α')}")
