------------------------------------------------------------------------
-- Substrate.Foundation.Fin
--
-- Substrate-native Fin. Phase 2: native indexed datatype + the
-- standard helpers (toℕ, fromℕ, _≟_, _<_, _≤_).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
  renaming (_<_ to _<ℕ_; _≤_ to _≤ℕ_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; sym)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)

------------------------------------------------------------------------
-- The Fin datatype.
------------------------------------------------------------------------

data Fin : ℕ → Set where
  zero : {n : ℕ} → Fin (suc n)
  suc  : {n : ℕ} → Fin n → Fin (suc n)

------------------------------------------------------------------------
-- toℕ / fromℕ.
------------------------------------------------------------------------

toℕ : {n : ℕ} → Fin n → ℕ
toℕ zero    = zero
toℕ (suc i) = suc (toℕ i)

fromℕ : (n : ℕ) → Fin (suc n)
fromℕ zero    = zero
fromℕ (suc n) = suc (fromℕ n)

fromℕ< : {m n : ℕ} → m <ℕ n → Fin n
fromℕ< {zero}  {suc _} _ = zero
fromℕ< {suc _} {suc _} (Substrate.Foundation.Nat.s≤s p) = suc (fromℕ< p)

------------------------------------------------------------------------
-- Decidable equality on Fin.
------------------------------------------------------------------------

suc-injective : {n : ℕ} {i j : Fin n} → (Fin.suc i) ≡ suc j → i ≡ j
suc-injective refl = refl

_≟_ : {n : ℕ} (i j : Fin n) → Dec (i ≡ j)
zero  ≟ zero  = yes refl
zero  ≟ suc _ = no λ ()
suc _ ≟ zero  = no λ ()
suc i ≟ suc j with i ≟ j
... | yes p = yes (cong suc p)
... | no  q = no λ eq → q (suc-injective eq)

------------------------------------------------------------------------
-- Order on Fin: lift from ℕ via toℕ.
------------------------------------------------------------------------

_<_ : {n : ℕ} → Fin n → Fin n → Set
i < j = toℕ i <ℕ toℕ j

_≤_ : {n : ℕ} → Fin n → Fin n → Set
i ≤ j = toℕ i ≤ℕ toℕ j
