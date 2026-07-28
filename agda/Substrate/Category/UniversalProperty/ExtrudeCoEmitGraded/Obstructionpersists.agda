------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Obstructionpersists
--
-- Defines: obstruction-persists
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Obstructionpersists where

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
open import Substrate.Foundation.Empty
open import Substrate.Algebra.R.Trace.Bisim using (~-refl) renaming (_~_ to _~ᵗ_)
open import Substrate.Foundation.Empty using () renaming (⊥ to Bot)
open import Substrate.Algebra.Wedge.CrossMul
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Agreeupto
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Agreeshrink


------------------------------------------------------------------------
-- obstruction-unify: the ONE graded obstruction across cover-the-cycle / CofreeDual / CrossMix. The obstruction
-- (disagreement between r,t) PERSISTS: ¬ agree-upto n ⇒ ¬ agree-upto (suc n) [contrapositive of agree-shrink] —
-- so a disagreement at grade n is a disagreement at ALL later grades (the graded obstruction, upward-closed by
-- degree, dⁿ=0 shape). And coherence ⟺ NO obstruction: t ~ r ⟺ (∀ n, agree-upto n r t). So the obstruction =
-- the failing grades (CrossMix's nilpotency degree = CofreeDual's ~-obstruction = the aperiodic pole — ONE thing).
------------------------------------------------------------------------

-- the obstruction PERSISTS (upward-closed in degree): disagreeing at grade n ⇒ disagreeing at (suc n).
obstruction-persists : (n : ℕ) (r t : RealTrace)
                     → (agree-upto n r t → ⊥) → (agree-upto (suc n) r t → ⊥)
obstruction-persists n r t ¬agree-n agree-sucn = ¬agree-n (agree-shrink n r t agree-sucn)
