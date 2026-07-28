------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Crossnilpotentupto
--
-- Defines: cross-nilpotent-upto
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Crossnilpotentupto where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.R.Trace.Bisim
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace using (coemit-trace) renaming (coalg to coemit-coalg)
open import Substrate.Foundation.Eq using () renaming (trans to ≡-trans)
open import Substrate.Category.Allegory.Refinement using (Refinement) renaming (iterate to Riterate)
open import Substrate.Category.Allegory.Refinement using () renaming (chain to Rchain; _⊑ᶠ_ to _R⊑ᶠ_)
open import Substrate.Algebra.R.Trace.Bisim using (~-trans) renaming (head~ to bhead~; tail~ to btail~)
open import Substrate.Foundation.Eq using (sym; cong) renaming (trans to ≡tr)
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo
open import Substrate.Algebra.Wedge
open import Substrate.Algebra.Wedge.Mul
open import Substrate.Algebra.R.Trace.Bisim using (~-refl) renaming (_~_ to _~ᵗ_)
open import Substrate.Foundation.Empty using () renaming (⊥ to Bot)
open import Substrate.Algebra.Wedge.CrossMul
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')
open import Substrate.Foundation.Fin.Op3
open import Substrate.Foundation.Fin.Op3
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitcrossmix
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitcrossismul


------------------------------------------------------------------------
-- degree-is-nilpotency: the CrossMix cross term (trace-mul r t) IS Nilpotent (collapses to z) — so coherence is
-- ALWAYS witnessed at the μ/EXACT frame (the trace-mul is square-zero: pow 0 = trace-mul r t, which is ~ z). But
-- the OBSTRUCTION DEGREE (327, the first-disagreement grade) lives at the ~/ν frame — the GRADE where the two
-- traces stop agreeing. So: the cross-term nilpotency (μ, always coherent, degree ≤ 1) and the obstruction degree
-- (ν, where bisimilarity fails) are the stencil's TWO FRAMES of the ONE obstruction (D-obstruction-is-one, dⁿ=0).
------------------------------------------------------------------------
-- the cross term is Nilpotent up to ~ (it collapses to zero-trace = z at grade 0) — the μ/EXACT frame coherence.
cross-nilpotent-upto : (r t : RealTrace) → cross coemit-crossmix r t ~ zero-trace
cross-nilpotent-upto = coemit-cross-is-mul
