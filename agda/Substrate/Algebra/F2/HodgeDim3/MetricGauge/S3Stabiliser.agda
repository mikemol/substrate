------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.S3Stabiliser
--
-- Packages the S₃ stabiliser of metric-id (in GL(3, F₂) congruence
-- action on SymBilinForm-3) as a `HasLagrangeOrder-at` instance of
-- the Substrate.Category.Coalgebra.LagrangeOrder primitive.
--
-- Pieces:
--
--   * S₃-elements : Fin 6 → Linear 3 3 — enumeration of the 6
--     elements of S₃ via Coxeter presentation (e, s₁, s₂, s₁∘s₂,
--     s₂∘s₁, s₁∘s₂∘s₁).
--   * S₃-cong-action : Fin 6 → Endomap SymBilinForm-3 — the
--     congruence action of each S₃ element on SymBilinForm-3.
--   * congruence-act-id-L-metric-id : the identity element fixes
--     metric-id (lemma).
--   * S₃-stabilises-metric-id : HasLagrangeOrder-at 6 S₃-cong-action
--     metric-id — the 6-element stabiliser as a unified
--     LagrangeOrder-at-a-point instance.
--
-- Per [[project-composite-torsion-euler-substrate]]: this is the
-- concrete instantiation of the Lagrange / Euler-Fermat lift to
-- the substrate's S₃ stabiliser story. Each individual stabilisation
-- witness (s₁-stabilises-metric-id, etc.) is already in
-- {Stabiliser, StabiliserClosure}.agda; this slice unifies them as a
-- single LagrangeOrder-at instance.
--
-- Per `feedback_categorical_name_first`: the categorical handle is
-- "Lagrange's theorem applied to the S₃ stabiliser action"; the
-- substrate's existing 6 per-element witnesses ARE this LagrangeOrder
-- instance, now named with its universal property.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.S3Stabiliser where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Literals using (₁; ₂; ₃; ₄; ₅)
open import Substrate.Foundation.Vec using ([]; _∷_; lookup)
open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear

open import Substrate.Algebra.F2.HodgeDim3.MetricGauge
  using (SymBilinForm-3; metric-id; bilinear-form-of; congruence-act)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser
  using (s₁; s₂; s₁-stabilises-metric-id; s₂-stabilises-metric-id)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.StabiliserClosure
  using (s₁∘s₂-stabilises-metric-id;
         s₂∘s₁-stabilises-metric-id;
         s₁∘s₂∘s₁-stabilises-metric-id)

open import Substrate.Category.Coalgebra using (Endomap)
open import Substrate.Category.Coalgebra.FiniteOrder
  using (iterate-at-fixed-point)
open import Substrate.Category.Coalgebra.LagrangeOrder
  using (Action; HasLagrangeOrder-at)

------------------------------------------------------------------------
-- N-1: Identity element stabilises metric-id.
--
-- congruence-act id-L M = the form with entries
--   bilinear-form-of M (apply id-L (basis i)) (apply id-L (basis j))
-- For id-L, apply id-L v = v (definitional), so
--   = bilinear-form-of M (basis i) (basis j)
-- For metric-id specifically, each of the 6 Vector 6 entries is the
-- corresponding matrix entry — equal to metric-id's entry by refl.
------------------------------------------------------------------------

congruence-act-id-L-metric-id :
  congruence-act id-L metric-id ≡ metric-id
congruence-act-id-L-metric-id = ≡-from-lookup _ _ goal
  where
    goal : (k : Fin 6) →
           lookup (congruence-act id-L metric-id) k ≡ lookup metric-id k
    goal zero                                  = refl
    goal (suc zero)                            = refl
    goal ₂                      = refl
    goal ₃                = refl
    goal ₄          = refl
    goal ₅    = refl

------------------------------------------------------------------------
-- N-2: S₃-elements — enumeration of the 6 S₃ elements via Coxeter
-- presentation.
--
--   0: e (identity)
--   1: s₁              (involution; swap basis 0 ↔ 1)
--   2: s₂              (involution; swap basis 1 ↔ 2)
--   3: s₁ ∘L s₂       (3-cycle; 0 → 1 → 2 → 0)
--   4: s₂ ∘L s₁       (3-cycle; 0 → 2 → 1 → 0)
--   5: s₁ ∘L s₂ ∘L s₁ (swap 0 ↔ 2; equals s₂∘L s₁∘L s₂ by braid)
--
-- Coxeter presentation: ⟨ s₁, s₂ | s₁² = s₂² = (s₁s₂)³ = e ⟩.
------------------------------------------------------------------------

