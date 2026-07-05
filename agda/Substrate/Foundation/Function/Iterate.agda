------------------------------------------------------------------------
-- Substrate.Foundation.Function.Iterate
--
-- The generic nth-iterate of an endofunction, and its basic laws — a pure
-- Foundation combinator (nothing type-specific). `iterate k f = f ∘ ⋯ ∘ f`
-- (k times); `iterate-add` its additivity; `HasFixedOrder f k` the pointwise
-- fixed-order predicate (f^k = id) and its closure under positive multiples.
--
-- Ⓖ.iterate-to-foundation (2026-07-05): this WAS misfiled as the Fin-specialized
-- `σ-iterate`/`HasOrderPerm`/`σ-iterate-add`/`HasOrderPerm-multiple` under
-- Algebra.F2.Linear.FromImages.Permutation.Iterate — but nothing there is Fin-
-- or F2-specific; it is the nth-iterate of ANY endofunction. Relocated here to
-- its true home; that module is now a Fin-specialized re-export shim (the tower-
-- as-combinatorial-basis principle: a pure combinator belongs in the base). The
-- tower's Perm-power bridges to it via WitnessTower.CyclicCollapse.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Function.Iterate where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)

-- iterate k f = f ∘ f ∘ ⋯ ∘ f  (k times).
iterate : {A : Set} → ℕ → (A → A) → (A → A)
iterate zero    f = λ x → x
iterate (suc k) f = λ x → f (iterate k f x)

-- additivity of iteration in the count.
iterate-add : {A : Set} (f : A → A) (a b : ℕ) (x : A) →
              iterate (a + b) f x ≡ iterate a f (iterate b f x)
iterate-add f zero    b x = refl
iterate-add f (suc a) b x = cong f (iterate-add f a b x)

-- HasFixedOrder f k = ∀ x → iterate k f x ≡ x  (pointwise f^k = id).
HasFixedOrder : {A : Set} → (A → A) → ℕ → Set
HasFixedOrder f k = ∀ x → iterate k f x ≡ x

-- fixed order at any positive multiple.
HasFixedOrder-multiple : {A : Set} (f : A → A) (k m : ℕ) →
                         HasFixedOrder f k → HasFixedOrder f (m * k)
HasFixedOrder-multiple f k zero    ord x = refl
HasFixedOrder-multiple f k (suc m) ord x =
  trans (iterate-add f k (m * k) x)
  (trans (cong (iterate k f) (HasFixedOrder-multiple f k m ord x)) (ord x))
