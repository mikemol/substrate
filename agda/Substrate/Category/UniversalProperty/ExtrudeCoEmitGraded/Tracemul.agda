------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
--
-- Defines: trace-mul
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.R.Trace.Final
open import Substrate.Algebra.R.Trace.Bisim
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ
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
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pair
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace


-- SO: the obstruction (the failing-grade set, upward-closed, = the nilpotency degree dⁿ=0) is EMPTY iff t ~ r —
-- the ONE obstruction, whether read as CrossMix's nilpotent cross term, CofreeDual's ~-obstruction, or the
-- aperiodic pole. Coherence-everywhere (no obstruction) = bisimilarity = νΦ-pair (the gfp, 324).

------------------------------------------------------------------------
-- trace-mul (operator: "this is pi-typing — you thread prior state through the constructor of your subsequent
-- state, how your coinduction works"). The mul I called ABSENT (326) IS there: the Π-typed dependent threading.
-- mul r s THREADS r's head into s's construction at each step (the coinductive cons IS the dependent product).
-- The SQUARE-ZERO threading (mirroring two-mul's ε²=z / d²=0): mul collapses to the zero-trace — the differential.
-- So RealTrace IS a MulDivStr; 326's "no mul" was D-search-own-labels (I dismissed the mul my coinduction USES).
------------------------------------------------------------------------

-- the threading mul: prior head threaded through the subsequent constructor (Π-typing); square-zero (→ z).
trace-mul : RealTrace → RealTrace → RealTrace
RealTrace.head (trace-mul r s) = 0                          -- square-zero: the product's head collapses (the differential d)
RealTrace.tail (trace-mul r s) = trace-mul (RealTrace.tail r) (RealTrace.tail s)  -- thread both tails through the subsequent constructor
