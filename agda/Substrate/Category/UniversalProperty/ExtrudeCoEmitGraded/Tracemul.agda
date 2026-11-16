------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
--
-- Defines: trace-mul
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pair
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


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
