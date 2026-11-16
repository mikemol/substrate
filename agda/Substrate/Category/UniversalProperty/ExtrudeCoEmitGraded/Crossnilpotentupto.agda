------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Crossnilpotentupto
--
-- Defines: cross-nilpotent-upto
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Crossnilpotentupto where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.Wedge.CrossMul
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitcrossmix
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitcrossismul
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


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
