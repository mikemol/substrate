{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Foundation.Iff — logical equivalence of types.
--
-- ⟡rc-het-iff (⟡set1-rerank2): a proof that two TYPES are propositionally
-- EQUAL (`A ≡ B` with A B : Set) intrinsically inhabits Set₁ (since
-- `_≡_ {Set}` lands in Set₁). Where the two sides are only ever used up
-- to a round-trip — never transported along — the honest statement is
-- logical equivalence `A ⇔ B = (A → B) × (B → A)`, which lives in Set₀.
-- Every ex-`≡`-of-Sets in the substrate was a `refl` (the sides were
-- definitionally equal), so each converts by `⇔-refl`.
------------------------------------------------------------------------

module Substrate.Foundation.Iff where

open import Substrate.Foundation.Product using (_×_; _,_)

infix 3 _⇔_

_⇔_ : Set → Set → Set
A ⇔ B = (A → B) × (B → A)

-- reflexivity: identity in both directions (the ex-`refl` witness).
⇔-refl : {A : Set} → A ⇔ A
⇔-refl = (λ x → x) , (λ x → x)
