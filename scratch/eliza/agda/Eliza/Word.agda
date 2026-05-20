------------------------------------------------------------------------
-- Eliza.Word
--
-- The universal cons-list `Word α`, the substrate's standard structural
-- representation of sequences over an alphabet. Mirrors
-- `Substrate.Groups.Coxeter.Word` from the canonical agda/ tree.
--
-- Every layer of the eliza pipeline expresses its data as a `Word α` for
-- an appropriate α:
--   * Word Char    — raw input stream.
--   * Word Gen     — generator emissions after routing.
--   * Word Chamber — chamber trajectory after walking.
--   * Word Orbit   — orbit trajectory after V₄-quotient.
--   * Word (T ⊎ NT) — Sequitur rule right-hand side.
--
-- Keeping the spine identical at every layer is the structural move that
-- lets the same combinators (++, map, length, etc.) instrument all
-- layers uniformly.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Eliza.Word where

open import Eliza.Prelude using (ℕ; zero; suc; _≡_; refl; _+_; cong)

------------------------------------------------------------------------
-- 1. The Word type.
------------------------------------------------------------------------

infixr 5 _∷_

data Word (α : Set) : Set where
  []  : Word α
  _∷_ : α → Word α → Word α

------------------------------------------------------------------------
-- 2. Concatenation.
------------------------------------------------------------------------

infixr 5 _++_

_++_ : {α : Set} → Word α → Word α → Word α
[]       ++ ys = ys
(x ∷ xs) ++ ys = x ∷ (xs ++ ys)

------------------------------------------------------------------------
-- 3. Length, map, foldr — the standard list combinators that downstream
-- modules use without re-deriving each time.
------------------------------------------------------------------------

length : {α : Set} → Word α → ℕ
length []       = zero
length (_ ∷ xs) = suc (length xs)

map : {α β : Set} → (α → β) → Word α → Word β
map f []       = []
map f (x ∷ xs) = f x ∷ map f xs

foldr : {α β : Set} → (α → β → β) → β → Word α → β
foldr f e []       = e
foldr f e (x ∷ xs) = f x (foldr f e xs)

------------------------------------------------------------------------
-- 4. Associativity of ++ — the one property the Coxeter/Sequitur
-- machinery uses constructively.
------------------------------------------------------------------------

++-assoc : (α : Set) (a b c : Word α) →
           (a ++ b) ++ c ≡ a ++ (b ++ c)
++-assoc α []      b c = refl
++-assoc α (x ∷ a) b c = cong (x ∷_) (++-assoc α a b c)
