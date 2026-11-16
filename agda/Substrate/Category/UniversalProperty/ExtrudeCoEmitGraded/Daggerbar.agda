------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Daggerbar
--
-- Defines: dagger-bar
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Daggerbar where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Barcong
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Transpose
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong


-- † and bar COMMUTE **AT THE ENDPOINTS** (StarV4's V₄-not-dihedral condition, `recip-bar`). HONEST SCOPE:
-- †∘bar and bar∘† are two CONSTRUCTIONS with the SAME TYPE (both : bar s ~ bar r). That is commutation of the
-- V₄ square on OBJECTS. A PROOF-level commutation (the two ~-proofs identified) needs a further step: either
-- ~-proof-irrelevance, or the totality — (∀ n) their take-images agree (351). NOT claimed here. ⟡coemit-v4-square.
dagger-bar : {r s : RealTrace} → r ~ s → bar s ~ bar r
dagger-bar p = bar-cong (~-sym p)           -- bar ∘ † (transpose p = † ∘ bar is the other route; SAME endpoints)
