------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Word.Length
--
-- Polymorphic word length ℕ+ length-distrib. The same functions
-- that FreeCyclic-Coxeter-Length provides specifically for F.Gen,
-- generalized over any generator type.
--
-- Used by: any F₂-graded structure that computes parity over word
-- lengths (V₄, all cyclic Coxeter instances, etc.).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Coxeter.Word.Length where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus

open import Substrate.Groups.Coxeter.Word
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong

------------------------------------------------------------------------
-- length — count of generators in a Word.
------------------------------------------------------------------------

length : ∀ {A} → Word A → ℕ
length []      = zero
length (_ ∷ w) = suc (length w)

------------------------------------------------------------------------
-- length-distrib — length is a monoid homomorphism over (ℕ, ℕ+, 0).
------------------------------------------------------------------------

length-distrib : ∀ {A} (a b : Word A) → length (a ++ b) ≡ length a ℕ+ length b
length-distrib []      b = refl
length-distrib (_ ∷ a) b = cong suc (length-distrib a b)
