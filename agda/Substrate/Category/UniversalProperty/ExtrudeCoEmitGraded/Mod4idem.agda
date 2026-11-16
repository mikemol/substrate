------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Mod4idem
--
-- Defines: mod4-idem
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Mod4idem where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Mod4
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- and mod4 lands in the four residues (idempotent: mod4 ∘ mod4 ≡ mod4 on the classes it produces).
mod4-idem : (n : ℕ) → mod4 (mod4 n) ≡ mod4 n
mod4-idem zero                        = refl
mod4-idem (suc zero)                  = refl
mod4-idem (suc (suc zero))            = refl
mod4-idem (suc (suc (suc zero)))      = refl
mod4-idem (suc (suc (suc (suc n))))   = mod4-idem n
