------------------------------------------------------------------------
-- Substrate.WitnessTower.Enumerate.Words23Count
--
-- Defines: words-2-3-count
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Enumerate; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Enumerate.Words23Count where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.List
open import Substrate.WitnessTower.Enumerate.LengthL
open import Substrate.WitnessTower.Enumerate.Words
open import Substrate.Foundation.Eq


words-2-3-count : lengthL (words 2 3) ≡ 8
words-2-3-count = refl
