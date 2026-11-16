------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Takedrop
--
-- Defines: take-drop
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Takedrop where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.List
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Lh
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Lt
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2


-- SHRINKING: agreeing on (suc n) digits ⇒ agreeing on n (the chain properly descends). By induction on n.
take-drop : (n : ℕ) (t r : RealTrace) → take (suc n) t ≡ take (suc n) r → take n t ≡ take n r
take-drop zero    t r _  = refl
take-drop (suc n) t r eq =
  cong₂ _∷_ (cong (lh (RealTrace.head t)) eq) (take-drop n (RealTrace.tail t) (RealTrace.tail r) (cong lt eq))
  where open import Substrate.Foundation.Eq using (cong₂)
