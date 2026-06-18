------------------------------------------------------------------------
-- Substrate.Algebra.F2.V4LagrangeInstance
--
-- The Klein 4-group V₄ ≅ F₂² as a `HasLagrangeOrder` instance of the
-- Substrate.Category.Coalgebra.LagrangeOrder primitive.
--
-- V₄ is the simplest NON-CYCLIC composite torsion: 4 elements each of
-- order 1 or 2, all of exponent 2 (i.e., g² = e for every g). |V₄| = 4
-- = 2 · 2 (not coprime to itself), so V₄ ≠ Z/4 — it doesn't decompose
-- as a product of coprime cyclic groups. Aut(V₄) = GL(2, F₂) of
-- order 6, not φ(4) = 2.
--
-- This slice instantiates HasLagrangeOrder 4 V₄-action — the
-- at-all-points version (not just at-a-point), since V₄'s translation
-- action on F₂² has no fixed points except trivially.
--
-- Per [[project-composite-torsion-euler-substrate]]: V₄ is the
-- substrate's example of the simplest non-cyclic composite torsion.
-- Demonstrates the LagrangeOrder primitive handles non-cyclic cases
-- where pure cyclic FLT doesn't reach.
--
-- Per [[feedback-v4-typeclass-architecture]]: V₄ canonically lives in
-- the Coxeter framework (Substrate.Groups.V4). This slice provides a
-- direct construction at the F₂² level for the LagrangeOrder
-- demonstration; a Coxeter-framework bridge is a deferred follow-on.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.V4LagrangeInstance where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Literals using (₁; ₂; ₃; ₄)
open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector

open import Substrate.Category.Coalgebra using (Endomap)
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)
open import Substrate.Category.Coalgebra.LagrangeOrder
  using (Action; HasLagrangeOrder)

------------------------------------------------------------------------
-- N-1: V₄ elements — the 4 elements of F₂².
--
--   0: (0, 0)  — identity
--   1: (1, 0)  — first generator
--   2: (0, 1)  — second generator
--   3: (1, 1)  — product = first ⊕ second
------------------------------------------------------------------------

V4-elements : Fin 4 → Vector 2
V4-elements zero                   = 𝟘 ∷ 𝟘 ∷ []
V4-elements ₁             = 𝟙 ∷ 𝟘 ∷ []
V4-elements ₂       = 𝟘 ∷ 𝟙 ∷ []
V4-elements ₃ = 𝟙 ∷ 𝟙 ∷ []

------------------------------------------------------------------------
-- N-2: V₄ action — each element acts on Vector 2 by XOR translation.
--
-- (V4-elements i) ⊕ v in F₂² terms. This is the translation action
-- of V₄ on itself (identified with F₂²); also extends to any F₂²-
-- module via componentwise XOR.
------------------------------------------------------------------------

V4-action : Action 4 (Vector 2)
V4-action i v = V4-elements i +ⱽ v

------------------------------------------------------------------------
-- N-3: Each V₄ element is an involution under its action.
--
--   V4-action i (V4-action i v)
-- = (V4-elements i) +ⱽ ((V4-elements i) +ⱽ v)
-- = ((V4-elements i) +ⱽ (V4-elements i)) +ⱽ v   [+ⱽ-assoc backward]
-- = 𝟎ⱽ +ⱽ v                                      [+ⱽ-self-inverse]
-- = v                                            [+ⱽ-identityˡ]
--
-- This is the F₂ characteristic-2 fact that g ⊕ g = 0 for any g.
------------------------------------------------------------------------

V4-each-involution :
  (i : Fin 4) (v : Vector 2) → V4-action i (V4-action i v) ≡ v
V4-each-involution i v =
  trans (sym (+ⱽ-assoc (V4-elements i) (V4-elements i) v))
  (trans (cong (_+ⱽ v) (+ⱽ-self-inverse (V4-elements i)))
         (+ⱽ-identityˡ v))

------------------------------------------------------------------------
-- N-4: Each V₄ element has order dividing 4 (in fact dividing 2).
--
-- iterate 4 (V4-action i) v
-- = V4 (V4 (V4 (V4 v)))
-- ≡ V4 (V4 v)             [V4-each-involution applied to innermost pair]
-- ≡ v                      [V4-each-involution applied again]
--
-- The "dividing 4" is structural (Lagrange at |V₄| = 4); each V₄
-- element actually has exponent 2.
------------------------------------------------------------------------

V4-each-has-order-4 : (i : Fin 4) → HasOrder (V4-action i) 4
V4-each-has-order-4 i v =
  trans (cong (λ x → V4-action i (V4-action i x)) (V4-each-involution i v))
        (V4-each-involution i v)

