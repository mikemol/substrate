------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm.HodgeRecast
--
-- Generic HodgeRecast at any n. Proves
--
--   v ·F w ≡ bilinear-form-of metric-id v w
--
-- as a single theorem parametric in n. The existing dim-3
-- HodgeDim3.MetricGauge.HodgeRecast and dim-4
-- HodgeDim4.MetricGauge.HodgeRecast become INSTANTIATION COROLLARIES
-- of this single proof (modulo bridges to the existing
-- SymBilinForm-{3,4} representations, which are a separate slice).
--
-- Proof strategy: the inner sum
--
--   sum-F₂ (λ j → metric-id i j · lookup w j)
--
-- δ-collapses to `lookup w i` — because metric-id is the Kronecker-
-- delta on F₂. With that, the outer sum becomes
--
--   sum-F₂ (λ i → lookup v i · lookup w i)  =  v ·F w
--
-- by definition.
--
-- Per `feedback_universal_property_discipline`: the δ-collapse is the
-- universal-property fact about metric-id as the diagonal identity;
-- naming it once eliminates per-dim recomputation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm.HodgeRecast where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using ([]; _∷_; lookup)
open import Substrate.Foundation.Function using (_∘_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.Universal using (sum-F₂; sum-F₂-cong)
open import Substrate.Algebra.F2.Vector.DotProduct using (_·F_)
open import Substrate.Algebra.F2.SymBilinForm
  using (BilinForm; bilinear-form-of; metric-id)

------------------------------------------------------------------------
-- N-1: sum-of-zeros — sum-F₂ of the constant-𝟘 function is 𝟘.
--
-- Trivial by induction on n: at zero, refl. At suc, `𝟘 + sum-of-zeros`
-- reduces via the `𝟘 + y = y` pattern.
------------------------------------------------------------------------

sum-of-zeros : ∀ {n} → sum-F₂ {n} (λ _ → 𝟘) ≡ 𝟘
sum-of-zeros {zero}  = refl
sum-of-zeros {suc n} = sum-of-zeros {n}

------------------------------------------------------------------------
-- N-2: metric-id-collapse — the δ-collapse property.
--
-- For any i and any w, the sum
--   sum-F₂ (λ j → metric-id i j · lookup w j)
-- reduces to `lookup w i`.
--
-- Proof: induction on i (with simultaneous pattern-match on w to
-- extract the head/tail).
--
--   Case i = zero (w = w₀ ∷ ws): the j=zero term is `𝟙 · w₀ = w₀`;
--     every j=suc-_ term is `𝟘 · lookup ws j' = 𝟘`. Sum collapses
--     to `w₀ + 𝟘 = w₀`.
--
--   Case i = suc i' (w = w₀ ∷ ws): the j=zero term is `𝟘 · w₀ = 𝟘`;
--     every j=suc-_ term is `metric-id i' j' · lookup ws j'`. Sum
--     becomes `𝟘 + sum-F₂ (...) ≡ sum-F₂ (...)`, and by IH equals
--     `lookup ws i' = lookup (w₀ ∷ ws) (suc i')`.
------------------------------------------------------------------------

metric-id-collapse :
  ∀ {n} (i : Fin n) (w : Vector n) →
  sum-F₂ (λ j → metric-id i j · lookup w j) ≡ lookup w i
metric-id-collapse {suc n} zero    (w₀ ∷ ws) =
  -- LHS reduces to: w₀ + sum-F₂ {n} (λ j → 𝟘 · lookup ws j)
  -- → w₀ + sum-F₂ {n} (λ _ → 𝟘)   [sum-F₂-cong via ·-absorbˡ]
  -- → w₀ + 𝟘                      [sum-of-zeros]
  -- → w₀                          [+-identityʳ]
  trans (cong (w₀ +_)
              (trans (sum-F₂-cong {n} (λ j → ·-absorbˡ (lookup ws j)))
                     (sum-of-zeros {n})))
        (+-identityʳ w₀)
metric-id-collapse {suc n} (suc i) (w₀ ∷ ws) =
  -- LHS reduces to: 𝟘 + sum-F₂ {n} (λ j → metric-id i j · lookup ws j)
  -- → sum-F₂ {n} (λ j → metric-id i j · lookup ws j)   [𝟘 + y = y, by pattern]
  -- → lookup ws i                                       [IH at n]
  -- = lookup (w₀ ∷ ws) (suc i)                          [by definition]
  metric-id-collapse {n} i ws

------------------------------------------------------------------------
-- N-3: HodgeRecast-generic — `v ·F w ≡ bilinear-form-of metric-id v w`
-- at any n.
--
-- After unfolding both sides:
--   LHS = sum-F₂ (λ i → lookup v i · lookup w i)
--   RHS = sum-F₂ (λ i → lookup v i · sum-F₂ (λ j → metric-id i j · lookup w j))
--
-- The two differ only in the inner factor: LHS has `lookup w i`,
-- RHS has `sum-F₂ (λ j → metric-id i j · lookup w j)`. metric-id-
-- collapse bridges the two pointwise; sum-F₂-cong lifts the bridge
-- to the outer sum.
------------------------------------------------------------------------

·F-eq-metric-id-bilin-generic :
  ∀ {n} (v w : Vector n) →
  v ·F w ≡ bilinear-form-of metric-id v w
·F-eq-metric-id-bilin-generic {n} v w =
  sum-F₂-cong {n}
    (λ i → cong (lookup v i ·_) (sym (metric-id-collapse i w)))

------------------------------------------------------------------------
-- N-4: Capstone — fixed-point reached for HodgeRecast.
--
-- After this slice, every HodgeRecast claim at any n is a corollary
-- of `·F-eq-metric-id-bilin-generic`:
--
--   * HodgeDim3.MetricGauge.HodgeRecast's `·F-eq-metric-id-bilin`
--     at n=3 — instantiation modulo the SymBilinForm-3 ↔
--     SymBilinForm 3 bridge.
--
--   * HodgeDim4.MetricGauge.HodgeRecast's `·F-eq-metric-id-4-bilin`
--     at n=4 — same.
--
--   * HodgeRecast at n=5, 6, ... — works immediately, no slice
--     needed.
--
-- The substrate's per-dim recast proofs (with their LHS→canonical /
-- RHS←canonical bridging templates) are NO LONGER needed for future
-- dimensions. The existing dim-3 / dim-4 versions remain valid in
-- their original form; bridging them to corollaries is a separate
-- annealing step that depends on the (deferred) SymBilinForm-3/4 ↔
-- SymBilinForm 3/4 wrappers.
--
-- Per `feedback_categorical_name_first`: the δ-collapse + sum-F₂-cong
-- IS the inference rule for HodgeRecast at any n. No new infrastructure
-- per dim; the universal property of metric-id (the Kronecker delta)
-- + the universal property of sum-F₂ (congruence under pointwise
-- equality) compose to give HodgeRecast for free.
------------------------------------------------------------------------
