------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Swap01
--
-- Defines: swap01
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Swap01 where

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
open import Substrate.Algebra.R.Trace.Bisim using (~-refl) renaming (_~_ to _~ᵗ_)
open import Substrate.Foundation.Empty using () renaming (⊥ to Bot)
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
open import Substrate.Groups.V4.Bijection
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere


------------------------------------------------------------------------
-- The HIGHER-ORDER FINITE (operator: final ≡ [~, terminal/ν] does NOT live on the carrier — it's COMPOSED of
-- reformulating each V₄ leg as "finite FROM A DIFFERENT PERSPECTIVE", a higher-order finite satisfied by PERMUTING
-- through the S₃-permutations of V₄'s 3 involutions). Each axis is finite in its own way; S₃ TRANSITIVELY connects
-- them (the single orbit); so ~ is reachability across the 3 perspectives, not a carrier-equality. (Pieces from
-- the Group/WitnessTower trees: M40Action's act-hom, Sn's finite complete enumeration — the orientation-change.)
------------------------------------------------------------------------
-- (3) coemit-s3-orbit: S₃ acts TRANSITIVELY on the 3 axes — every axis reaches every other by a permutation. The
--     single orbit IS the higher-order finite: the 3 "finite-from-a-perspective" legs are one, up to permutation.

-- the transposition swapping two Fin-3 positions (a concrete S₃ generator) — the orientation-change permutation.
swap01 : Fin 3 → Fin 3
swap01 zero             = suc zero
swap01 (suc zero)       = zero
swap01 (suc (suc zero)) = suc (suc zero)