------------------------------------------------------------------------
-- N-5: V₄ satisfies HasLagrangeOrder — at every point in F₂².
--
-- Stronger than `HasLagrangeOrder-at` (which fixes a specific point):
-- V₄'s translation action on F₂² gives the order-dividing-4 property
-- at EVERY v, not just at a fixed point.
--
-- Concrete demonstration: the substrate's first composite-torsion
-- LagrangeOrder instance with full (at-all-points) coverage.
------------------------------------------------------------------------

V4-has-lagrange-order : HasLagrangeOrder 4 V4-action
V4-has-lagrange-order = V4-each-has-order-4

------------------------------------------------------------------------
-- N-5½: the translation action is SIMPLY TRANSITIVE — free + transitive.
-- (The "free (orbit = F₂² itself)" capstone bullet, proved. Stated at the
-- translation level g = V4-elements i, where V4-action i v = g +ⱽ v; both
-- are pure +ⱽ-cancellation, the char-2 fact g ⊕ g = 0.)
------------------------------------------------------------------------

-- FREE: only the zero translation fixes a point (g ⊕ v ≡ v ⟹ g ≡ 𝟎).
V4-action-free : (g v : Vector 2) → (g +ⱽ v) ≡ v → g ≡ 𝟎ⱽ
V4-action-free g v eq =
  trans (sym (+ⱽ-identityʳ g))
  (trans (cong (g +ⱽ_) (sym (+ⱽ-self-inverse v)))
  (trans (sym (+ⱽ-assoc g v v))
  (trans (cong (_+ⱽ v) eq)
         (+ⱽ-self-inverse v))))

-- TRANSITIVE: the translation (w ⊕ v) carries v to w, so every point's
-- orbit is all of F₂² (orbit = F₂² itself).
V4-action-transitive : (v w : Vector 2) → ((w +ⱽ v) +ⱽ v) ≡ w
V4-action-transitive v w =
  trans (+ⱽ-assoc w v v)
  (trans (cong (w +ⱽ_) (+ⱽ-self-inverse v))
         (+ⱽ-identityʳ w))

------------------------------------------------------------------------
-- N-6: Capstone — V₄ as the substrate's canonical composite-torsion
-- example.
--
-- After this slice, the Klein 4-group V₄ is formally recognized as a
-- LagrangeOrder instance:
--
--   * |V₄| = 4 with each element of exponent dividing 2
--   * Translation action on F₂² is SIMPLY TRANSITIVE — PROVED:
--     `V4-action-free` (free) + `V4-action-transitive` (orbit = F₂²).
--   * (prose: Aut(V₄) = GL(2, F₂) of order 6 — not φ(4)=2, V₄ ≠ Z/4 — is
--     classical; the automorphism group is NOT computed/formalized here.)
--
-- This is the simplest non-cyclic composite torsion in the substrate;
-- demonstrates LagrangeOrder primitive handles non-cyclic cases where
-- pure cyclic FLT (HasOrder) doesn't reach.
--
-- Per [[project-composite-torsion-euler-substrate]]: V₄'s gauge
-- behavior is qualitatively different from cyclic groups — its
-- automorphism group GL(2, F₂) = S₃ has 6 elements, encoding the
-- 6 permutations of V₄'s 3 non-identity elements as the "generators"
-- of the non-cyclic torsion structure.
--
-- Connection to [[project-3plus1-parity-universal]]: V₄'s 3 non-
-- identity elements + identity = "3+1 in V₄"; each pair of non-identity
-- elements (v₁, v₂) has v₃ = v₁ ⊕ v₂ as their "Hodge-dual-like"
-- partner. The 3+1 parity at the V₄ level is the simplest non-cyclic
-- torsion instance of this pattern.
--
-- Deferred follow-ons:
--
--   * **Coxeter-framework V₄ bridge**: connect this F₂²-based
--     construction to Substrate.Groups.V4 (which goes through the
--     Coxeter framework per [[feedback-v4-typeclass-architecture]]).
--
--   * **V₄ ↪ GL(n, F₂) embeddings**: how V₄ sits inside higher-dim
--     Linear groups (V₄ is a subgroup of S_n for n ≥ 4, and of
--     various GL(n, F₂)).
--
--   * **3+1 parity at V₄ level as BC failure**: the 3 non-identity
--     V₄ elements form a Beck-Chevalley non-commuting structure;
--     formalising this would connect V₄ to the BC primitive #5.
------------------------------------------------------------------------
