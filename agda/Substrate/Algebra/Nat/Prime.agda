------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Prime
--
-- Primality and the prime-factorisation STRUCTURE (definitions only; the
-- proofs — decidable divisibility, the least-divisor search, and the
-- factorisation EXISTENCE theorem — live in `Prime.Properties`, keeping this
-- data-exporting module's import closure proof-free, per the def/proof policy).
--
-- Factorisation is the substrate's keystone wedge `a = recon q b r`
-- (never-discard-residue) iterated: `DivMod.Reconstruction.div-mod-eq` is that
-- wedge, divisibility is the wedge with remainder 0, and prime factorisation is
-- the wedge iterated by least prime divisor. `Factored` is the surjectivity
-- target the Ω3-L-primes ℤ-power codec needs (every positive ℚ a product of
-- prime powers).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Prime where

open import Substrate.Foundation.Nat using (ℕ; _*_; _≤_)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Foundation.List using (List; []; _∷_; foldr)
open import Substrate.Algebra.Nat.Divides.Type using (_∣_)

-- n is prime: n ≥ 2 and every divisor ≥ 2 is n itself.
IsPrime : ℕ → Set
IsPrime n = (2 ≤ n) × ((d : ℕ) → d ∣ n → 2 ≤ d → d ≡ n)

-- ∏ of a list of factors.
product : List ℕ → ℕ
product = foldr _*_ 1

-- every factor in the list is prime.
data AllPrime : List ℕ → Set where
  []ᴾ  : AllPrime []
  _∷ᴾ_ : ∀ {p ps} → IsPrime p → AllPrime ps → AllPrime (p ∷ ps)

-- a prime factorisation of n: a prime list whose product is n.
Factored : ℕ → Set
Factored n = Σ (List ℕ) (λ ps → AllPrime ps × (product ps ≡ n))
