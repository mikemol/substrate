------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflipfree
--
-- Defines: pflip-free
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflipfree where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflip
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


------------------------------------------------------------------------
-- (2) coemit-lawvere-atoms: instantiate the remaining three carrier-generic atoms.
------------------------------------------------------------------------

-- pflip is FIXED-POINT-FREE on ℕ: it always flips the parity bit, so pflip n ≡ n is impossible.
pflip-free : (n : ℕ) → pflip n ≡ n → ⊥
pflip-free zero ()
pflip-free (suc zero) ()
pflip-free (suc (suc n)) eq = pflip-free n (suc-suc-inj eq)
  where suc-suc-inj : {a b : ℕ} → suc (suc a) ≡ suc (suc b) → a ≡ b
        suc-suc-inj refl = refl
