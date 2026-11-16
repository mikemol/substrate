------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQConfluence.Proj1
--
-- Defines: proj₁
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQConfluence; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQConfluence.Proj1 where

open import Substrate.Foundation.Product
import Substrate.Foundation.Product as FP   -- for the ⟡def-eq projection witnesses
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq



proj₁ : {A B : Set} → A × B → A
proj₁ (a , _) = a
