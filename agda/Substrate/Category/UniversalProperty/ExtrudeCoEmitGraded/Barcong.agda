------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Barcong
--
-- Defines: bar-cong
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Barcong where

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
open import Substrate.Algebra.R.Trace.Bisim using (~-refl) renaming (_~_ to _~ᵗ_)
open import Substrate.Foundation.Empty using () renaming (⊥ to Bot)
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Algebra.F2
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis

open import Substrate.Groups.Symmetric.Eq Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflip
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar


------------------------------------------------------------------------
-- REGROUND (catalog index + depgraph, per directive):
--   • catalog/README: "each file is a shadow that survives session boundaries"; the catalog records "which
--     concepts are the same idea under different names, which claims supersede which, WHERE INTENT DRIFTED".
--   • import-graph.md: 1643 modules, 10428 SEMANTIC dependency edges (from elaborated cores, not import lines).
--   • reuse-graph.md: 747 structures, 492 refinement edges. "X --> Y means X is BUILT ON Y. **Before reinventing
--     a structure, check whether the thing you want already REFINES an existing primitive here.**"
--   • drift_archaeology.md: behavioural classes — summary-collapse, user-framing operational-drift, silent
--     naturalisation, acknowledged-then-abandoned. (The corpus has an archaeology of exactly my failure modes.)
-- Accordingly the three constructions below REFINE canonical primitives (Setoid, IsoGroupoid's iso-sym/†, DivStr).
------------------------------------------------------------------------

-- bar-cong: the conjugation RESPECTS the constructed equality (a coinductive congruence). Needed for both the
-- setoid instance (conj must respect ≈) and the transpose (†∘bar acts on ~-proofs).
bar-cong : {r s : RealTrace} → r ~ s → bar r ~ bar s
head~ (bar-cong p) = cong pflip (head~ p)
tail~ (bar-cong p) = bar-cong (tail~ p)
