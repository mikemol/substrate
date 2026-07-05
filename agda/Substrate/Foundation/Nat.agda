------------------------------------------------------------------------
-- Substrate.Foundation.Nat
--
-- Substrate-native ℕ. Phase 2: native datatype + BUILTIN NATURAL.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat where

open import Substrate.Foundation.Eq using (_≡_; refl; cong; sym)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)

------------------------------------------------------------------------
-- The natural-number datatype + BUILTIN.
------------------------------------------------------------------------

data ℕ : Set where
  zero : ℕ
  suc  : ℕ → ℕ

{-# BUILTIN NATURAL ℕ #-}

------------------------------------------------------------------------
-- Arithmetic.
------------------------------------------------------------------------

infixl 6 _+_ _∸_
infixl 7 _*_
infixr 8 _^_

_+_ : ℕ → ℕ → ℕ
zero  + n = n
suc m + n = suc (m + n)

_*_ : ℕ → ℕ → ℕ
zero  * n = zero
suc m * n = n + (m * n)

_^_ : ℕ → ℕ → ℕ
m ^ zero  = suc zero
m ^ suc n = m * (m ^ n)

_∸_ : ℕ → ℕ → ℕ
m     ∸ zero  = m
zero  ∸ suc _ = zero
suc m ∸ suc n = m ∸ n

------------------------------------------------------------------------
-- Order: _≤_ and _<_ as inductive predicates.
------------------------------------------------------------------------

infix 4 _≤_ _<_

data _≤_ : ℕ → ℕ → Set where      -- ⟦shape:7ac77a03 z≤n,s≤s⟧
  z≤n : {n : ℕ}              → zero  ≤ n
  s≤s : {m n : ℕ} → m ≤ n → suc m ≤ suc n

_<_ : ℕ → ℕ → Set
m < n = suc m ≤ n

------------------------------------------------------------------------
-- Decidable equality + comparison.
------------------------------------------------------------------------

suc-injective : {m n : ℕ} → suc m ≡ suc n → m ≡ n
suc-injective refl = refl

_≟_ : (m n : ℕ) → Dec (m ≡ n)
zero  ≟ zero  = yes refl
zero  ≟ suc _ = no λ ()
suc _ ≟ zero  = no λ ()
suc m ≟ suc n with m ≟ n
... | yes p = yes (cong suc p)
... | no  q = no λ eq → q (suc-injective eq)

s≤s-injective : {m n : ℕ} → suc m ≤ suc n → m ≤ n
s≤s-injective (s≤s p) = p

_≤?_ : (m n : ℕ) → Dec (m ≤ n)
zero  ≤? _     = yes z≤n
suc _ ≤? zero  = no λ ()
suc m ≤? suc n with m ≤? n
... | yes p = yes (s≤s p)
... | no  q = no λ le → q (s≤s-injective le)

_<?_ : (m n : ℕ) → Dec (m < n)
m <? n = suc m ≤? n

------------------------------------------------------------------------
-- NonZero predicate (used by GCD / quotient arcs).
------------------------------------------------------------------------

data NonZero : ℕ → Set where
  nz-suc : ∀ {n} → NonZero (suc n)

instance
  nz : ∀ {n} → NonZero (suc n)
  nz = nz-suc
