------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQHexagon.PIdxEqQIdx
--
-- Defines: PIdx≡QIdx
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQHexagon; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQHexagon.PIdxEqQIdx where

open import Substrate.Foundation.Iff
open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQHexagon.PIdx
open import Substrate.FUSep.FUSepQHexagon.QIdx


PIdx≡QIdx : PIdx ⇔ QIdx
PIdx≡QIdx = ⇔-refl
