------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitconjconj
--
-- Defines: coemit-conj-conj
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitconjconj where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflipinvolutive
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong


------------------------------------------------------------------------
-- (1) coemit-conj-conj-totality: conj∘conj = id, CONSTRUCTED (351: ≡ is the totality of the orbit's actions).
--     Coinductively: heads by pflip-involutive, tails by corecursion. This IS conj-conj — not "only up to ~".
------------------------------------------------------------------------
coemit-conj-conj : (r : RealTrace) → bar (bar r) ~ r
head~ (coemit-conj-conj r) = pflip-involutive (RealTrace.head r)
tail~ (coemit-conj-conj r) = coemit-conj-conj (RealTrace.tail r)
