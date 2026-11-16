------------------------------------------------------------------------
-- Substrate.WitnessTower.Enumerate.LenMap
--
-- Defines: len-map
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Enumerate; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Enumerate.LenMap where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.List
open import Substrate.WitnessTower.Enumerate.MapL
open import Substrate.WitnessTower.Enumerate.LengthL
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong



-- lengthL is preserved by mapL.
len-map : ∀ {a b} {A : Set a} {B : Set b} (f : A → B) (xs : List A) →
          lengthL (mapL f xs) ≡ lengthL xs
len-map f []       = refl
len-map f (x ∷ xs) = cong suc (len-map f xs)
