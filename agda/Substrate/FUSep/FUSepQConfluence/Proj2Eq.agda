------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQConfluence.Proj2Eq
--
-- Defines: proj₂≡
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQConfluence; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQConfluence.Proj2Eq where

open import Substrate.Foundation.Product
import Substrate.Foundation.Product as FP   -- for the ⟡def-eq projection witnesses
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQConfluence.Proj2


proj₂≡ : {A B : Set} (p : A × B) → proj₂ p ≡ FP.proj₂ p
proj₂≡ (a , b) = refl
