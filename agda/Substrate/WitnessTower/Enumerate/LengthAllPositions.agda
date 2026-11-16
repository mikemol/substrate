------------------------------------------------------------------------
-- Substrate.WitnessTower.Enumerate.LengthAllPositions
--
-- Defines: length-all-positions
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Enumerate; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Enumerate.LengthAllPositions where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.List
open import Substrate.WitnessTower.Enumerate.LengthL
open import Substrate.WitnessTower.Enumerate.AllPositions
open import Substrate.WitnessTower.Enumerate.LenMap
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans



-- |all-positions n| = n.
length-all-positions : (n : ℕ) → lengthL (all-positions n) ≡ n
length-all-positions zero    = refl
length-all-positions (suc n) =
  cong suc (trans (len-map suc (all-positions n)) (length-all-positions n))
