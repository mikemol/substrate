"""Eliza.ChainSymbol — hashable wrapper around a SylowChain for use as
a Sequitur terminal symbol.

Per the user's directive: Sequitur should infer grammar over the walk
chains, with each per-window chain as a single symbol. Sequitur takes
arbitrary terminals; ChainSymbol packages the (v, s3, s2) triple as a
frozen, hashable, comparable object that participates in Sequitur's
digram-uniqueness machinery cleanly.

The PRODUCT operation is the lift to a next-level symbol: given a
sequence of ChainSymbols [a, b, c, ...], their composed S₄ element
has its own chain decomposition, which is itself a ChainSymbol. This
is what makes the grammar recursively inferred: Sequitur rules at
level i lift to ChainSymbols at level i+1.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from eliza.alphabets import Chamber, ORIGIN, perm_compose
from eliza.sylow_chain import SylowChain, build_chain


@dataclass(frozen=True, order=True)
class ChainSymbol:
    """A SylowChain wrapped as a Sequitur terminal symbol.

    Stored fields exactly recover the SylowChain triple. Hashability
    follows from the frozen dataclass + tuple-of-tuples representation
    of chamber values.

    Per [[ordering-is-chirality-choice]]: the field ordering (v, s3, s2)
    is the substrate's chirality convention; downstream consumers see
    the SAME ordering throughout.
    """
    v: Chamber                 # V₄ element
    s3: Chamber                # Sylow-3 element
    s2: Chamber                # Sylow-2-coset element

    @classmethod
    def from_chain(cls, chain: SylowChain) -> "ChainSymbol":
        return cls(v=chain.v, s3=chain.s3, s2=chain.s2)

    @classmethod
    def from_s4(cls, g: Chamber) -> "ChainSymbol":
        return cls.from_chain(build_chain(g))

    @classmethod
    def identity(cls) -> "ChainSymbol":
        return cls.from_s4(ORIGIN)

    def as_chain(self) -> SylowChain:
        return SylowChain(v=self.v, s3=self.s3, s2=self.s2)

    def to_s4(self) -> Chamber:
        """The single S₄ element this chain decomposes."""
        return self.as_chain().reconstruct()

    @property
    def word_length(self) -> int:
        return self.as_chain().word_length

    def __mul__(self, other: "ChainSymbol") -> "ChainSymbol":
        """Product: compose the S₄ elements and re-extract a ChainSymbol.

        This is the LIFT operation — sequences of ChainSymbols
        compose into a single ChainSymbol at the next level.
        """
        return ChainSymbol.from_s4(perm_compose(self.to_s4(), other.to_s4()))

    def __repr__(self) -> str:
        return f"χ(v={self.v}, s3={self.s3}, s2={self.s2}, |w|={self.word_length})"


def product(symbols: Iterable[ChainSymbol]) -> ChainSymbol:
    """The S₄-product of a sequence of ChainSymbols, re-chained.

    sequence [a, b, c, ...] → ChainSymbol of (a.s₄ · b.s₄ · c.s₄ · ...).
    Empty sequence → identity.
    """
    acc = ORIGIN
    for s in symbols:
        acc = perm_compose(acc, s.to_s4())
    return ChainSymbol.from_s4(acc)


# --- Self-check ---------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    from eliza.manifold import Manifold
    m = Manifold()
    chambers = m.nodes
    # (1) Round-trip every S₄ element through ChainSymbol.
    for g in chambers:
        cs = ChainSymbol.from_s4(g)
        assert cs.to_s4() == g, f"round-trip failed for {g}: -> {cs.to_s4()}"
    # (2) Hashability — symbols are usable as dict keys.
    table = {ChainSymbol.from_s4(g): g for g in chambers}
    assert len(table) == 24, f"hash collisions: only {len(table)} unique"
    # (3) Product associativity (algebraic; should be S₄-inherited).
    a, b, c = (ChainSymbol.from_s4(chambers[1]),
               ChainSymbol.from_s4(chambers[5]),
               ChainSymbol.from_s4(chambers[11]))
    left = (a * b) * c
    right = a * (b * c)
    assert left == right, f"associativity failed: {left} vs {right}"
    # (4) Identity behaviour.
    e = ChainSymbol.identity()
    assert (a * e) == a and (e * a) == a, "identity acts trivially"
    # (5) product([]) = identity, product([x]) = x.
    assert product([]) == e
    assert product([a]) == a
    assert product([a, b]) == a * b

    if verbose:
        print("=== ChainSymbol self-check ===")
        print(f"  24 S₄ elements round-trip through ChainSymbol     OK")
        print(f"  hashability: {len(table)} unique keys              OK")
        print(f"  (a·b)·c == a·(b·c) for sampled symbols             OK")
        print(f"  identity behaviour                                  OK")
        print(f"  product([]) == identity; product([a, b]) == a·b   OK")
        print(f"\n  sample symbol: {a}")
        print(f"  a * b = {a * b}")
        print(f"\nResult: OK")
    return True


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
