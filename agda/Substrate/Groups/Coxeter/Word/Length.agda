------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Word.Length
--
-- Polymorphic word length + length-distrib. The same functions
-- that FreeCyclic-Coxeter-Length provides specifically for F.Gen,
-- generalized over any generator type.
--
-- Used by: any F₂-graded structure that computes parity over word
-- lengths (V₄, all cyclic Coxeter instances, etc.).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Coxeter.Word.Length where

open import Data.Nat using (ℕ; zero; suc; _+_)
open import Relation.Binary.PropositionalEquality using (_≡_; refl; cong)

open import Substrate.Groups.Coxeter.Word

------------------------------------------------------------------------
-- length — count of generators in a Word.
------------------------------------------------------------------------

length : ∀ {A} → Word A → ℕ
length []      = zero
length (_ ∷ w) = suc (length w)

------------------------------------------------------------------------
-- length-distrib — length is a monoid homomorphism over (ℕ, +, 0).
------------------------------------------------------------------------

length-distrib : ∀ {A} (a b : Word A) → length (a ++ b) ≡ length a + length b
length-distrib []      b = refl
length-distrib (_ ∷ a) b = cong suc (length-distrib a b)
