------------------------------------------------------------------------
-- Substrate.WitnessTower.Enumerate.Perms2Count
--
-- Defines: perms-2-count
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Enumerate; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Enumerate.Perms2Count where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.List
open import Substrate.WitnessTower.Enumerate.LengthL
open import Substrate.WitnessTower.Enumerate.Perms
open import Substrate.Foundation.Eq


perms-2-count : lengthL (perms 2) ≡ 2
perms-2-count = refl
