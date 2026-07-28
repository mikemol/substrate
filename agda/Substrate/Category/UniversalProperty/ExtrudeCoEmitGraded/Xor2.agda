------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Xor2
--
-- Defines: xor2
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Xor2 where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace using (coemit-trace) renaming (coalg to coemit-coalg)
open import Substrate.Foundation.Product
open import Substrate.Foundation.Eq using () renaming (trans to ≡-trans)
open import Substrate.Category.Allegory.Refinement using (Refinement) renaming (iterate to Riterate)
open import Substrate.Category.Allegory.Refinement using () renaming (chain to Rchain; _⊑ᶠ_ to _R⊑ᶠ_)
open import Substrate.Algebra.R.Trace.Bisim using (~-trans) renaming (head~ to bhead~; tail~ to btail~)
open import Substrate.Foundation.Eq using (sym; cong) renaming (trans to ≡tr)
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo
open import Substrate.Algebra.Wedge
open import Substrate.Foundation.Empty
open import Substrate.Algebra.R.Trace.Bisim using (~-refl) renaming (_~_ to _~ᵗ_)
open import Substrate.Foundation.Empty using () renaming (⊥ to Bot)
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
open import Substrate.Groups.V4.Bijection
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Algebra.F2
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflip
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitTraceKlein


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
