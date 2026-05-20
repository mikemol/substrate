"""Eliza.OpcodeSet — substrate-native opcodes for pre-seeded ChainSequitur.

Per the user's framing: each grammar rule IS an opcode. Pre-populating
ChainSequitur with structural opcodes (the substrate's known gauge
generators + their common compositions) gives the codec an INSTRUCTION
SET to encode against — instead of inferring all rules from scratch.

The opcode set is organised by gauge layer:
  * I_NOP                — identity transition (no-op)
  * V4_α / V4_β / V4_γ   — the three V₄ involutions
  * SYLOW3_123 / SYLOW3_132 — the two 3-cycles
  * S3_SYLOW2_12         — the (1 2) transposition
  * 16 NIBBLE_n          — the 16 nibble-perms (the per-nibble transitions)
  * COMMON_*             — frequent compositions discovered empirically
                          (e.g., αβ = γ, 3-cycle·transposition = ...)

Plus exploding-bitmap rules:
  * REP_IDENTITY_k      — k consecutive identity transitions
  * REP_ALPHA_k         — k consecutive V₄_α applications
  * (etc; populated as discovered useful patterns)

The opcode set is a STARTER GRAMMAR injected into ChainSequitur before
input observation. Sequitur extends it with composite opcodes during
inference; the substrate-native opcodes remain as low-numbered rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from eliza.alphabets import (
    Chamber, NIBBLE_TO_PERM, ORIGIN, perm_compose,
)
from eliza.chain_symbol import ChainSymbol
from eliza.sylow_chain import (
    V4_α, V4_β, V4_γ, V4_E, V4_ELEMENTS,
    S3_E, S3_12, S3_23, S3_13, S3_123, S3_132,
    SYLOW3_GENERATOR, S3_SYLOW2_GENERATOR,
)


# --- Opcode definition --------------------------------------------------


@dataclass(frozen=True)
class Opcode:
    """One substrate-native opcode = a chain transition.

    body: a sequence of ChainSymbols whose product = the opcode's effect.
    The opcode represents the rule body; its "lifted" effect is the
    product of its body symbols.
    """
    name: str
    body: Tuple[ChainSymbol, ...]
    category: str = "generic"      # "I" | "V4" | "Sylow3" | "S3-Sylow2" | "nibble" | "exploding-bitmap" | "composite"

    @property
    def length(self) -> int:
        return len(self.body)

    def __repr__(self) -> str:
        return f"Opcode({self.name}, |b|={self.length}, cat={self.category})"


# --- The substrate-native opcode set -----------------------------------


def _identity_chain() -> ChainSymbol:
    return ChainSymbol.from_s4(ORIGIN)


def _chain(g: Chamber) -> ChainSymbol:
    return ChainSymbol.from_s4(g)


def _nibble_chain(n: int) -> ChainSymbol:
    """Chain produced by one nibble transition from ORIGIN."""
    return ChainSymbol.from_s4(perm_compose(ORIGIN, NIBBLE_TO_PERM[n]))


def build_default_opcodes() -> List[Opcode]:
    """The default substrate-native opcode set.

    Body lengths ≥ 2 (Sequitur rules have body ≥ 2 by construction).
    Length-1 "opcodes" wouldn't be rules — they're terminals.

    The opcodes here are 2-symbol patterns where ONE of the symbols is
    a structurally-meaningful generator. Sequitur creates new rules from
    repeated digrams; pre-seeding with these means digrams involving
    these generators get encoded compactly from the start.
    """
    e = _identity_chain()
    α = _chain(V4_α)
    β = _chain(V4_β)
    γ = _chain(V4_γ)
    c3 = _chain(S3_123)
    c3_inv = _chain(S3_132)
    s2 = _chain(S3_12)

    ops: List[Opcode] = []

    # I-frame "identity-doubling": repeat identity transitions.
    ops.append(Opcode("I_NOP_x2", (e, e), category="I"))

    # V₄ doublings (V₄ elements are involutions; doubling = identity).
    ops.append(Opcode("V4_alpha_x2", (α, α), category="V4"))
    ops.append(Opcode("V4_beta_x2", (β, β), category="V4"))
    ops.append(Opcode("V4_gamma_x2", (γ, γ), category="V4"))

    # V₄ composition: αβ = γ; βα = γ (V₄ is abelian).
    ops.append(Opcode("V4_alpha_beta", (α, β), category="V4"))
    ops.append(Opcode("V4_beta_alpha", (β, α), category="V4"))

    # Sylow-3 cycle (order 3): cycle then inverse-cycle = identity.
    ops.append(Opcode("Sylow3_fwd_then_inv", (c3, c3_inv), category="Sylow3"))
    ops.append(Opcode("Sylow3_squared", (c3, c3), category="Sylow3"))

    # S₃-Sylow-2 doubling (involution).
    ops.append(Opcode("S3_S2_x2", (s2, s2), category="S3-Sylow2"))

    # Cross-Sylow composition: V₄ × Sylow-3.
    ops.append(Opcode("V4a_Sylow3", (α, c3), category="composite"))
    ops.append(Opcode("Sylow3_V4a", (c3, α), category="composite"))

    return ops


# --- Exploding-bitmap opcodes (length > 2) -----------------------------


def build_exploding_bitmap_opcodes() -> List[Opcode]:
    """Long-body opcodes for high-redundancy patterns.

    Each opcode body is N copies of a base chain. A single rule reference
    to such an opcode UNFOLDS to N chains — the "exploding bitmap"
    pattern: one symbol covers many.

    Pre-populating these means that highly redundant input (e.g., zeros
    or all-identical bytes) compresses to a small constant number of
    opcode references regardless of stream length.
    """
    e = _identity_chain()
    α = _chain(V4_α)
    γ = _chain(V4_γ)

    ops: List[Opcode] = []
    for k in (4, 8, 16, 32, 64):
        ops.append(Opcode(f"EXPLODE_I_x{k}", tuple([e] * k),
                          category="exploding-bitmap"))
        ops.append(Opcode(f"EXPLODE_ALPHA_x{k}", tuple([α] * k),
                          category="exploding-bitmap"))
    return ops


# --- Convenience: combined set --------------------------------------


def build_full_opcode_set() -> List[Opcode]:
    """Default opcodes + exploding-bitmap opcodes."""
    return build_default_opcodes() + build_exploding_bitmap_opcodes()


# --- Cost-estimator: bits to encode a chain via an opcode ------------


def opcode_match(opcode: Opcode, stream: List[ChainSymbol], start: int) -> bool:
    """Does the stream starting at `start` match the opcode's body
    symbol-for-symbol?"""
    if start + opcode.length > len(stream):
        return False
    return tuple(stream[start:start + opcode.length]) == opcode.body


# --- Self-check --------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    defaults = build_default_opcodes()
    explodings = build_exploding_bitmap_opcodes()
    full = build_full_opcode_set()

    # All opcodes must have non-empty bodies.
    empty_bodies = [op for op in full if op.length < 2]

    # Names are unique.
    names = [op.name for op in full]
    name_dup = len(names) != len(set(names))

    # By category breakdown.
    cats: Dict[str, int] = {}
    for op in full:
        cats[op.category] = cats.get(op.category, 0) + 1

    if verbose:
        print("=== OpcodeSet self-check ===")
        print(f"  default opcodes:       {len(defaults)}")
        print(f"  exploding-bitmap ops:  {len(explodings)}")
        print(f"  full set:              {len(full)}")
        print(f"  category breakdown:    {cats}")
        print(f"  empty bodies:          {len(empty_bodies)}")
        print(f"  duplicate names:       {'YES' if name_dup else 'NO'}")
        print(f"\n  default ops:")
        for op in defaults:
            print(f"    {op.name:>22}  body length {op.length}  cat={op.category}")
        ok = len(empty_bodies) == 0 and not name_dup
        print(f"\nResult: {'OK' if ok else 'FAIL'}")
        return ok
    return len(empty_bodies) == 0 and not name_dup


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
