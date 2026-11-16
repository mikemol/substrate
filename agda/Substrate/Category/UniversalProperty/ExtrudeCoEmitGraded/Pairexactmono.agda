------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pairexactmono
--
-- Defines: Φ-pair-exact-mono
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pairexactmono where

open import Substrate.Foundation.Product
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.RTPair
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pairexact
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


Φ-pair-exact-mono : {P Q : RTPair → Set} → ((rt : RTPair) → P rt → Q rt)
                  → (rt : RTPair) → Φ-pair-exact P rt → Φ-pair-exact Q rt
Φ-pair-exact-mono le (r , t) (h≡ , p) = h≡ , le (RealTrace.tail r , RealTrace.tail t) p
