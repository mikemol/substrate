------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Prime
--
-- Primality and prime factorisation, as the DIV-MOD WEDGE iterated.
--
-- Factorisation is not bespoke number theory: it is the substrate's keystone
-- wedge `a = recon q b r` (never-discard-residue) specialised and iterated.
-- `DivMod.Reconstruction.div-mod-eq : a ≡ (a mod-suc b) + (a div-suc b)*(suc b)`
-- IS that wedge; divisibility is the wedge with REMAINDER 0 (`mod0→∣`), the
-- quotient `a div-suc b` is the residue, and prime factorisation is the wedge
-- iterated by the least prime divisor — well-founded on the strictly-decreasing
-- quotient. This is the FTA-existence half = the surjectivity the Ω3-L-primes
-- ℤ-power codec needs (every positive ℚ is a product of prime powers).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Prime where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_; _≤_; _<_; s≤s; z≤n)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂; _×_)
open import Substrate.Foundation.List using (List; []; _∷_; foldr)
open import Substrate.Algebra.Nat.Divides.Type using (_∣_; divides)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_)
open import Substrate.Algebra.Nat.DivMod.DivSuc using (_div-suc_)
open import Substrate.Algebra.Nat.DivMod.Reconstruction using (div-mod-eq)

------------------------------------------------------------------------
-- 1. The wedge with remainder 0: a zero remainder IS divisibility, and the
--    quotient (the wedge residue) is the cofactor.
------------------------------------------------------------------------

mod0→∣ : (n d : ℕ) → n mod-suc d ≡ 0 → suc d ∣ n
mod0→∣ n d eq =
  divides (n div-suc d)
    (trans (div-mod-eq n d)
           (cong (λ r → r + (n div-suc d) * suc d) eq))

------------------------------------------------------------------------
-- 2. Primality + the factorisation structure (the surjectivity target).
------------------------------------------------------------------------

-- n is prime: n ≥ 2 and every divisor ≥ 2 is n itself.
IsPrime : ℕ → Set
IsPrime n = (2 ≤ n) × ((d : ℕ) → d ∣ n → 2 ≤ d → d ≡ n)

-- ∏ of a list of factors.
product : List ℕ → ℕ
product = foldr _*_ 1

-- every factor in the list is prime.
data AllPrime : List ℕ → Set where
  []  : AllPrime []
  _∷_ : ∀ {p ps} → IsPrime p → AllPrime ps → AllPrime (p ∷ ps)

-- a prime factorisation of n: a prime list whose product is n.
Factored : ℕ → Set
Factored n = Σ (List ℕ) (λ ps → AllPrime ps × (product ps ≡ n))

------------------------------------------------------------------------
-- 3. The bridge fires computationally: 2 ∣ 6 (6 mod 2 = 0 by refl).
--    (Non-vacuous witness that the wedge-with-r=0 reduces.)
------------------------------------------------------------------------

2∣6 : 2 ∣ 6
2∣6 = mod0→∣ 6 1 refl
