------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQConfluence.Proj1Eq
--
-- Defines: proj₁≡
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQConfluence; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQConfluence.Proj1Eq where

open import Substrate.Foundation.Product
import Substrate.Foundation.Product as FP   -- for the ⟡def-eq projection witnesses
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQConfluence.Proj1


proj₁≡ : {A B : Set} (p : A × B) → proj₁ p ≡ FP.proj₁ p
proj₁≡ (a , b) = refl
