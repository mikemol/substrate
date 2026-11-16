------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQHexagon.P1
--
-- Defines: p₁
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQHexagon; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQHexagon.P1 where

open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq



p₁ : {A B : Set} → A × B → A
p₁ (a , _) = a
