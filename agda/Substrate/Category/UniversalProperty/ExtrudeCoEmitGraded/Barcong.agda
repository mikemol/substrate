------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Barcong
--
-- Defines: bar-cong
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Barcong where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble

open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflip
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong


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
