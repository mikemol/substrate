"""Eliza.RuleAction — algebraic action on rule expansions.

U-arc shadow: every emission of a rule reference carries a
`RuleAction` describing how to transform the rule's expansion before
appending it to the chain.

A = V₄ × AffineProjection × F₂Patch × SpanCoupling

U1 implements only V₄ (existing sequitur residue lifted into the
codec lineage). Later slices enlarge A:

  U2 + U3 — AffineProjection := (start_phase, length_mask).
            Subsumes LZ77 as an affine restriction on rule expansion.
  U4 + U5 — F₂Patch := sparse F₂ correction vector at sparsity ≤ K.
            Subsumes fuzzy match via Hodge-bivector flip pattern.
  U6 + U7 — SpanCoupling := (rule_right, overlap_mask) — bifibrational,
            non-commutative; subsumes B-frame bidirectional reference.

The action is composable; A is a monoid (the four factors compose
componentwise; SpanCoupling is non-commutative — H-rung). At identity
the action reduces to V5 behaviour exactly.
"""

from __future__ import annotations

from dataclasses import dataclass


# V₄ ≅ Z/2 × Z/2 composition table, identical to sequitur.py:29-34.
# Re-stated here so rule_action is self-contained.
_V4_COMPOSE = {
    ("e", "e"): "e", ("e", "α"): "α", ("e", "β"): "β", ("e", "γ"): "γ",
    ("α", "e"): "α", ("α", "α"): "e", ("α", "β"): "γ", ("α", "γ"): "β",
    ("β", "e"): "β", ("β", "α"): "γ", ("β", "β"): "e", ("β", "γ"): "α",
    ("γ", "e"): "γ", ("γ", "α"): "β", ("γ", "β"): "α", ("γ", "γ"): "e",
}

V4_RESIDUES = ("e", "α", "β", "γ")
V4_IDENTITY = "e"


@dataclass(frozen=True)
class RuleAction:
    """An action `a ∈ A` to apply when expanding a rule reference.

    Components are introduced slice by slice; defaults reproduce the
    identity action (= V5 behaviour).

      residue        — V₄ rotation tag ∈ {e, α, β, γ}.   (U1)
      start_phase    — affine translation in rule expansion.  (U2)
      length_mask    — affine truncation; -1 means "full body".  (U3)
      f2_patch       — sparse F₂ flip indices.  (U4+U5)
      span_coupling  — optional (rule_right, overlap_mask) tuple.  (U6+U7)

    Identity action: RuleAction() — residue=e, no projection, no patch,
    no coupling.
    """

    residue: str = V4_IDENTITY
    start_phase: int = 0
    length_mask: int = -1
    f2_patch: tuple = ()             # tuple of int indices (sparse F₂)
    span_coupling: tuple = ()        # () or (rule_right_id, overlap_mask)

    def is_identity(self) -> bool:
        return (self.residue == V4_IDENTITY
                and self.start_phase == 0
                and self.length_mask == -1
                and self.f2_patch == ()
                and self.span_coupling == ())


IDENTITY = RuleAction()


def compose_v4(left: str, right: str) -> str:
    """Compose two V₄ residue tags."""
    return _V4_COMPOSE[(left, right)]


def compose(a: "RuleAction", b: "RuleAction") -> "RuleAction":
    """Compose two actions: `(a ∘ b)` applied to a rule equals `a`
    applied to (b applied to the rule's expansion).

    U1 only composes the V₄ factor; other factors will gain their
    own composition rules as they land.
    """
    return RuleAction(
        residue=compose_v4(a.residue, b.residue),
        start_phase=a.start_phase + b.start_phase,
        length_mask=a.length_mask if a.length_mask != -1 else b.length_mask,
        f2_patch=tuple(sorted(set(a.f2_patch) ^ set(b.f2_patch))),
        span_coupling=a.span_coupling or b.span_coupling,
    )


# --- V₄ application on chain-symbol bodies ----------------------------
# U1: identity-only stub. Non-identity application becomes load-bearing
# starting at U2 when the encoder actually emits non-trivial residues.


def apply_to_body(body, action: RuleAction):
    """Apply an action to a chain-symbol body (sequence of S₄ indices).

    U2: handles `start_phase` (slice body from phase). Other non-identity
    factors raise NotImplementedError until their slice lands; this is
    the annealing guard.
    """
    if action.is_identity():
        return body
    # U2: start_phase slicing. U3: length_mask truncation.
    sliced = body
    if action.start_phase > 0:
        sliced = sliced[action.start_phase:]
    if action.length_mask != -1:
        sliced = sliced[:action.length_mask]
    # U4+: f2_patch, span_coupling land here in turn.
    if action.f2_patch:
        raise NotImplementedError("f2_patch: U4/U5")
    if action.span_coupling:
        raise NotImplementedError("span_coupling: U6/U7")
    # V₄ residue application also deferred — U-arc currently emits
    # residue='e' only; this slot lands when speculation surfaces a
    # V₄-tagged match. (Today V5/V6 sequitur canonicalisation is off.)
    return sliced
