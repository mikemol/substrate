------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Properties
--
-- Substrate-native properties of Fin: re-exports the decidable
-- equality + ordering, plus the toℕ ↔ fromℕ< roundtrip lemmas and
-- the toℕ bound. Built incrementally as downstream arcs (Cyclic
-- permutations, mod-suc-derived structures) need them.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Properties where

open import Substrate.Foundation.Nat
  using (ℕ; zero; suc; _<_; _≤_; s≤s; z≤n)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; sym; trans)
open import Substrate.Foundation.Fin public
  using (Fin; zero; suc; toℕ; fromℕ; fromℕ<; _≟_; _<_; _≤_; suc-injective)

------------------------------------------------------------------------
-- The toℕ-bound: every Fin n's underlying ℕ is strictly less than n.
------------------------------------------------------------------------

toℕ-bound : ∀ {n} (i : Fin n) → toℕ i Substrate.Foundation.Nat.< n
toℕ-bound zero    = s≤s z≤n
toℕ-bound (suc i) = s≤s (toℕ-bound i)

------------------------------------------------------------------------
-- toℕ ∘ fromℕ< roundtrip: converting m to Fin n via fromℕ< then back
-- via toℕ recovers m exactly.
------------------------------------------------------------------------

toℕ-fromℕ< : ∀ {m n} (p : m Substrate.Foundation.Nat.< n) →
             toℕ (fromℕ< p) ≡ m
toℕ-fromℕ< {zero}  {suc _} _       = refl
toℕ-fromℕ< {suc m} {suc _} (s≤s p) = cong suc (toℕ-fromℕ< p)

------------------------------------------------------------------------
-- toℕ-injective: equality of underlying ℕ implies equality of Fin.
--
-- The Fin n's `n` is fixed implicitly; this just identifies positions.
------------------------------------------------------------------------

toℕ-injective : ∀ {n} {i j : Fin n} → toℕ i ≡ toℕ j → i ≡ j
toℕ-injective {.(suc _)} {zero}  {zero}  _  = refl
toℕ-injective {.(suc _)} {suc i} {suc j} eq =
  cong suc (toℕ-injective (Substrate.Foundation.Nat.suc-injective eq))
