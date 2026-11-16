------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Perspectiveisfiniteheadtail
--
-- Defines: perspective-is-finite-head-tail
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Perspectiveisfiniteheadtail where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Len
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Perspectivefinite
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- (2) coemit-perspective-finite-rest: the other two axes' finiteness. head-tail = depth-1 (a single digit);
--     cyc-aper = depth-n (the finite window) — the same bounded pattern as μν, completing the 3 finite perspectives.
perspective-is-finite-head-tail : (r : RealTrace) → len (perspective-finite head-tail-axis r 0) ≡ 1
perspective-is-finite-head-tail r = refl
