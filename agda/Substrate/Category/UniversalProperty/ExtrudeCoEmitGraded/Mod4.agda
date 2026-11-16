------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Mod4
--
-- Defines: mod4
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Mod4 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Digittov4
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- (3) coemit-digit-mod4: 357 proved digit-to-v4 is 4-periodic and surjective on {0,1,2,3} — which IS the quotient.
--     Here the fibre is stated LITERALLY: digit-to-v4 n ≡ digit-to-v4 (mod4 n), i.e. the map factors through ℕ/4.
--     (Preflight: Foundation.Nat has no mod/_%_, so mod4 is defined here — 4-periodic recursion, matching bit1's.)
------------------------------------------------------------------------
mod4 : ℕ → ℕ
mod4 zero                          = zero
mod4 (suc zero)                    = suc zero
mod4 (suc (suc zero))              = suc (suc zero)
mod4 (suc (suc (suc zero)))        = suc (suc (suc zero))
mod4 (suc (suc (suc (suc n))))     = mod4 n
