------------------------------------------------------------------------
-- Substrate.WitnessTower.Enumerate.Perms1Count
--
-- Defines: perms-1-count
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Enumerate; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Enumerate.Perms1Count where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.List
open import Substrate.WitnessTower.Enumerate.LengthL
open import Substrate.WitnessTower.Enumerate.Perms
open import Substrate.WitnessTower.Enumerate.Words
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- The count checks: perms 4 has 24 entries (S₄), words 2 3 has 2³ = 8.
------------------------------------------------------------------------

perms-1-count : lengthL (perms 1) ≡ 1
perms-1-count = refl
