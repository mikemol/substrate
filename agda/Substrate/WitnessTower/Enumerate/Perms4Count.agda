------------------------------------------------------------------------
-- Substrate.WitnessTower.Enumerate.Perms4Count
--
-- Defines: perms-4-count
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Enumerate; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Enumerate.Perms4Count where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.List
open import Substrate.WitnessTower.Enumerate.LengthL
open import Substrate.WitnessTower.Enumerate.Perms
open import Substrate.Foundation.Eq


perms-4-count : lengthL (perms 4) ≡ 24
perms-4-count = refl
