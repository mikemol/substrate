------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Prefixseparates
--
-- Defines: prefix-separates
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Prefixseparates where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.List
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Lh
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Lt
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.F2.AES.KAT.Pre


-- THE PREFIX LIMIT: equal prefixes at every grade ⇒ bisimilar (the finite prefixes determine the trace up to ~).
-- head from grade 1 (take 1 r = head r ∷ []); tail prefixes from grade (suc n), via cong lt.
prefix-separates : (r s : RealTrace) → ((n : ℕ) → take n r ≡ take n s) → r ~ s
head~ (prefix-separates r s pre) = cong (lh (RealTrace.head r)) (pre 1)
tail~ (prefix-separates r s pre) =
  prefix-separates (RealTrace.tail r) (RealTrace.tail s) (λ n → cong lt (pre (suc n)))
