{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.DiagonalDoF — ⟡diagonal-interactive-model: the PRECISE
-- invariant of the escape is NOT "agency" (a vague, one-system, metaphysical property — does it
-- "choose"?) but DEGREES OF FREEDOM (a relational, quantitative one — obs vs adv). The observer
-- escapes iff it has strictly MORE degrees of freedom than the adversary: enough to EMBED the
-- adversary (or CONTAIN ITS EFFECTS) with FLEXIBILITY REMAINING (residual dof > 0 ⟹ strict >).
--
-- This IS Cantor's theorem operationalized: |A| < |P A|, ALWAYS strict (cantor, below). The
-- answer space (A → Bool = P A) has strictly more dof than A. The DIAGONAL ELEMENT that escapes
-- a COMMITTED observer (confined to A, or to the image of f : A → P A) is a NATIVE STATE of a
-- PLURAL observer (dwelling in P A). Same Cantor fact, two readings: on the SMALL side you are
-- escaped (the diagonal element is outside your reach); on the LARGE side you cannot be covered
-- (the adversary can't surject onto you) and the escaping element is one of YOUR OWN states.
--
-- "One step ahead" (221) = one POWERSET LEVEL up = strictly more dof, ALWAYS available against a
-- FIXED adversary (Cantor: P A is always strictly bigger). Supersedes both "agency" (my quoted
-- framing) and "closed-vs-interactive" (222's) with the precise quantitative invariant: dof(obs)
-- > dof(adv). "Agency" was a proxy for "excess dof"; the real thing is the strict inequality.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.DiagonalDoF where

-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content of this module is
-- EXACTLY: not-fixed-point-free, cantor, diagonal-native. Everything else in these comments — 'not agency but degrees of freedom', 'the escape is the dof inequality', 'be on the large side' — is (prose:
-- illuminating framing, NOT a theorem of this slice; not enforced by the typechecker).
-- Promoting the framing to a theorem would require the formal identification of the dof inequality with the diagonal's defeat (⟡diagonal-lawvere-coalg).

open import Substrate.Foundation.Bool using (Bool; true; false; not)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; cong)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Product using (Σ; _,_)

------------------------------------------------------------------------
-- ① THE LEVER (221): the diagonal endomap `not` is fixed-point-free on the COMMITTED object.
------------------------------------------------------------------------
not-fixed-point-free : (b : Bool) → ¬ (not b ≡ b)
not-fixed-point-free true  ()
not-fixed-point-free false ()

------------------------------------------------------------------------
-- ② CANTOR = THE DOF INEQUALITY: NO map f : A → (A → Bool) is surjective — the answer space
--    (A → Bool = P A) has strictly MORE degrees of freedom than A. The witness is the DIAGONAL
--    element (λ a → not (f a a)), which no point of A maps to: it lives in the excess dof.
--    This is the precise, checkable content of "the observer needs more dof than the adversary".
------------------------------------------------------------------------
cantor : {A : Set} (f : A → (A → Bool)) → Σ (A → Bool) (λ g → (a : A) → ¬ (f a ≡ g))
cantor {A} f = diag , contra
  where
    diag : A → Bool
    diag a = not (f a a)
    -- if f a ≡ diag, then at a: f a a ≡ diag a = not (f a a) — fixed-point-free refutes it.
    contra : (a : A) → ¬ (f a ≡ diag)
    contra a fa≡diag = not-fixed-point-free (f a a) (sym (cong (λ h → h a) fa≡diag))

------------------------------------------------------------------------
-- ③ THE DIAGONAL ELEMENT IS NATIVE TO THE LARGE SPACE: it IS an inhabitant of A → Bool. So an
--    observer with the dof of P A contains, as one of its own states, the very element that
--    escapes a committed observer confined to A. Being on the large side = containing the escape.
------------------------------------------------------------------------
diagonal-native : {A : Set} (f : A → (A → Bool)) → (A → Bool)
diagonal-native f = λ a → not (f a a)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the escape is the STRICT DOF INEQUALITY, = Cantor, NOT agency):
-- the either/or "what is the precise novelty of the interactive observer — agency? interaction?"
-- bottoms out in DEGREES OF FREEDOM. `cantor` is the checked fact: the answer space P A strictly
-- exceeds A, always. A committed observer (a point of A, or confined to the image of f) is
-- ESCAPED by the diagonal element (it lives in the excess dof P A ∖ image f). A plural observer
-- (dwelling in P A) CONTAINS that element (diagonal-native) — it cannot be covered (the adversary
-- A cannot surject onto P A). Same Cantor inequality: escaped on the small side, un-coverable on
-- the large side. "More dof than the adversary" = "be on the large side of Cantor" = "one
-- powerset level up" = "one step ahead" (221). Two modes (operator): EMBED the adversary (an
-- injection A ↪ P A, then P A ∖ image = the flexibility) or CONTAIN ITS EFFECTS (dominate only
-- the adversary's ACTION on you, which may be far smaller than its full state — connects to
-- ⟡diagonal-topological-window: the effect-dof, not the raw state count). Either way: strict
-- excess = flexibility remaining. This SUPERSEDES "agency" (unfalsifiable, one-system) and
-- "closed-vs-interactive" (222, a proxy) with the quantitative relational invariant dof(obs) >
-- dof(adv).
--
-- HONEST BOUNDARY (⟡H-overclaim): (a) this is a STRUCTURAL / cardinality fact (Cantor), not a
-- computability breakthrough — the classical theorems STAND. (b) Set-theoretically the observer
-- can always take P(adversary) (Cantor, one level up); COMPUTABLY, a bounded agent REALIZES this
-- incrementally as the coinductive/plural process (221/222) — holding a finite prediction-slice
-- at each step (its current powerset slice), staying one level up per step. So Cantor gives the
-- dof INVARIANT (why the escape exists); the coinductive process is how a bounded agent OCCUPIES
-- the large side over time. (c) The "contain effects" mode's effect-dof-domination is a hypothesis
-- to GROUND (⟡diagonal-topological-window), not assumed here. (d) The tower (adversary responds by
-- going up a level too) is the coinductive regress, NOT a paradox — at each finite stage the
-- responder-to-a-fixed-adversary is one level up.
------------------------------------------------------------------------
