------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Word.Count
--
-- Polymorphic generator-weighted count over Words. Sibling of
-- Coxeter.Word.Length: where `length` is the special case where every
-- generator contributes 1, `count-by sel` weights each generator by
-- `sel g`.
--
-- Per [[expose-generator-not-orbit]]: the orbit was Word-Count-A vs
-- Word-Count-B vs length, each hand-rolled with its own distributivity
-- proof. This module IS the generator-weighted count ℕ+ its monoid
-- homomorphism property, derived once and parametric in the selector.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Coxeter.Word.Count where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc

open import Substrate.Groups.Coxeter.Word
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Algebra.Wedge.BinMul.Sel

------------------------------------------------------------------------
-- count-by sel w = Σ_{g in w} sel g.
--
-- Specialisations:
--   length         = count-by (λ _ → 1)
--   count-A        = count-by (λ { A → 1 ; B → 0 })
--   count-B        = count-by (λ { A → 0 ; B → 1 })
------------------------------------------------------------------------

count-by : ∀ {A} (sel : A → ℕ) → Word A → ℕ
count-by sel []      = zero
count-by sel (g ∷ w) = sel g ℕ+ count-by sel w

------------------------------------------------------------------------
-- count-by is a monoid homomorphism (Word A, ++, []) → (ℕ, ℕ+, 0).
------------------------------------------------------------------------

count-by-distrib : ∀ {A} (sel : A → ℕ) (a b : Word A) →
                   count-by sel (a ++ b) ≡ count-by sel a ℕ+ count-by sel b
count-by-distrib sel []      b = refl
count-by-distrib sel (g ∷ a) b =
  trans (cong (sel g ℕ+_) (count-by-distrib sel a b))
        (sym (+ℕ-assoc (sel g) (count-by sel a) (count-by sel b)))

count-by-[] : ∀ {A} (sel : A → ℕ) → count-by sel [] ≡ zero
count-by-[] _ = refl
