------------------------------------------------------------------------
-- Substrate.WitnessTower.Enumerate.LengthAppend
--
-- Defines: length-++
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Enumerate; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Enumerate.LengthAppend where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.List
open import Substrate.WitnessTower.Enumerate.LengthL
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong



-- length distributes over append.
length-++ : ∀ {a} {A : Set a} (xs ys : List A) →
            lengthL (xs ++ ys) ≡ lengthL xs ℕ+ lengthL ys
length-++ []       ys = refl
length-++ (x ∷ xs) ys = cong suc (length-++ xs ys)
