------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Xor2
--
-- Defines: xor2
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Xor2 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflip
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitTraceKlein
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- PREFLIGHT (Category.Lawvere's remaining atoms, exact fields):
--   record FixedPointFree   (V : Set) : Set { δ : V → V ; δ-free : δ v ≡ v → ⊥ }
--   record InvolutiveResidue(V : Set) : Set { δ ; δ-free ; δ-invol : δ (δ v) ≡ v }
--   record TorsorAtom       (A : Set) : Set { _∙_ ; e ; fix→unit : (g ∙ x) ≡ x → g ≡ e }
-- Header: "the F₂ instance is δ = (𝟙 +_), whose δ-free is exactly WitnessTower.Diagonal.flip-disagrees."
--
-- (1) coemit-trace-delta2: bar = pflip on the digit = XOR-1 (bit0 = the chirality/parity bit, 350). Its INDEPENDENT
--     partner is XOR-2 (bit1): 0↔2, 1↔3, 4↔6, 5↔7, … Both are involutions and they COMMUTE (XOR is abelian), so
--     ⟨bar, bar₂⟩ ≅ ℤ/2 × ℤ/2 = V₄ on the TRACE carrier — matching V4Full's (morph, obj) = (bit0, bit1) exactly.
--     This is the GENUINE δ₂ that CoemitTraceKlein demanded (354): no longer the degenerate V₂ collapse.
------------------------------------------------------------------------
-- xor2 on the digit: flip bit1 (0↔2, 1↔3, then 4-periodic).
xor2 : ℕ → ℕ
xor2 zero                             = suc (suc zero)
xor2 (suc zero)                       = suc (suc (suc zero))
xor2 (suc (suc zero))                 = zero
xor2 (suc (suc (suc zero)))           = suc zero
xor2 (suc (suc (suc (suc n))))        = suc (suc (suc (suc (xor2 n))))
