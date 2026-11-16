------------------------------------------------------------------------
-- Substrate.WitnessTower.Enumerate.Perms3Count
--
-- Defines: perms-3-count
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Enumerate; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Enumerate.Perms3Count where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.List
open import Substrate.WitnessTower.Enumerate.LengthL
open import Substrate.WitnessTower.Enumerate.Perms
open import Substrate.Foundation.Eq


perms-3-count : lengthL (perms 3) ≡ 6
perms-3-count = refl
