------------------------------------------------------------------------
-- Eliza.Prelude
--
-- Minimal type-theoretic prelude for the Eliza skeleton. Self-contained
-- (no agda-stdlib) so the skeleton type-checks with just `agda` on the
-- scratch/eliza/agda/ tree. Uses only Agda built-ins.
--
-- The skeleton's job is to express CONTRACTS, not implementations; most
-- numeric / continuous machinery (ℝ, log, divisions, etc.) shows up as
-- postulates in downstream modules. The constructive parts (Word, walk,
-- orbit, cocycle composition) are fully defined.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Eliza.Prelude where

------------------------------------------------------------------------
-- ℕ and order primitives.
------------------------------------------------------------------------

data ℕ : Set where
  zero : ℕ
  suc  : ℕ → ℕ

{-# BUILTIN NATURAL ℕ #-}

infixl 6 _+_
_+_ : ℕ → ℕ → ℕ
zero    + n = n
(suc m) + n = suc (m + n)

------------------------------------------------------------------------
-- Propositional equality.
------------------------------------------------------------------------

infix 4 _≡_
data _≡_ {A : Set} (x : A) : A → Set where
  refl : x ≡ x

cong : {A B : Set} {x y : A}
       (f : A → B) → x ≡ y → f x ≡ f y
cong f refl = refl

sym : {A : Set} {x y : A} → x ≡ y → y ≡ x
sym refl = refl

trans : {A : Set} {x y z : A} → x ≡ y → y ≡ z → x ≡ z
trans refl refl = refl

------------------------------------------------------------------------
-- Disjoint sum + product.
------------------------------------------------------------------------

infixr 4 _⊎_
data _⊎_ (A B : Set) : Set where
  inl : A → A ⊎ B
  inr : B → A ⊎ B

infixr 4 _,_
record _×_ (A B : Set) : Set where
  constructor _,_
  field
    fst : A
    snd : B
open _×_ public

------------------------------------------------------------------------
-- Booleans + Maybe.
------------------------------------------------------------------------

data Bool : Set where
  true false : Bool

data Maybe (A : Set) : Set where
  nothing : Maybe A
  just    : A → Maybe A

------------------------------------------------------------------------
-- The empty type, for absurd-pattern bridges where needed.
------------------------------------------------------------------------

data ⊥ : Set where
