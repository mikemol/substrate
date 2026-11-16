------------------------------------------------------------------------
-- Substrate.WitnessTower.Enumerate.LengthConcatMapLConst
--
-- Defines: length-concatMapL-const
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Enumerate; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Enumerate.LengthConcatMapLConst where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.List
open import Substrate.WitnessTower.Enumerate.ConcatMapL
open import Substrate.WitnessTower.Enumerate.LengthL
open import Substrate.WitnessTower.Enumerate.LengthAppend
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Trans



-- a concatMap whose blocks all have the same length c sums to |xs| · c.
length-concatMapL-const :
  ∀ {a b} {A : Set a} {B : Set b}
  (c : ℕ) (g : A → List B) (xs : List A) →
  (∀ x → lengthL (g x) ≡ c) →
  lengthL (concatMapL g xs) ≡ lengthL xs * c
length-concatMapL-const c g []       hyp = refl
length-concatMapL-const c g (x ∷ xs) hyp =
  trans (length-++ (g x) (concatMapL g xs))
        (cong₂ _ℕ+_ (hyp x) (length-concatMapL-const c g xs hyp))
