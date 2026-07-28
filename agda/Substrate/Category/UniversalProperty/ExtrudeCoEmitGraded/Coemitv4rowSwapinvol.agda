------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4rowSwapinvol
--
-- Defines: coemit-v4-rowSwap-invol
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4rowSwapinvol where

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
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
open import Substrate.Groups.V4.Bijection
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.N-to-F2-Parity
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere


------------------------------------------------------------------------
-- CATALOG REUSE (operator directive, D-catalog-reuse-check): the catalog reveals the CANONICAL V₄/S₄ machinery I was
-- reinventing. concepts.md § "V₄/S₄ algebraic structure (M28–M37)":
--   C-V4-Klein         : V₄ = the three DOUBLE-TRANSPOSITIONS of S₄, acting on 4 axes.
--   C-Z3-A4-V4         : Z₃ = A₄/V₄ (the 3-cycle quotient — my 3 axes are this quotient).
--   C-S4-A4-chirality  : chirality = the parity bit of S₄/A₄ ≅ ℤ/2.
--   C-V4-semidirect-S3 : S₄ ≅ V₄ ⋊ S₃ with S₃ = Stab(D) (the ANCHOR-AXIS stabilizer); σ = v·s uniquely. PRIMARY (v19).
-- And Substrate.Algebra.R.Trace.V4FullCocycle gives V4Full (V₄ = ℤ/2×ℤ/2) ON THE TRACE CARRIER, with the group laws
-- ALREADY PROVEN: rowSwap-invol, recip-invol, klein-is-product, klein-invol, gens-commute; plus chirality-of/-hom.
-- So: coemit-s4-group-laws = REUSE V4Full's laws (not hand-rolled); the V₄ here is the canonical Trace-side one.
------------------------------------------------------------------------

-- (1) coemit-s4-group-laws: the V₄ group laws, REUSED from the canonical Trace-side V4Full (not re-derived).
--     The two generators are involutions, they commute, and their product is the central klein element.
coemit-v4-rowSwap-invol : V4._·_ V4.rowSwap-gen V4.rowSwap-gen ≡ V4.e
coemit-v4-rowSwap-invol = V4.rowSwap-invol
