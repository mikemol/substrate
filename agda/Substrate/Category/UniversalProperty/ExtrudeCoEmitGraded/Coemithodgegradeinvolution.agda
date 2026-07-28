------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemithodgegradeinvolution
--
-- Defines: coemit-hodge-grade-involution
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemithodgegradeinvolution where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace using (coemit-trace) renaming (coalg to coemit-coalg)
open import Substrate.Foundation.Eq using () renaming (trans to ≡-trans)
open import Substrate.Category.Allegory.Refinement using (Refinement) renaming (iterate to Riterate)
open import Substrate.Category.Allegory.Refinement using () renaming (chain to Rchain; _⊑ᶠ_ to _R⊑ᶠ_)
open import Substrate.Algebra.R.Trace.Bisim using (~-trans) renaming (head~ to bhead~; tail~ to btail~)
open import Substrate.Foundation.Eq using (sym; cong) renaming (trans to ≡tr)
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo
open import Substrate.Algebra.R.Trace.Bisim using (~-refl) renaming (_~_ to _~ᵗ_)
open import Substrate.Foundation.Empty using () renaming (⊥ to Bot)
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')
open import Substrate.Foundation.Fin.Fin
open import Substrate.WitnessTower.Hodge
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.N-to-F2-Parity
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.WitnessTower.FaceSet
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere


------------------------------------------------------------------------
-- (3) coemit-hodge-axis: Hodge's dual-grade₃ (Λ⁰↔Λ³, Λ¹↔Λ² — the grade involution) IS the μν-axis flip. The
--     grade-duality (Hodge ★) riding the rung-3→4 seam = the μ↔ν axis reflection (one of V₄'s 3 involutions).
------------------------------------------------------------------------

-- the Hodge grade-involution is an involution (Λ⁰↔Λ³, Λ¹↔Λ²), matching axis-flip's flip²=id (the μν-axis).
-- RENAMED (345 retraction discharged): this is the Hodge GRADE involution (Λᵏ↔Λⁿ⁻ᵏ), NOT the μν/orientation flip.
-- The canonical orientation is chirality (S₄/A₄ parity) — see coemit-orientation-of. The FACT stands; the name was wrong.
coemit-hodge-grade-involution : (i : Fin 4) → dual-grade₃ (dual-grade₃ i) ≡ i
coemit-hodge-grade-involution = dual-grade₃-involution
  where open import Substrate.Foundation.Fin.Fin
