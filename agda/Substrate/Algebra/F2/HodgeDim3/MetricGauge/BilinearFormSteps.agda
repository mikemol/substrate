------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.BilinearFormSteps
--
-- Two micro-primitives for rewriting `bilinear-form-of M (apply s e₁) (apply s e₂)`
-- via per-basis-image lemmas `apply s eᵢ ≡ rᵢ`.
--
--   diag-bf-step      — same vector on both bilinear-form-of arguments
--   off-diag-bf-step  — different vectors on each argument
--
-- These primitives capture the "rewrite both basis-images" pattern that
-- recurs in `congruence-act s metric-id ≡ metric-id` proofs (e.g.,
-- Stabiliser.agda's s₁/s₂-stabilises-metric-id, where the 6 lookup-i
-- goals split into 3 diagonal (i ∈ {₀, ₁, ₂}) + 3 off-diagonal
-- (i ∈ {₃, ₄, ₅}) cases).
--
-- Extracted under the fine-grained-over-coarse discipline; each per-site
-- goal collapses from a 2-line cong-trans/cong expression to a 1-line
-- primitive call.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.BilinearFormSteps where

open import Substrate.Foundation.Eq using (_≡_; cong; cong-trans)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Type using (SymBilinForm-3)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.BilinearFormOf using (bilinear-form-of)

------------------------------------------------------------------------
-- Diagonal step. Rewrites `bilinear-form-of M (apply s e) (apply s e)`
-- via a single basis-image lemma.
------------------------------------------------------------------------

diag-bf-step :
  (M : SymBilinForm-3) (s : Linear 3 3) (e : Vector 3) {r : Vector 3} →
  apply s e ≡ r →
  bilinear-form-of M (apply s e) (apply s e) ≡ bilinear-form-of M r r
diag-bf-step M _ _ lem = cong (λ x → bilinear-form-of M x x) lem

------------------------------------------------------------------------
-- Off-diagonal step. Rewrites `bilinear-form-of M (apply s e₁) (apply s e₂)`
-- via two basis-image lemmas, one per argument.
------------------------------------------------------------------------

off-diag-bf-step :
  (M : SymBilinForm-3) (s : Linear 3 3) (e₁ e₂ : Vector 3) {r₁ r₂ : Vector 3} →
  apply s e₁ ≡ r₁ →
  apply s e₂ ≡ r₂ →
  bilinear-form-of M (apply s e₁) (apply s e₂) ≡ bilinear-form-of M r₁ r₂
off-diag-bf-step M s _ e₂ {r₁} lem-1 lem-2 =
  cong-trans (λ x → bilinear-form-of M x (apply s e₂)) lem-1
             (cong (bilinear-form-of M r₁) lem-2)