S₃-elements : Fin 6 → Linear 3 3
S₃-elements zero                                  = id-L
S₃-elements (suc zero)                            = s₁
S₃-elements ₂                      = s₂
S₃-elements ₃                = s₁ ∘L s₂
S₃-elements ₄          = s₂ ∘L s₁
S₃-elements ₅    = s₁ ∘L s₂ ∘L s₁

------------------------------------------------------------------------
-- N-3: S₃-cong-action — the congruence action of each S₃ element on
-- SymBilinForm-3.
--
-- Each S₃ element g gives an endomap of SymBilinForm-3 via
-- congruence-act g.
------------------------------------------------------------------------

S₃-cong-action : Action 6 SymBilinForm-3
S₃-cong-action i = congruence-act (S₃-elements i)

------------------------------------------------------------------------
-- N-4: S₃-stabilises-metric-id — the LagrangeOrder-at instance.
--
-- Each of the 6 S₃ elements fixes metric-id under congruence action:
-- congruence-act g metric-id ≡ metric-id. By
-- `iterate-at-fixed-point`, iterating any number of times (including
-- 6) preserves the fixed point.
--
-- This packages the 6 individual stabilisation witnesses as a single
-- LagrangeOrder-at-metric-id instance. The categorical handle:
-- "Lagrange's theorem applied to the stabiliser subgroup."
------------------------------------------------------------------------

S₃-stabilises-metric-id : HasLagrangeOrder-at 6 S₃-cong-action metric-id
S₃-stabilises-metric-id zero =
  iterate-at-fixed-point {γ = congruence-act id-L}
                         congruence-act-id-L-metric-id 6
S₃-stabilises-metric-id (suc zero) =
  iterate-at-fixed-point {γ = congruence-act s₁}
                         s₁-stabilises-metric-id 6
S₃-stabilises-metric-id ₂ =
  iterate-at-fixed-point {γ = congruence-act s₂}
                         s₂-stabilises-metric-id 6
S₃-stabilises-metric-id ₃ =
  iterate-at-fixed-point {γ = congruence-act (s₁ ∘L s₂)}
                         s₁∘s₂-stabilises-metric-id 6
S₃-stabilises-metric-id ₄ =
  iterate-at-fixed-point {γ = congruence-act (s₂ ∘L s₁)}
                         s₂∘s₁-stabilises-metric-id 6
S₃-stabilises-metric-id ₅ =
  iterate-at-fixed-point {γ = congruence-act (s₁ ∘L s₂ ∘L s₁)}
                         s₁∘s₂∘s₁-stabilises-metric-id 6

------------------------------------------------------------------------
-- N-5: Capstone — composite-torsion infrastructure pays off concretely.
--
-- After this slice, the substrate's S₃ stabiliser story is unified
-- as a single LagrangeOrder-at-metric-id instance. The previously-
-- scattered per-element witnesses ({Stabiliser, StabiliserClosure}.agda)
-- are now organised as a Fin 6 → Endomap family with the universal
-- Lagrange property.
--
-- Structural payoff:
--
--   * **Unification**: 6 separate per-element stabilisation witnesses
--     become 1 LagrangeOrder-at instance. The Coxeter group structure
--     of S₃ is now explicit at the categorical level.
--
--   * **Composite-torsion concrete instance**: this is the substrate's
--     first concrete `HasLagrangeOrder-at` instance, demonstrating
--     the LagrangeOrder primitive (from Coalgebra.LagrangeOrder)
--     pays off in real substrate work — not just an abstract type.
--
--   * **|orbit| · |stabiliser| = 28 · 6 = 168** at L_metric: the
--     LagrangeOrder-at witness IS the 6-cardinality stabiliser side
--     of this arithmetic.
--
-- Per [[project-composite-torsion-euler-substrate]]: the
-- LagrangeOrder lift handles composite (non-cyclic-prime) torsion;
-- S₃ is the simplest non-trivial example.
--
-- Deferred follow-ons:
--
--   * **HasLagrangeOrder (all-points) version**: would require showing
--     each congruence-act g preserves arbitrary M, not just metric-id.
--     That's a stronger statement (orbit-stabiliser everywhere) and
--     a separate slice.
--
--   * **S₃ as Coxeter subgroup of GL(3, F₂)**: bridge to
--     Substrate.Groups.S3 (via Coxeter framework). Connects this
--     concrete dim-3 stabiliser to the abstract group structure.
--
--   * **Analogous S₄ instance at dim 4**: when dim-4 stabiliser
--     work develops, mirror this LagrangeOrder-at-metric-id-4
--     instance at 24-cardinality.
------------------------------------------------------------------------
