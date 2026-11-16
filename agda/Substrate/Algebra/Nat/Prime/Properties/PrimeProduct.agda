------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Prime.Properties.PrimeProduct
--
-- Defines: prime-∈-product
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Prime.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Prime.Properties.PrimeProduct where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Product
open import Substrate.Foundation.Sum.Sum
open import Substrate.Foundation.List
open import Substrate.Foundation.List.Any
open import Substrate.Foundation.WellFounded
open import Substrate.Foundation.Nat.Properties.Mul
open import Substrate.Foundation.Nat.Properties.Order
open import Substrate.Algebra.Nat.Divides.Type
open import Substrate.Algebra.Nat.DivMod.Unique.Private
open import Substrate.Algebra.Nat.WellFounded.LtWellFounded
open import Substrate.Algebra.Nat.WellFounded.Private
open import Substrate.Algebra.Nat.GCD.GcdPos.GcdPos
open import Substrate.Algebra.Nat.GCD.GcdDividesLeft
open import Substrate.Algebra.Nat.GCD.GcdDividesRight
open import Substrate.Algebra.Z.Euclid
open import Substrate.Algebra.Nat.Prime
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Nat.Prime.Properties.DividesToLe
open import Substrate.Algebra.Nat.Prime.Properties.Factorize
open import Substrate.Algebra.Nat.Prime.Properties.Factorize2
open import Substrate.Algebra.Nat.Prime.Properties.PrimeDividesProduct
open import Substrate.Algebra.Nat.Prime.Properties.PrimeDividesprimeToEq



-- THE CAPSTONE: a prime dividing a product of primes IS one of them. By
-- induction on the prime list using `prime-divides-product` at each step; the
-- empty case is impossible (a prime ≥2 cannot divide the empty product 1).
-- Combined with existence (factorize!), this forces the prime multiset — FTA
-- uniqueness in the form the codec needs (the "log" is well-defined).
prime-∈-product : ∀ {p qs} → IsPrime p → AllPrime qs → p ∣ product qs → p ∈ qs
prime-∈-product {p} {[]}       pp []ᴾ          p∣1
  with ≤-trans (proj₁ pp) (∣→≤ p zero p∣1)
... | (s≤s ())
prime-∈-product {p} {q ∷ rest} pp (qp ∷ᴾ restp) p∣qr
  with prime-divides-product pp q (product rest) p∣qr
... | inj₁ p∣q    = here (prime∣prime→≡ pp qp p∣q)
... | inj₂ p∣rest = there (prime-∈-product pp restp p∣rest)
